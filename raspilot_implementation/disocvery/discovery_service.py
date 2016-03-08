import logging
import socket
from threading import Thread


class DiscoveryService:
    """
    Classed used in the discovery stage by the Android device.
    """

    def __init__(self, discovery_port, reply_port):
        self.__discovery_port = discovery_port
        self.__reply_port = reply_port
        self.__discovery_thread = None
        self.__logger = logging.getLogger('raspilot.log')
        self.__discovery_enabled = True
        self.__discovery_socket = None

    def __discovery(self):
        """
        Listens for discovery messages and announce IP address which can be used to connect to the raspilot service
        :return: returns nothing
        """
        self.__discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__discovery_socket.bind(('', self.__discovery_port))
        try:
            while self.__discovery_enabled:
                self.__logger.info("Waiting for discovery request...")
                (_, address) = self.__discovery_socket.recvfrom(1024)
                self.__logger.info("connection from address {}".format(address))
                my_address = socket.gethostbyname(socket.gethostname()).encode('utf-8')
                reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                reply_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self.__logger.info('Replying to {}'.format(address[0]))
                reply_socket.sendto(bytes(my_address), (address[0], self.__reply_port))
                reply_socket.close()
        except OSError:
            pass
        self.__logger.debug('Discovery shut down')

    def enable_discovery(self):
        """
        Creates and starts the discovery service, if the discovery thread is not running already
        :return:
        """
        if not self.__discovery_thread:
            self.__discovery_thread = Thread(target=self.__discovery, name="RASPILOT_DISCOVERY")
            self.__discovery_thread.start()

    def disable_discovery(self):
        """
        If the discovery socket is available closes the socket, sets the discovery thread to None and disables the discovery flag
        :return:
        """
        self.__discovery_enabled = False
        if self.__discovery_socket:
            self.__discovery_socket.close()
            self.__discovery_socket = None
        self.__discovery_thread = None
