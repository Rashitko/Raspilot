import socket
import struct
from threading import Thread, Event, RLock

from raspilot.providers.orientation_provider import OrientationProvider, OrientationProviderConfig

FMT = "!dddd"
RECV_BYTES = 1024
MAX_CONNECTIONS = 1
HOST = ''


class RaspilotOrientationProvider(OrientationProvider):

    @staticmethod
    def __create_socket(port):
        """
        Creates and bind a socket to the specified port
        :param port: port to bind to
        :return: created socket which is bound to the specified port
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, port))
        return s

    def __init__(self, config):
        super().__init__(config)
        self.__port = config.port
        self.__socket = None
        self.__client_connected_event = Event()
        self.__socket_listening_event = Event()
        self.__data_process_lock = RLock()
        self.__receive = True
        self.__connection = None
        self.__address = None

    def start(self):
        super().start()
        try:
            self.__socket = self.__create_socket(self.__port)
            Thread(target=self.__process).start()
            return True
        except:
            return False

    def __process(self):
        """
        Opens the socket and waits for the connection, then receives data until RaspilotOrientationProvider.stop()
        is called
        :return: returns nothing
        """
        self.__socket.listen(MAX_CONNECTIONS)
        self.__socket_listening_event.set()
        while self.__receive:
            try:
                connection, address = self.__socket.accept()
                self.__on_client_connected(connection, address)
                print("Client {} on address {} connected".format(connection, address))
                while self.__receive:
                    data = connection.recv(RECV_BYTES)
                    if not data:
                        break
                    try:
                        self.__on_data_received(data)
                    except DataProcessingError:
                        print("Invalid data received ignoring them.")
                connection.close()
                print("Connection closed")
                self.__on_connection_closed()
            except ConnectionAbortedError:
                print("Connection Aborted error")
                pass

    def __on_connection_closed(self):
        """
        Sets client connection and address to None
        :return: returns nothing
        """
        self.__connection = None
        self.__address = None

    def __on_client_connected(self, connection, address):
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

    def __on_data_received(self, data):
        """
        Processes the received data. Should return fast, because it blocks receiving of other data from the socket.
        Unpacks data, creates Quaternion from them, and saves it so it can be read by other classes for example
        the Notifier. If any exception is thrown during the processing DataProcessingError is thrown
        :param data: received data
        :return: returns nothing
        :exception: DataProcessingError if any exception is risen during the processing
        """
        with self.__data_process_lock:
            try:
                (x, y, z, w) = struct.unpack(FMT, data)
            except Exception as e:
                print("An error occurred. Error was: {}".format(e))
                raise DataProcessingError("An error occurred. Error was: {}".format(e))

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
            self.__connection.shutdown(0)
        if self.__socket:
            self.__socket.close()


class RaspilotOrientationProviderConfig(OrientationProviderConfig):
    def __init__(self, port):
        """
        Creates a new 'RaspilotOrientationProviderConfig' which is used for
        the RaspilotOrientationProviderConfiguration. See wiki for more information about this provider.
        :param port: port on which should the provider listen for orientation data
        :return: returns nothing
        """
        super().__init__()
        self.__port = port

    @property
    def port(self):
        return self.__port


class DataProcessingError(Exception):
    """
    Error thrown when processing error. Throwing this error result in ignoring the received data.
    """
    pass
