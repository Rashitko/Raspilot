import json

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory, connectionDone
from twisted.protocols.basic import LineReceiver

from new_raspilot.raspilot_framework.base_started_module import BaseStartedModule
from new_raspilot.raspilot_framework.commands.command import Command
from new_raspilot.raspilot_framework.utils.raspilot_logger import RaspilotLogger


class AndroidProvider(BaseStartedModule):
    def __init__(self):
        super().__init__()

    def _execute_initialization(self):
        self.__protocol = AndroidProtocol(self.raspilot.command_receiver)

    def _execute_start(self):
        endpoint = TCP4ServerEndpoint(reactor, 50001)
        endpoint.listen(AndroidProtocolFactory(self.__protocol))
        return True

    def _execute_stop(self):
        pass

    def send_data(self, data):
        if self.__protocol.transport:
            reactor.callFromThread(self.__protocol.sendLine, data)


class AndroidProtocol(LineReceiver):
    def __init__(self, callbacks):
        super().__init__()
        self.delimiter = bytes([0, 10])
        self.__logger = RaspilotLogger.get_logger()
        self.__callbacks = callbacks

    def rawDataReceived(self, data):
        self.__logger.debug("Raw data received {}".format(data))

    def lineReceived(self, line):
        self.__logger.debug("Data received {}".format(line))
        try:
            parsed_data = json.loads(line.decode('utf-8'))
            self.__callbacks.execute_command(Command.from_json(parsed_data))
        except json.JSONDecodeError as e:
            self.__logger.error("Invalid data received.\n\tData were {}.\n\tException risen is {}".format(line, e))
        except Exception as e:
            self.__logger.critical(
                "Exception occurred during data processing.\n\tData were {}.\n\tException risen is {}".format(line, e))

    def connectionMade(self):
        self.__logger.info("Connection from {} opened".format(self.transport.client[0]))

    def connectionLost(self, reason=connectionDone):
        self.__logger.info("Connection lost")


class AndroidProtocolFactory(Factory):

    def __init__(self, protocol):
        super().__init__()
        self.__protocol = protocol

    def buildProtocol(self, addr):
        return self.__protocol
