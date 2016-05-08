import struct
from threading import Thread

import serial
import serial.tools.list_ports

from new_raspilot.core.base_started_module import BaseStartedModule
from new_raspilot.modules.rx_provider import RaspilotRXProvider, RXValues
from new_raspilot.utils.value_mapper import ValueMapper


class ArduinoProvider(BaseStartedModule):
    CONTROL_MODE_CHANGE_COMMAND_TYPE = 'm'
    START_COMMAND_TYPE = 's'
    DISARM_COMMAND_TYPE = 'd'
    RX_FORWARD_COMMAND_TYPE = 'f'
    RX_FORWARD_FMT = "bbbb"

    FLIGHT_MODE_RX = bytes('r', 'ascii')
    FLIGHT_MODES = {FLIGHT_MODE_RX: 'RX Control'}

    BAUD_RATE = 9600

    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__handler = ArduinoCommandHandler()
        self.__arduino_port = None
        self.__serial = serial.Serial()
        self.__serial.baudrate = self.BAUD_RATE
        self.__rx_provider = None

    def _execute_initialization(self):
        super()._execute_initialization()
        self.__rx_provider = self.raspilot.get_module(RaspilotRXProvider)
        if self.__rx_provider is None:
            raise ValueError("RX provider must be set")
        self.__arduino_port = self.__discover_arduino()
        self.__handler.add_handler(self.__command_type_to_bytes(self.START_COMMAND_TYPE), self.__handle_arduino_start)
        self.__handler.add_handler(self.__command_type_to_bytes(self.DISARM_COMMAND_TYPE), self.__handle_disarmed)
        self.__handler.add_handler(self.__command_type_to_bytes(self.RX_FORWARD_COMMAND_TYPE), self.__handle_rx_forward)

    def __discover_arduino(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "Arduino" in port[1]:
                self._log_info("Arduino found on port {}".format(port))
                return port[0]
        return None

    def _execute_start(self):
        if self.__arduino_port:
            self.__serial.port = self.__arduino_port
            self.__serial.open()
            Thread(target=self.__receive_loop).start()
            self.__start_arduino()
            self.__disarm()
            self.__set_rx_control_mode()
            return self.__serial.is_open
        else:
            self._log_warning("Arduino not found")
            return True

    def __start_arduino(self):
        self.send_arduino_command(self.__command_type_to_bytes(self.START_COMMAND_TYPE))

    def __disarm(self):
        self.send_arduino_command(self.__command_type_to_bytes(self.DISARM_COMMAND_TYPE))

    def __set_rx_control_mode(self):
        self.send_arduino_command(self.__command_type_to_bytes(self.CONTROL_MODE_CHANGE_COMMAND_TYPE),
                                  self.FLIGHT_MODE_RX)

    def send_arduino_command(self, cmd_type_bytes, data=None):
        self.__serial.write(cmd_type_bytes)
        if data:
            self.__serial.write(data)

    @staticmethod
    def __command_type_to_bytes(cmd_type):
        return bytes([ord(cmd_type)])

    def __receive_loop(self):
        while self.__serial.is_open:
            try:
                cmd_type = self.__serial.read(1)
                self.__handle_command_type(cmd_type)
            except serial.SerialException as e:
                if self.started:
                    self._log_critical("Error during receiving Arduino data. Error was {}".format(e))

    def _execute_stop(self):
        if self.__serial.is_open:
            self.__serial.close()

    def load(self):
        return True

    def __handle_command_type(self, cmd_type):
        self.__handler.execute_action(cmd_type)

    def __handle_arduino_start(self):
        self._log_info('Arduino Started')

    def __handle_armed(self):
        self._log_info('Motors ARMED')

    def __handle_disarmed(self):
        self._log_info('Motors DISARMED')

    def __handle_rx_forward(self):
        data = self.__serial.read(4)
        if self.__rx_provider:
            (ail, ele, thr, rud) = struct.unpack(self.RX_FORWARD_FMT, data)
            ail = ValueMapper.map(ail, 0, 180, 1000, 2000)
            ele = ValueMapper.map(ele, 0, 180, 1000, 2000)
            thr = ValueMapper.map(thr, 0, 180, 1000, 2000)
            rud = ValueMapper.map(rud, 0, 180, 1000, 2000)
            self.__rx_provider.set_channels(RXValues(ail, ele, thr, rud))


def __handler_rx_control_mode(self, *args):
    if len(args) > 0:
        mode = self.FLIGHT_MODES.get(args[0], None)
        self._log_info('Control mode is {}'.format(mode))
    else:
        self._log_error("Control mode argument missing")


class ArduinoCommandHandler:
    def __init__(self):
        self.__handlers = {}

    def add_handler(self, cmd_type_bytes, handler, args=None):
        if not callable(handler):
            raise ValueError("Handler argument must be callable")
        self.__handlers[cmd_type_bytes] = (handler, args)

    def remove_handler(self, cmd_type_bytes):
        self.__handlers[cmd_type_bytes] = None

    def execute_action(self, cmd_type_bytes):
        handler = self.__handlers.get(cmd_type_bytes, None)
        if handler:
            args = handler[1]
            method = handler[0]
            if args:
                method(args)
            else:
                method()
