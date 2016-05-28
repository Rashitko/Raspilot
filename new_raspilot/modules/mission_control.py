import json

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import connectionDone, ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

from new_raspilot.core.commands.command import BaseCommand
from new_raspilot.core.providers.mission_control_provider import BaseMissionControlProvider
from new_raspilot.core.utils.raspilot_logger import RaspilotLogger


class RaspilotMissionControlProvider(BaseMissionControlProvider):
    def _execute_initialization(self):
        self.__protocol = FlightProtocol(self)

    def _execute_start(self):
        endpoint = TCP4ClientEndpoint(reactor, 'raspilot.projekty.ms.mff.cuni.cz', 3003)
        endpoint.connect(FlightProtocolFactory(self.__protocol))
        return True

    def _execute_stop(self):
        pass

    def send_message(self, data):
        if self.__protocol.transport:
            reactor.callFromThread(self.__protocol.sendLine, data)

    def execute_command(self, command):
        self.raspilot.command_receiver.execute_command(command)

    def on_connection_opened(self, address):
        self.logger.debug("Connected to Flight Control on address {}".format(address))

    def on_connection_lost(self):
        self.logger.error("Connection with Flight Control lost")


class FlightProtocol(LineReceiver):
    def __init__(self, callbacks):
        super().__init__()
        self.delimiter = bytes('\n', 'utf-8')
        self.__callbacks = callbacks

    def lineReceived(self, line):
        try:
            parsed_data = json.loads(line.decode('utf-8'))
            self.__callbacks.execute_command(BaseCommand.from_json(parsed_data))
        except json.JSONDecodeError as e:
            self.__logger.error("Invalid data received.\n\tData were {}.\n\tException risen is {}".format(line, e))
        except Exception as e:
            self.__logger.critical(
                "Exception occurred during data processing.\n\tData were {}.\n\tException risen is {}".format(line, e))

    def rawDataReceived(self, data):
        pass

    def connectionMade(self):
        self.__callbacks.on_connection_opened(self.transport.addr[0])

    def connectionLost(self, reason=connectionDone):
        self.__callbacks.on_connection_lost()


class FlightProtocolFactory(ReconnectingClientFactory):
    def __init__(self, protocol):
        super().__init__()
        self.__logger = RaspilotLogger.get_logger()
        self.__protocol = protocol

    def clientConnectionFailed(self, connector, reason):
        self.__logger.debug("Connection failed")
        super().clientConnectionFailed(connector, reason)

    def clientConnectionLost(self, connector, unused_reason):
        self.__logger.debug("clientConnectionLost")
        super().clientConnectionLost(connector, unused_reason)

    def startedConnecting(self, connector):
        self.__logger.debug("startedConnecting")
        super().startedConnecting(connector)

    def buildProtocol(self, addr):
        return self.__protocol
