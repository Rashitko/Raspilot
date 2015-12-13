import logging
import struct
from threading import RLock

from raspilot.providers.orientation_provider import OrientationProvider, OrientationProviderConfig
from raspilot_implementation.providers.socket_provider import SocketProvider

FMT = "!ddd"
RECV_BYTES = 24
MAX_CONNECTIONS = 1
HOST = ''


class RaspilotOrientationProvider(SocketProvider, OrientationProvider):
    def __init__(self, config):
        SocketProvider.__init__(self, port=config.orientation_port, recv_size=RECV_BYTES)
        OrientationProvider.__init__(self, config)
        self.__logger = logging.getLogger('raspilot.log')
        self.__orientation = None
        self.__offset_orientation = Orientation(0, 0, 0)
        self.__prop_lock = RLock()

    def _on_data_received(self, data):
        """
        Processes the received data. Should return fast, because it blocks receiving of other data from the socket.
        The data should be three doubles in format: roll, pitch, yaw.
        Unpacks data, and saves the received angles so it can be read by other classes for example
        the Notifier.
        :param data: received data
        :return: returns nothing
        """
        with self.__prop_lock:
            (roll, pitch, yaw) = struct.unpack(FMT, data)
            self.__orientation = Orientation(roll, pitch, yaw)

    def current_orientation(self):
        return self.__get_offset_orientation()

    def __get_offset_orientation(self):
        """
        Returns orientation which is modified with the offsets. Offsets are set with the set_neutral method.
        :return: returns Orientation
        """
        if self.__orientation:
            return Orientation(
                    self.__orientation.roll - self.__offset_orientation.roll,
                    self.__orientation.pitch - self.__offset_orientation.pitch,
                    self.__orientation.yaw)
        else:
            return None

    def set_neutral(self):
        self.__logger.info("Neutral orientation set.")
        self.__offset_orientation = self.current_orientation()
        return self.__offset_orientation is not None


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


class Orientation:
    """
    Wrapper class for the roll pitch and yaw angles.
    """

    def __init__(self, roll, pitch, yaw):
        """
        Creates a new 'Orientation' with roll, pitch and yaw angles specified.
        :param roll: roll angle in degrees
        :param pitch: pitch angle in degrees
        :param yaw: yaw andle in degrees
        :return: returns nothing
        """
        self.__roll = roll
        self.__pitch = pitch
        self.__yaw = yaw

    def to_json(self):
        return {'roll': self.roll, 'pitch': self.pitch, 'yaw': self.roll}

    @property
    def roll(self):
        return self.__roll

    @property
    def pitch(self):
        return self.__pitch

    @property
    def yaw(self):
        return self.__yaw
