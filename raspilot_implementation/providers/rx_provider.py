import logging
import struct
from threading import Thread

import serial
import serial.serialutil
import serial.tools.list_ports

from raspilot.providers.rx_provider import RXProvider, RXConfig
from raspilot_implementation.utils.rc_command import RCChannelValues


class RaspilotRXProvider(RXProvider):
    ARDUINO_PORT_KEYWORD = "Arduino"
    FMT = "hhhhh"
    """
    Default FMT used to unpack the struct received from Arduino
    """

    CHANNELS_COUNT = 5
    """
    Default number of channels read by Arduino from the RX
    """

    def __init__(self, config):
        """
        Creates a new 'RaspilotRXProvider'. This provider is used with Arduino (connected via a serial port) which
        sends PWM frequencies read from the radio RX.
        :param config: config used to configure this provider
        :return: returns nothing
        """
        super().__init__(config)
        self.__baud_rate = config.baud_rate
        self.__port = None
        self.__reading_thread = None
        self.__run = False
        self.__logger = logging.getLogger('raspilot.log')
        self.__channels = None

    def start(self):
        """
        Tries to find Arduino a connect with it over the serial port. If Arduino is found and serial is successfully
        opened, loop which receives the data from Arduino is started (in separate Thread).
        :return: True if connection was successful, False otherwise
        """
        super().start()
        port = ArduinoProber.search_arduino_com_port(self.ARDUINO_PORT_KEYWORD)
        if port:
            self.__logger.info("Arduino found on port {}. Opening connection with baud rate {}".format(port, self.__baud_rate))
            try:
                self.__port = serial.Serial(port, self.__baud_rate)
                self.__run = True
                self.__reading_thread = Thread(target=self.__read_serial_loop, name="RX_INPUT_THREAD")
                self.__reading_thread.start()
            except serial.SerialException:
                pass
        else:
            self.__logger.warn("Arduino NOT found")
        return self.__port is not None

    def __read_serial_loop(self):
        """
        While provider is started reads data from serial port. If port is not opened (might be because of an Exception),
        ArduinoProber is used to find Arduino and new serial.Serial() instance is created. Exceptions which might be
        risen during the communication and data processing are handled here. After stop of this provider is the port
        closed and Thread exits.
        :return: returns nothing
        """
        while self.__run:
            try:
                if not self.__port.isOpen():
                    port = ArduinoProber.search_arduino_com_port(self.ARDUINO_PORT_KEYWORD)
                    if port:
                        self.__port = serial.Serial(port, self.__baud_rate)
                data = self.__port.read(struct.calcsize(self.FMT))
                channels = struct.unpack(self.FMT, data)
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
        self.__port.close()

    def stop(self):
        """
        Sets the flag, so loop receiving data from Arduino will exit.
        :return: returns True
        """
        super().stop()
        self.__run = False
        return True

    def get_channels_count(self):
        return self.CHANNELS_COUNT

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
    def __init__(self, baud_rate):
        super().__init__()
        self.__baud_rate = baud_rate

    @property
    def baud_rate(self):
        return self.__baud_rate

    @baud_rate.setter
    def baud_rate(self, value):
        self.__baud_rate = value


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
