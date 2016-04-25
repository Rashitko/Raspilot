import logging
import struct
from threading import RLock, Thread, Event

from raspilot_implementation.pid.pid_controller import PID
from raspilot_implementation.providers.stream_socket_provider import StreamSocketProvider

from obsolete.raspilot.providers import OrientationProvider, OrientationProviderConfig

CLIENT_CONNECTION_TIMEOUT = 10

SERIALIZATION_SCALE_FACTOR = 1

MAX_CONNECTIONS = 1
HOST = ''


class RaspilotOrientationProvider(OrientationProvider):
    MESSAGE_COMPONENTS = 6
    FMT = '!' + 'f' * MESSAGE_COMPONENTS
    RECV_BYTES = struct.calcsize(FMT)
    NAME = 'RaspilotOrientationProvider'

    ROLL_INDEX = 0
    PITCH_INDEX = 1
    AZIMUTH_INDEX = 2
    X_ANGULAR_INDEX = 3
    Y_ANGULAR_INDEX = 4
    Z_ANGULAR_INDEX = 5

    def __init__(self, config):
        super().__init__(config)
        self.__socket_provider = OrientationStreamSocketProvider(port=config.orientation_port,
                                                                 recv_size=RaspilotOrientationProvider.RECV_BYTES,
                                                                 name=RaspilotOrientationProvider.NAME)
        self.__logger = logging.getLogger('raspilot.log')
        self.__orientation = None
        self.__prop_lock = RLock()
        self.__pitch_stabilise_pid = PID()
        self.__pitch_rate_pid = PID()

    def current_orientation(self):
        return self.__socket_provider.current_orientation

    def initialize(self):
        super().initialize()
        self.__socket_provider.raspilot = self.raspilot

    def stop(self):
        super().stop()
        self.__socket_provider.stop()

    def start(self):
        super().start()
        return self.__socket_provider.start()


class OrientationStreamSocketProvider(StreamSocketProvider):
    def __init__(self, port, recv_size, name):
        super().__init__(port, recv_size, name)
        self.__logger = logging.getLogger('raspilot.log')
        self.__orientation = None
        self.__connection_event = None

    def _handle_data(self, data):
        super()._handle_data(data)
        orientation_size = struct.calcsize(RaspilotOrientationProvider.FMT)
        byte_array = [data[i:i+orientation_size] for i in range(0, len(data), orientation_size)]
        self.__orientation = self.__read_orientation(struct.unpack(RaspilotOrientationProvider.FMT, byte_array[-1]))

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

    def on_client_connected(self, address):
        if self.__connection_event:
            self.__connection_event.set()

    def on_client_connection_lost(self, reason):
        super().on_client_connection_lost(reason)
        if not self.__connection_event:
            Thread(target=self.__stop_if_no_connection).start()

    def __stop_if_no_connection(self):
        """
        Waits for the client connection. If no connection is made in the specified time, stops the Raspilot
        :return: returns nothing
        """
        self.__connection_event = Event()
        self.__connection_event.wait(CLIENT_CONNECTION_TIMEOUT)
        if not self.connected:
            self.__logger.warning("Client not connected after 10 seconds. Stopping Raspilot")
            self.raspilot.stop()
        self.__connection_event = None


    @property
    def current_orientation(self):
        return self.__orientation


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
