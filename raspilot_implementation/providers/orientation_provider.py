import logging
import struct
from threading import RLock

from raspilot.providers.orientation_provider import OrientationProvider, OrientationProviderConfig
from raspilot_implementation.pid.pid_controller import PID
from raspilot_implementation.providers.stream_socket_provider import StreamSocketProvider

SERIALIZATION_SCALE_FACTOR = 1

MAX_CONNECTIONS = 1
HOST = ''


class RaspilotOrientationProvider(StreamSocketProvider, OrientationProvider):
    MESSAGE_COMPONENTS = 6
    FMT = '!' + 'f' * MESSAGE_COMPONENTS
    RECV_BYTES = struct.calcsize(FMT)

    ROLL_INDEX = 0
    PITCH_INDEX = 1
    AZIMUTH_INDEX = 2
    X_ANGULAR_INDEX = 3
    Y_ANGULAR_INDEX = 4
    Z_ANGULAR_INDEX = 5

    def __init__(self, config):
        StreamSocketProvider.__init__(self, port=config.orientation_port, recv_size=RaspilotOrientationProvider.RECV_BYTES)
        OrientationProvider.__init__(self, config)
        self.__logger = logging.getLogger('raspilot.log')
        self.__orientation = None
        self.__prop_lock = RLock()
        self.__pitch_stabilise_pid = PID()
        self.__pitch_rate_pid = PID()

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
            self.__orientation = self.__read_orientation(struct.unpack(RaspilotOrientationProvider.FMT, data))

    @staticmethod
    def __read_orientation(orientation_tuple):
        """
        Reads the orientation from the orientation tuple. The tuple must have particular data under following keys:
         RaspilotOrientationProvider#ROLL_INDEX
         RaspilotOrientationProvider#ROLL_PITCH
         RaspilotOrientationProvider#ROLL_AZIMUTH
         RaspilotOrientationProvider#X_ANGULAR
         RaspilotOrientationProvider#Y_ANGULAR
         RaspilotOrientationProvider#Z_ANGULAR.
        No exceptions are handled here.
        :param orientation_tuple: tuple to read data from
        :return: new Orientation
        """
        orientation_tuple = tuple(x / SERIALIZATION_SCALE_FACTOR for x in orientation_tuple)
        roll = orientation_tuple[RaspilotOrientationProvider.ROLL_INDEX]
        pitch = orientation_tuple[RaspilotOrientationProvider.PITCH_INDEX]
        azimuth = orientation_tuple[RaspilotOrientationProvider.AZIMUTH_INDEX]
        x_angular = orientation_tuple[RaspilotOrientationProvider.X_ANGULAR_INDEX]
        y_angular = orientation_tuple[RaspilotOrientationProvider.Y_ANGULAR_INDEX]
        z_angular = orientation_tuple[RaspilotOrientationProvider.Z_ANGULAR_INDEX]
        return Orientation(roll, pitch, azimuth, x_angular, y_angular, z_angular)

    def current_orientation(self):
        return self.__orientation

    def stop(self):
        OrientationProvider.stop(self)
        StreamSocketProvider.stop(self)


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

    def __init__(self, roll, pitch, yaw, x_angular, y_angular, z_angular):
        """
        Creates a new 'Orientation' with roll, pitch, yaw angles and angular speeds specified.
        :param roll: roll angle in degrees
        :param pitch: pitch angle in degrees
        :param yaw: yaw angle in degrees
        :param x_angular: angular speed around x-axis
        :param y_angular: angular speed around y-axis
        :param z_angular: angular speed around z-axis
        :return: returns nothing
        """
        self.__roll = roll
        self.__pitch = pitch
        self.__yaw = yaw
        self.__x_angular = x_angular
        self.__y_angular = y_angular
        self.__z_angular = z_angular

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

    @property
    def x_angular(self):
        return self.__x_angular

    @property
    def y_angular(self):
        return self.__y_angular

    @property
    def z_angular(self):
        return self.__z_angular
