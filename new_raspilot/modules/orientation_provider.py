import struct
import time
from threading import Thread

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory, connectionDone
from twisted.protocols.basic import LineReceiver

from new_raspilot.core.providers.orientation_provider import BaseOrientationProvider
from new_raspilot.core.utils.raspilot_logger import RaspilotLogger
from new_raspilot.raspilot_implementation.commands.stop_command import StopCommand


class RaspilotOrientationProvider(BaseOrientationProvider):
    COUNT_DOWN_LIMIT_IN_SEC = 5

    def __init__(self):
        super().__init__()
        self.__orientation = None
        self.__countdown_thread = None
        self.__connected = False

    def _execute_initialization(self):
        self.__protocol = OrientationProtocol(self)

    def _execute_start(self):
        endpoint = TCP4ServerEndpoint(reactor, 50000)
        endpoint.listen(OrientationProtocolFactory(self.__protocol))
        return True

    def _execute_stop(self):
        pass

    def current_orientation(self):
        return self.__orientation

    def on_new_orientation(self, roll, pitch, azimuth, x_change, y_change, z_change):
        self.__orientation = Orientation(roll, pitch, azimuth, x_change, y_change, z_change)

    def on_connection_opened(self, address):
        self.logger.info("Android Orientation Socket connected from {}".format(address))
        self.__connected = True

    def on_connection_lost(self):
        self.logger.warning("Android Orientation Socket connection lost")
        self.__connected = False
        if not self.__countdown_thread:
            self.__countdown_thread = Thread(target=self.__client_connection_countdown, daemon=True).start()

    def __client_connection_countdown(self):
        i = RaspilotOrientationProvider.COUNT_DOWN_LIMIT_IN_SEC
        while not self.__connected and i >= 1:
            seconds_text = 'second' if i == 1 else 'seconds'
            self.logger.warning(
                "Client has {} {} to reconnect, otherwise Raspilot will be shut down".format(i, seconds_text))
            i -= 1
            time.sleep(1)
        if not self.__connected:
            self.raspilot.command_executor.execute_command(StopCommand())
            self.logger.error("Client connection not restored. Raspilot shutting down")


class Orientation:
    def __init__(self, roll, pitch, azimuth, x_change, y_change, z_change):
        self.__roll = roll
        self.__pitch = pitch
        self.__azimuth = azimuth
        self.__x_change = x_change
        self.__y_change = y_change
        self.__z_change = z_change

    def as_json(self):
        return {'roll': self.roll, 'pitch': self.pitch, 'azimuth': self.__azimuth}

    @property
    def roll(self):
        return self.__roll

    @property
    def pitch(self):
        return self.__pitch

    @property
    def azimuth(self):
        return self.__azimuth

    @property
    def x_change(self):
        return self.__x_change

    @property
    def y_change(self):
        return self.__y_change

    @property
    def z_change(self):
        return self.__z_change


class OrientationProtocol(LineReceiver):
    def __init__(self, callbacks):
        self.__logger = RaspilotLogger.get_logger()
        self.delimiter = bytes([0, 10])
        self.__callbacks = callbacks

    def rawDataReceived(self, data):
        self.__logger.debug("Raw data received {}".format(data))

    def lineReceived(self, line):
        try:
            (roll, pitch, azimuth, x_change, y_change, z_change) = struct.unpack("!ffffff", line)
            self.__callbacks.on_new_orientation(roll, pitch, azimuth, x_change, y_change, z_change)
        except struct.error as e:
            self.__logger.error("Invalid data received.\n\tData were {}.\n\tError was {}".format(line, e))
        except Exception as e:
            self.__logger.critical("Error during data processing.\n\tData were {}.\n\tError was {}".format(line, e))

    def connectionMade(self):
        self.__callbacks.on_connection_opened(self.transport.client[0])

    def connectionLost(self, reason=connectionDone):
        self.__callbacks.on_connection_lost()


class OrientationProtocolFactory(Factory):
    def __init__(self, protocol):
        self.__protocol = protocol

    def buildProtocol(self, addr):
        return self.__protocol
