import struct

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

from new_raspilot.raspilot_framework.providers.orientation_provider import OrientationProvider
from new_raspilot.raspilot_framework.utils.raspilot_logger import RaspilotLogger


class ROrientationProvider(OrientationProvider):
    def __init__(self):
        super().__init__()

    def _execute_initialization(self):
        self.__protocol = OrientationProtocol(self)

    def _execute_start(self):
        endpoint = TCP4ServerEndpoint(reactor, 50000)
        endpoint.listen(OrientationProtocolFactory(self.__protocol))
        return True

    def _execute_stop(self):
        pass

    def current_orientation(self):
        pass


class OrientationProtocol(LineReceiver):
    def __init__(self, callbacks):
        self.__logger = RaspilotLogger.get_logger()
        self.delimiter = bytes('\n', 'utf-8')
        self__callbacks = callbacks

    def rawDataReceived(self, data):
        self.__logger.debug("Raw data received {}".format(data))

    def lineReceived(self, line):
        (f,) = struct.unpack("!f", line)
        self.__logger.debug("Data received {}".format(f))


class OrientationProtocolFactory(Factory):
    def __init__(self, protocol):
        self.__protocol = protocol

    def buildProtocol(self, addr):
        return self.__protocol
