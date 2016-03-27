import json
import logging

from twisted.internet import reactor
from twisted.internet.protocol import connectionDone, ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

from raspilot.providers.base_provider import BaseProviderConfig
from raspilot.providers.flight_control_provider import FlightControlProvider

CHANNEL_NAME_FORMAT = "device:{}"


class RaspilotFlightControlProvider(FlightControlProvider):
    """
    Implementation of the abstract WebsocketsProvider.
    """

    def __init__(self, websockets_config):
        """
        Constructs a new 'RaspilotWebsocketsProvider' which is initialized from data in the configuration.
        :param websockets_config: configuration to read initialization data from
        :return: returns nothing
        """
        super().__init__(websockets_config)
        self.__logger = logging.getLogger('raspilot.log')
        self.__server_address = websockets_config.server_address
        self.__port = websockets_config.port
        self.__protocol = RaspilotFlightControlProtocol()

    def stop(self):
        # noinspection PyUnresolvedReferences
        reactor.callFromThread(reactor.stop)
        return True

    def start(self):
        """
        Connects and waits for the success of failure.
        :return: True, if connection is successful, False otherwise
        """
        # noinspection PyUnresolvedReferences
        reactor.connectTCP(self.__server_address, self.__port, RaspilotFlightControlClientFactory(self.__protocol))
        return True

    def send_telemetry_update_message(self, message, success=None, failure=None):
        """
        Sends a raw message via the websocket. If the transmission fails failure callback is executed (if set).
        If the transmission is successful the success callback is executed (if set). It is not verified that someone
        receives the message, only transmission success is reported. Callbacks should have one parameter - message.
        :param message: message to be sent
        :param success: success callback
        :param failure: failure callback
        :return: True if transmission is successful, False otherwise.
        """
        return self.__protocol.send_message(self.__serialize_message(message))

    def send_message(self, message, success=None, failure=None):
        return self.__protocol.send_message(self.__serialize_message(message))

    @staticmethod
    def __serialize_message(message):
        json_data = json.dumps(message)
        json_data += '\n'
        return bytes(json_data.encode('utf-8'))


class RaspilotFlightControlProtocol(LineReceiver):
    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger('raspilot.log')

    def connectionMade(self):
        super().connectionMade()
        self.__logger.debug('FlightControl connection successful')

    def connectionLost(self, reason=connectionDone):
        super().connectionLost(reason)
        self.__logger.debug('FlightControl connection lost')

    def send_message(self, data):
        if self.connected:
            reactor.callFromThread(self.sendLine, data)
            return True
        else:
            return False


class RaspilotFlightControlClientFactory(ReconnectingClientFactory):
    def __init__(self, protocol):
        super().__init__()
        self.__logger = logging.getLogger('raspilot.log')
        self.__protocol = protocol

    def buildProtocol(self, addr):
        self.__logger.debug('Connected')
        self.resetDelay()
        return self.__protocol

    def clientConnectionLost(self, connector, reason):
        self.__logger.error('Lost connection.  Reason:{}'.format(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        self.__logger.error('Connection failed. Reason:{}'.format(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)


class RaspilotFlightControlConfig(BaseProviderConfig):
    """
    Used to initialize the RaspilotWebsocketsProvider. All subclasses of the RaspilotWebsocketsProvider which has their
    own config should extend this class.
    """

    def __init__(self, server_address, port):
        """
        Constructs a new 'RaspilotWebsocketsConfig' which is used to initialize the RaspilotWebsocketsProvider.
        :param raspilot_config: configuration used to read data from
        :return: returns nothing
        """
        super().__init__()
        self.__server_address = server_address
        self.__port = port

    @property
    def server_address(self):
        return self.__server_address

    @server_address.setter
    def server_address(self, value):
        self.__server_address = value

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, value):
        self.__port = value
