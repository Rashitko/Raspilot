import socket
import logging
from threading import Thread

from raspilot.raspilot import Raspilot, RaspilotBuilder


class RaspilotImpl(Raspilot):

    def __init__(self, raspilot_builder):
        super().__init__(raspilot_builder)
        self.__discovery_port = raspilot_builder.discovery_port
        self.__reply_port = raspilot_builder.reply_port
        self.__discovery_thread = None

    def __discovery(self):
        """
        Listens for discovery messages and announce IP address which can be used to connect to the raspilot service
        :param discovery_port port to listen for messages
        :param reply_port port to reply to with the discovery message
        :return: returns nothing
        """
        logger = logging.getLogger('raspilot.log')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', self.__discovery_port))
        logger.info("Waiting for discovery request...")
        (_, address) = s.recvfrom(1024)
        logger.info("connection from address {}".format(address))
        my_address = socket.gethostbyname(socket.gethostname()).encode('utf-8')
        reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        reply_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        logger.info('Replying to {}'.format(address[0]))
        reply_socket.sendto(bytes(my_address), (address[0], self.__reply_port))
        reply_socket.close()
        s.close()

    def enable_discovery(self):
        if not self.__discovery_thread:
            self.__discovery_thread = Thread(target=self.__discovery, name="RASPILOT_DISCOVERY")
            self.__discovery_thread.start()


class RaspilotImplBuilder(RaspilotBuilder):

    def __init__(self, discovery_port, reply_port):
        super().__init__()
        self.__discovery_port = discovery_port
        self.__reply_port = reply_port

    @property
    def discovery_port(self):
        return self.__discovery_port

    @discovery_port.setter
    def discovery_port(self, value):
        self.__discovery_port = value

    @property
    def reply_port(self):
        return self.__reply_port

    @reply_port.setter
    def reply_port(self, value):
        self.__reply_port = value

    def build(self):
        return RaspilotImpl(self)
