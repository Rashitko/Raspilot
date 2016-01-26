import logging
import struct
from threading import Thread

import serial
import serial.serialutil
import serial.tools.list_ports

from raspilot.providers.rx_provider import RXProvider, RXConfig
from raspilot_implementation.rc_command import RCChannelValues

ARDUINO_PORT_KEYWORD = "Arduino"
BAUD_RATE = 115200
FMT = "hhhhh"
CHANNELS_COUNT = 5


class RaspilotRXProvider(RXProvider):
    def __init__(self, config):
        super().__init__(config)
        self.__port = None
        self.__reading_thread = None
        self.__run = False
        self.__logger = logging.getLogger('raspilot.log')
        self.__channels = None

    def start(self):
        super().start()
        port = ArduinoProber.search_arduino_com_port(ARDUINO_PORT_KEYWORD)
        if port:
            self.__logger.info("Arduino found on port {}".format(port))
            try:
                self.__port = serial.Serial(port, BAUD_RATE)
                self.__run = True
                self.__reading_thread = Thread(target=self.__read_serial_loop, name="RX_INPUT_THREAD")
                self.__reading_thread.start()
            except serial.SerialException:
                pass
        else:
            self.__logger.warn("Arduino NOT found")
        return self.__port is not None

    def __read_serial_loop(self):
        while self.__run:
            try:
                if not self.__port.isOpen():
                    self.__port.open()
                data = self.__port.read(struct.calcsize(FMT))
                channels = struct.unpack(FMT, data)
                received_channels_count = len(channels)
                if received_channels_count == self.get_channels_count():
                    self.__channels = RCChannelValues(channels)
                else:
                    self.__logger.error("Wrong number of channels received. Expected {} channels but got {}".format(
                            self.get_channels_count(), received_channels_count))
            except serial.SerialException as serial_ex:
                self.__logger.error(serial_ex)
                self.__port.close()
            except struct.error as struct_ex:
                self.__logger.error(struct_ex)
            except Exception as e:
                self.__logger.error(e)
        self.__port.close()

    def stop(self):
        super().stop()
        self.__run = False
        return True

    def get_channels_count(self):
        return CHANNELS_COUNT

    def get_channels(self):
        return self.__channels

    def get_channel_value(self, channel):
        if channel > self.get_channels_count() or channel < 1:
            return None
        return self.get_channels()[channel]

    @property
    def ailerons(self):
        return self.__channels.ailerons

    @property
    def elevator(self):
        return self.__channels[RCChannelValues.CHANNELS_MAP['elevator']]

    @property
    def throttle(self):
        return self.__channels[RCChannelValues.CHANNELS_MAP['throttle']]

    @property
    def rudder(self):
        return self.__channels[RCChannelValues.CHANNELS_MAP['rudder']]

    @property
    def aux(self):
        return self.__channels[RCChannelValues.CHANNELS_MAP['aux']]


class RaspilotRXConfig(RXConfig):
    pass


class ArduinoProber:
    """
    Class used to discover the port where Arduino is connected.
    """

    @staticmethod
    def search_arduino_com_port(port_keyword):
        """
        Searches for an available serial port with given keyword in the name and returns path to this port,
         or None if no such port is available
        :param port_keyword keyword to search in port names for
        :return: path to port with given keyword, or None if no such port exists
        """
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if port_keyword in port[1]:
                return port[0]
        return None
