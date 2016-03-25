import logging
import socket
from queue import Queue, Full
from threading import RLock, Thread, Event

import raspilot.providers.base_provider

HOST = ''
MAX_CONNECTIONS = 1
RECV_BYTES = 1024


class SocketProvider(raspilot.providers.base_provider.BaseProvider):
    @staticmethod
    def __create_socket(port):
        """
        Creates and bind a socket to the specified port
        :param port: port to bind to
        :return: created socket which is bound to the specified port
        """
        logger = logging.getLogger('raspilot.log')
        logger.debug('Opening socket on {}:{}'.format(HOST, port))
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, port))
        return s

    def __init__(self, port, recv_size, name=None):
        raspilot.providers.base_provider.BaseProvider.__init__(self, None, name)
        self.__logger = logging.getLogger('raspilot.log')
        self.__port = port
        self.__recv_size = recv_size
        self.__socket = None
        self.__data_process_lock = RLock()
        self.__run = True
        self.__client_address = None
        self.__socket_listening_event = Event()
        self.__client_available_event = Event()
        self.__queue = Queue()
        self.__recv_lock = RLock()

    def start(self):
        super().start()
        # noinspection PyBroadException
        try:
            self.__socket = self.__create_socket(self.__port)
            Thread(target=self._process, name="SOCKET_PROVIDER_IN_{}".format(self.__class__.__name__)).start()
            Thread(target=self._send_loop, name="SOCKET_PROVIDER_OUT_{}".format(self.__class__.__name__)).start()
            self.__socket_listening_event.wait()
            return True
        except Exception as e:
            self.__logger.error("An error occurred during socket provider start. {}".format(e))
            return False

    def _process(self):
        """
        Opens the socket and receives data until SocketProvider.stop() is called.
        :return: returns nothing
        """
        self.__socket_listening_event.set()
        while self.__run:
            try:
                with self.__data_process_lock:
                    (data, address) = self.__socket.recvfrom(1024)
                    if not data:
                        break
                    if address:
                        self.client_address = address[0]
                        if not self.__client_available_event.is_set():
                            self.__client_available_event.set()
                    self.__handle_data(data)
            except DataProcessingError:
                self.__logger.warning("Wrong data received, ignoring them")
            except OSError:
                pass
        self.__socket.close()
        self.__logger.debug("Process loop of {} exiting".format(self.__class__.__name__))

    def __handle_data(self, data):
        """
        Catches all Exceptions during the data processing and rises a DataProcessingError instead.
        :param data: received data
        :return: returns nothing
        """
        try:
            self._on_data_received(data)
        except Exception as e:
            message = "Error during data processing. Error was {}".format(e)
            self.__logger.error(message)
            raise DataProcessingError(message)

    def _on_data_received(self, data):
        """
        Processes the received data.
        :param data: received data
        :return: returns nothing
        """
        pass

    def _send_loop(self):
        self.__client_available_event.wait()
        while self.__run:
            data = self.__queue.get()
            if data:
                self.__logger.log(9,
                                  'Sending data to Android device on {}:{}'.format(self.__client_address, self.__port))
                self.__socket.sendto(data, (self.__client_address, self.__port))
            self.__queue.task_done()
        self.__logger.debug('Send loop of {} exiting'.format(self.__class__.__name__))

    def send(self, message):
        """
        Adds the message to the queue, from which it will be sent when the connection to the client will be available.
        :param message: message to be sent
        :return: returns nothing
        """
        try:
            self.__queue.put_nowait(bytes(message.encode('UTF-8')))
        except Full:
            self.__logger.error("Message queue was full. Dropping the message.")

    def stop(self):
        super().stop()
        self.__run = False
        if self.__socket:
            self.__socket.close()
        try:
            self.__queue.put_nowait(None)
        except Full:
            self.__logger.error("Message queue was full. Dropping the message.")
        self.__client_available_event.set()

    @property
    def client_address(self):
        return self.__client_address

    @client_address.setter
    def client_address(self, value):
        self.__client_address = value
        self.__client_available_event.set()


class DataProcessingError(Exception):
    """
    Error thrown when processing error. Throwing this error result in ignoring the received data.
    """
    pass
