import socket
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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, port))
        return s

    def __init__(self, port):
        raspilot.providers.base_provider.BaseProvider.__init__(self, None)
        self.__port = port
        self.__socket = None
        self.__data_process_lock = RLock()
        self.__receive = True
        self.__connection = None
        self.__address = None
        self.__socket_listening_event = Event()
        self.__client_connected_event = Event()

    def start(self):
        super().start()
        try:
            self.__socket = self.__create_socket(self.__port)
            Thread(target=self._process).start()
            self.__socket_listening_event.wait()
            return True
        except:
            return False

    def _process(self):
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
                self._on_client_connected(connection, address)
                print("Client {} on address {} connected".format(connection, address))
                while self.__receive:
                    try:
                        with self.__data_process_lock:
                            data = connection.recv(RECV_BYTES)
                            if not data:
                                break
                            self.__handle_data(data)
                    except DataProcessingError:
                        print("Wrong data received, ignoring them")
                    except OSError:
                        pass
                connection.close()
                print("Connection closed")
                self._on_connection_closed()
            except ConnectionAbortedError:
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
            print(message)
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
            self.__connection.close()
        if self.__socket:
            self.__socket.close()

class DataProcessingError(Exception):
    """
    Error thrown when processing error. Throwing this error result in ignoring the received data.
    """
    pass
