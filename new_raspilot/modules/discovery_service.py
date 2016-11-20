import socket

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

from new_raspilot.core.base_started_module import BaseStartedModule
from new_raspilot.core.utils.raspilot_logger import RaspilotLogger


class DiscoveryService(BaseStartedModule):
    DISCOVERY_PORT = 3001

    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)

    def _execute_start(self):
        reactor.listenUDP(DiscoveryService.DISCOVERY_PORT, DiscoveryProtocol())
        RaspilotLogger.get_logger().debug("Listening for Discovery Requests")
        return True

    def load(self):
        return True


class DiscoveryProtocol(DatagramProtocol):
    def __init__(self):
        super().__init__()
        self.__logger = RaspilotLogger.get_logger()

    def datagramReceived(self, datagram, addr):
        super().datagramReceived(datagram, addr)
        my_address = socket.gethostbyname(socket.gethostname())
        self.__logger.debug("Discovery request from {}".format(addr[0]))
        self.transport.write(bytes(my_address, 'utf-8'), addr)
