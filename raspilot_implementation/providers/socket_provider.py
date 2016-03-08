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
        logger.info('Opening socket on {}:{}'.format(HOST, port))
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
        self.__receive = True
        self.__address = None
        self.__socket_listening_event = Event()
        self.__client_connected_event = Event()
        self.__queue = Queue()
        self.__recv_lock = RLock()

    def start(self):
        super().start()
        # noinspection PyBroadException
        try:
            self.__socket = self.__create_socket(self.__port)
            Thread(target=self._process, name="SOCKET_PROVIDER_IN_{}".format(self.__class__.__name__)).start()
            self.__socket_listening_event.wait()
            return True
        except Exception as e:
            self.__logger.error("An error occurred during socket provider start. {}".format(e))
            return False

    def _process(self):
        """
        Opens the socket and waits for the connection, then receives data until SocketProvider.stop()
        is called
        :return: returns nothing
        """
        self.__socket_listening_event.set()
        while self.__receive:
            try:
                with self.__data_process_lock:
                    (data, address) = self.__socket.recvfrom(1024)
                    if not data:
                        break
                    self.__handle_data(data)
            except DataProcessingError:
                self.__logger.warning("Wring data received, ignoring them")
            except OSError:
                pass
        self.__socket.close()
        self._on_connection_closed()

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

    def _on_connection_closed(self):
        """
        Sets client connection and address to None
        :return: returns nothing
        """
        self.__address = None
        try:
            self.__queue.put_nowait(None)
        except Full:
            self.__logger.error("Message queue was full. Dropping the message.")

    def _on_client_connected(self, address):
        """
        Called when a client connects. Client connected event is set, so RaspilotOrientationProvider.wait_for_client()
        is no longer blocked.
        :param address: client address
        :return: returns nothing
        """
        self.__address = address
        self.__client_connected_event.set()
        Thread(target=self._send_loop, name="SOCKET_PROVIDER_OUT_{}".format(self.__class__.__name__)).start()

    def _send_loop(self):
        raise NotImplementedError("Send loop not implemented yet")

    def send(self, message):
        """
        Adds the message to the queue, from which it will be sent when the connection to the client will be available.
        :param message: message to be sent
        :return: returns nothing
        """
        try:
            self.__queue.put_nowait(message)
        except Full:
            self.__logger.error("Message queue was full. Dropping the message.")

    def wait_for_client(self):
        """
        Returns when a new client is connected.
        :return: returns client address
        """
        self.__client_connected_event.wait()
        return self.__address

    def stop(self):
        super().stop()
        self.__receive = False
        if self.__socket:
            self.__socket.close()
        try:
            self.__queue.put_nowait(None)
        except Full:
            self.__logger.error("Message queue was full. Dropping the message.")


class DataProcessingError(Exception):
    """
    Error thrown when processing error. Throwing this error result in ignoring the received data.
    """
    pass
