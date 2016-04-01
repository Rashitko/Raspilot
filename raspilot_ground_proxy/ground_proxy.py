import datetime
import json
import logging
import os
import sys

from colorlog import ColoredFormatter
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, connectionDone, ReconnectingClientFactory

GROUND_PORT = 3004

FLIGHT_PORT = 3003

LOGGER_NAME = 'raspilot_proxy.log'
date_format = "%Y-%m-%d %H:%M:%S"


class ProxyProtocol(Protocol):
    """
    Simple protocol which sends the received data to the output socket.
    """

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__output = None

    def dataReceived(self, data):
        """
        Sends the received data to the output, if output is connected
        :param data: received data
        :return: returns nothing
        """
        super().dataReceived(data)
        if self.__output.transport:
            self.__output.transport.write(data)

    def connectionLost(self, reason=connectionDone):
        """
        Sends message to the output, if output is connected
        :param reason: not used
        :return: returns nothing
        """
        super().connectionLost(reason)
        self.__logger.info('Connection from {} lost. Reason {}'.format(self.output_address, reason))
        if self.__output.transport:
            self.__output.transport.write(self.__create_connection_state_message(False))

    def connectionMade(self):
        """
        Sends message to the output, if output is connected
        :return: returns nothing
        """
        super().connectionMade()
        self.__logger.info('New connection from {}'.format(self.output_address))
        if self.__output.transport:
            self.__output.transport.write(self.__create_connection_state_message(True))

    def __create_connection_state_message(self, connected):
        """
        Creates message which is sent when connection state of the output changes.
        :param connected: True if output is connected False otherwise
        :return: returns newly created message as bytes
        """
        data = {'name': 'connection_state_changed', 'connected': connected, 'address': self.output_address}
        return bytes(json.dumps(data).encode('utf-8'))

    @property
    def output_address(self):
        return self.transport.client[0]

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = value


class ProxyFactory(ReconnectingClientFactory):
    def __init__(self, protocol):
        super().__init__()
        self.__protocol = protocol

    def buildProtocol(self, addr):
        return self.__protocol


def init_logger(level, logs_path):
    """
    Initializes the Raspilot logger.
    :param level: logging level of the created logger
    :return: returns nothing
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)
    fh = logging.FileHandler("{}raspilot_proxy-{}.log".format(logs_path, datetime.datetime.now().strftime("%Y-%m-%d")))
    fh.setLevel(level)
    message_format = '%(log_color)s[%(levelname)s] %(asctime)s%(reset)s\n\t''%(message)s\n\t''[FILE]%(pathname)s:%(lineno)s\n\t''[THREAD]%(threadName)s'
    formatter = ColoredFormatter(message_format, date_format)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False


if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    pids_dir = os.path.join(dir, '../tmp')
    current_dir = os.path.dirname(__file__)
    log_dir = os.path.join(current_dir, '../logs/')
    init_logger('DEBUG', log_dir)

    logger = logging.getLogger(LOGGER_NAME)
    logger.info('Starting Raspilot Proxy. Listening on ports {} and {}'.format(FLIGHT_PORT, GROUND_PORT))

    flight_protocol = ProxyProtocol()
    ground_protocol = ProxyProtocol()
    flight_protocol.output = ground_protocol
    ground_protocol.output = flight_protocol

    flight_point = TCP4ServerEndpoint(reactor, FLIGHT_PORT)
    flight_factory = ProxyFactory(flight_protocol)
    flight_point.listen(flight_factory)
    ground_point = TCP4ServerEndpoint(reactor, GROUND_PORT)
    ground_factory = ProxyFactory(ground_protocol)
    ground_point.listen(ground_factory)
    reactor.run()

    logger.info('Raspilot Proxy exiting')
