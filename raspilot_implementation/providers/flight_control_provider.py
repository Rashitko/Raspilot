import logging
from threading import Thread

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, connectionDone, ReconnectingClientFactory

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
        self.__server_address = websockets_config.server_address
        self.__port = websockets_config.port

    def stop(self):
        reactor.callFromThread(reactor.stop)
        return True

    def start(self):
        """
        Connects and waits for the success of failure.
        :return: True, if connection is successful, False otherwise
        """
        f = RaspilotFlightControlClientFactory()
        reactor.connectTCP(self.__server_address, self.__port, f)
        return True

    @staticmethod
    def __start_reactor():
        reactor.run(installSignalHandlers=False)

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
        super().send_telemetry_update_message(message)
        return True

    def send_message(self, message, success=None, failure=None):
        super().send_message(message)


class RaspilotFlightControlProtocol(Protocol):
    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger('raspilot.log')

    def connectionMade(self):
        super().connectionMade()
        self.__logger.debug('FlightControl connection successful')

    def connectionLost(self, reason=connectionDone):
        super().connectionLost(reason)
        self.__logger.debug('FlightControl connection lost')


class RaspilotFlightControlClientFactory(ReconnectingClientFactory):
    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger('raspilot.log')

    def buildProtocol(self, addr):
        self.__logger.debug('Connected')
        return RaspilotFlightControlProtocol()


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
