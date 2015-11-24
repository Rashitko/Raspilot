import struct

from raspilot.providers.orientation_provider import OrientationProvider, OrientationProviderConfig
from raspilot_implementation.providers.socket_provider import SocketProvider

FMT = "!ddd"
RECV_BYTES = 1024
MAX_CONNECTIONS = 1
HOST = ''


class RaspilotOrientationProvider(SocketProvider, OrientationProvider):
    def __init__(self, config):
        OrientationProvider.__init__(self, config)
        SocketProvider.__init__(self, config.orientation_port)
        self.__roll = 0
        self.__pitch = 0
        self.__yaw = 0

    def _on_data_received(self, data):
        """
        Processes the received data. Should return fast, because it blocks receiving of other data from the socket.
        The data should be three doubles in format: roll, pitch, yaw.
        Unpacks data, and saves the received angles so it can be read by other classes for example
        the Notifier.
        :param data: received data
        :return: returns nothing
        """
        (self.__roll, self.__pitch, self.__yaw) = struct.unpack(FMT, data)
        print("roll: {}, pitch: {}, yaw: {}".format(self.__roll, self.__pitch, self.__yaw))


class RaspilotOrientationProviderConfig(OrientationProviderConfig):
    def __init__(self, orientation_port):
        """
        Creates a new 'RaspilotOrientationProviderConfig' which is used for
        the RaspilotOrientationProviderConfiguration. See wiki for more information about this provider.
        :param orientation_port: port on which should the provider listen for orientation data
        :return: returns nothing
        """
        super().__init__()
        self.__orientation_port = orientation_port

    @property
    def orientation_port(self):
        return self.__orientation_port
