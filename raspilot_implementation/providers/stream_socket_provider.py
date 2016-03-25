import logging
import socket
from queue import Queue, Full
from threading import RLock, Thread, Event

import raspilot.providers.base_provider

DEFAULT_SOCKET_TIMEOUT = 1

HOST = ''
MAX_CONNECTIONS = 1
RECV_BYTES = 1024


class StreamSocketProvider(raspilot.providers.base_provider.BaseProvider):
    @staticmethod
    def __create_socket(port):
        """
        Creates and bind a socket to the specified port
        :param port: port to bind to
        :return: created socket which is bound to the specified port
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(DEFAULT_SOCKET_TIMEOUT)
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
        self.__connection = None
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
        self.__socket.listen(MAX_CONNECTIONS)
        self.__socket_listening_event.set()
        while self.__receive:
            try:
                connection, address = self.__socket.accept()
                self._on_client_connected(connection, address)
                self.__logger.info("Client on address {} connected".format(address))
                while self.__receive:
                    try:
                        with self.__data_process_lock:
                            data = connection.recv(self.__recv_size)
                            if not data:
                                break
                            self.__handle_data(data)
                    except DataProcessingError:
                        self.__logger.warning("Wrong data received, ignoring them")
                    except OSError:
                        pass
                self._on_connection_closed()
            except ConnectionAbortedError:
                pass
            except OSError:
                pass

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
        self.__connection = None
        self.__address = None
        try:
            self.__queue.put_nowait(None)
        except Full:
            self.__logger.error("Message queue was full. Dropping the message.")

    def _on_client_connected(self, connection, address):
        """
        Called when a client connects. Client connected event is set, so RaspilotOrientationProvider.wait_for_client()
        is no longer blocked.
        :param connection: new connection
        :param address: client address
        :return: returns nothing
        """
        self.__connection = connection
        self.__address = address
        self.__client_connected_event.set()
        Thread(target=self._send_loop, name="SOCKET_PROVIDER_OUT_{}".format(self.__class__.__name__)).start()

    def _send_loop(self):
        self.__logger.debug("Starting send loop")
        while self.__connection:
            message = self.__queue.get()
            if message and self.__connection:
                self.__logger.info("Sending message to Android.\n{}".format(message))
                self.__connection.send(message.encode())
            else:
                self.__logger.debug("message: {}, connection: {}, source:{}".format(message, self.__connection,
                                                                                    self.__class__.__name__))
                self.__logger.info("Client connection already closed or no messages available")
            self.__queue.task_done()
        self.__logger.debug("Exiting the send loop")

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
        if self.__connection:
            self.__logger.debug("Shutting down and closing the connection")
            self.__connection.shutdown(socket.SHUT_RDWR)
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
