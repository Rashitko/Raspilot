import logging
from threading import Event

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory, connectionDone

import raspilot.providers.base_provider

DEFAULT_RECV_SIZE = 1024


class StreamSocketProvider(raspilot.providers.base_provider.BaseProvider):
    def __init__(self, port, recv_size=DEFAULT_RECV_SIZE, name=None):
        super().__init__(None, name)
        self.__logger = logging.getLogger('raspilot.log')
        self.__protocol = RaspilotBaseProtocol(self)
        self.__factory = RaspilotBaseFactory(self.__protocol)
        self.__recv_size = recv_size
        self.__port = port
        self.__client_connected_event = Event()
        self.__address = None
        self.__endpoint = None
        reactor.callFromThread(self.__setup_endpoint)

    def __setup_endpoint(self):
        self.__endpoint = TCP4ServerEndpoint(reactor, self.__port)
        self.__endpoint.listen(self.__factory)

    def start(self):
        super().start()
        return True

    def on_data_received(self, data):
        """
        Catches all Exceptions during the data processing and rises a DataProcessingError instead.
        :param data: received data
        :return: returns nothing
        """
        try:
            self._handle_data(data)
        except Exception as e:
            message = "Error during data processing. Error was {}".format(e)
            self.__logger.error(message)
            raise DataProcessingError(message)

    def _handle_data(self, data):
        """
        Processes the received data.
        :param data: received data
        :return: returns nothing
        """
        pass

    def on_client_connected(self, address):
        """
        Called when a client connects. Client connected event is set, so RaspilotOrientationProvider.wait_for_client()
        is no longer blocked.
        :param address: client address
        :return: returns nothing
        """
        self.__address = address
        self.__client_connected_event.set()

    def on_client_connection_lost(self, reason):
        """
        Called when a client connection is lost.
        :param reason: reason why the connection was lost
        :return: returns nothing
        """
        self.__address = None
        pass

    def send(self, message):
        """
        Adds the message to the queue, from which it will be sent when the connection to the client will be available.
        :param message: message to be sent
        :return: returns nothing
        """
        return self.__protocol.send_message(self._serialize_message(message))

    def _serialize_message(self, message):
        """
        Subclasses must override. Serializes the message as a bytes array.
        :param message: message to be serialized
        :return: serialized message as a bytes array
        """
        return bytes(message)

    def wait_for_client(self):
        """
        Returns when a new client is connected.
        :return: returns nothing
        """
        self.__client_connected_event.wait()
        return None

    def stop(self):
        super().stop()
        return True

    @property
    def connected(self):
        return self.__protocol.transport.connected


class RaspilotBaseProtocol(Protocol):
    def __init__(self, callbacks, suppress_data_discard_logs=False):
        """
        Creates new 'RaspilotBaseProtocol'. The provided callbacks object must have following methods implemented:
            on_client_connected(address),
            on_client_connection_lost(reason),
            on_data_received(data).
        :param callbacks: callbacks object, can be None.
        :param suppress_data_discard_logs: set to True, if callbacks are null and you don't want to log the warnings
        about discarding received data
        :return: returns nothing
        """
        self.__logger = logging.getLogger('raspilot.log')
        self.__callbacks = callbacks
        self.__suppress_data_discard_logs = suppress_data_discard_logs

    def connectionLost(self, reason=connectionDone):
        """
        Called after the client connection is lost. If callbacks are set, callbacks.on_client_connection_lost(reason) is
        called.
        :param reason: reason why the connection was lost
        :return: returns nothing
        """
        super().connectionLost(reason)
        self.logger.debug("Connection lost. Reason was {}".format(reason))
        if self.__callbacks:
            self.__callbacks.on_client_connection_lost(reason)

    def connectionMade(self):
        """
        Called after the client connects. If callbacks are set, callbacks.on_connection_made(address) is called.
        :return: returns nothing
        """
        super().connectionMade()
        self.logger.debug("{} connection successful".format(self.__callbacks.__class__.__name__))
        if self.__callbacks:
            self.__callbacks.on_client_connected(self.transport.client[0])

    def dataReceived(self, data):
        """
        Called upon receiving the data. If callbacks are set, callbacks.on_data_received(data) is called.
        :param data: data received
        :return: returns nothing
        """
        super().dataReceived(data)
        if self.__callbacks:
            self.__callbacks.on_data_received(data)
        elif not self.__suppress_data_discard_logs:
            self.logger.warning("{} callbacks is None, discarding received data".format(self.__callbacks.__class__.__name__))

    def send_message(self, message):
        """
        Sends the message if connected.
        :param message: message to be sent
        :return: True if message was sent, False otherwise
        """
        if self.connected:
            reactor.callFromThread(self.transport.write, message)
            return True
        return False

    @property
    def logger(self):
        return self.__logger


class RaspilotBaseFactory(Factory):
    def __init__(self, protocol):
        self.__protocol = protocol

    def buildProtocol(self, addr):
        return self.__protocol


class DataProcessingError(Exception):
    """
    Error thrown when processing error. Throwing this error result in ignoring the received data.
    """
    pass


class DataTransmissionError(Exception):
    """
    Error thrown when transmitting data.
    """
    pass
