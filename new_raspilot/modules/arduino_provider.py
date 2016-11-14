import struct
from threading import Thread

import serial
import serial.tools.list_ports

from new_raspilot.core.base_started_module import BaseStartedModule
from new_raspilot.raspilot_implementation.commands.orientation_command import OrientationCommand
from new_raspilot.raspilot_implementation.commands.rx_update_command import RXUpdateCommand


class ArduinoProvider(BaseStartedModule):
    BAUD_RATE = 115200
    FC_OUTPUT_COMMAND_TYPE = 'o'
    FC_OUTPUT_COMMAND_FMT = 'hhhh'

    RX_INPUT_COMMAND_TYPE = 'i'
    RX_INPUT_COMMAND_FMT = 'hhhhhhb'

    ORIENTATION_COMMAND_TYPE = 'O'
    ORIENTATION_COMMAND_FMT = 'hhh'
    ORIENTATION_MODIFIER = 100

    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__handler = ArduinoCommandHandler()
        self.__arduino_port = None
        self.__serial = serial.Serial()
        self.__serial.baudrate = self.BAUD_RATE

    def _execute_initialization(self):
        super()._execute_initialization()
        self.__arduino_port = self.__discover_arduino()
        self.__handler.add_handler(self.__command_type_to_bytes(self.RX_INPUT_COMMAND_TYPE), self.__handle_rx_input)
        self.__handler.add_handler(self.__command_type_to_bytes(self.FC_OUTPUT_COMMAND_TYPE), self.__handle_fc_output)
        self.__handler.add_handler(self.__command_type_to_bytes(self.ORIENTATION_COMMAND_TYPE),
                                   self.__handle_orientation)

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
            return self.__serial.is_open
        else:
            self._log_warning("Arduino not found")
            return True

    def send_arduino_command(self, cmd_type_bytes, data=None):
        if self.__serial and self.__serial.is_open:
            try:
                self.__serial.write(cmd_type_bytes)
                if data:
                    self.__serial.write(data)
            except serial.SerialException as e:
                self._log_error("An error occurred during transmission to Arduino. Error was {}".format(e))

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

    def __handle_rx_input(self):
        data = self.__serial.read(struct.calcsize(self.RX_INPUT_COMMAND_FMT))
        (ail, ele, thr, rud, aux1, aux2, mode) = struct.unpack(self.RX_INPUT_COMMAND_FMT, data)
        cmd = RXUpdateCommand(ail, ele, thr, rud)
        self.raspilot.command_executor.execute_command(cmd)

    def __handle_fc_output(self):
        data = self.__serial.read(struct.calcsize(self.FC_OUTPUT_COMMAND_FMT))
        (ail, ele, thr, rud) = struct.unpack(self.FC_OUTPUT_COMMAND_FMT, data)

    def __handle_orientation(self):
        data = self.__serial.read(struct.calcsize(self.ORIENTATION_COMMAND_FMT))
        (roll, pitch, yaw) = struct.unpack(self.ORIENTATION_COMMAND_FMT, data)
        orientation = tuple(x / self.ORIENTATION_MODIFIER for x in (roll, pitch, yaw))
        cmd = OrientationCommand(orientation[0], orientation[1], orientation[2])
        self.raspilot.command_executor.execute_command(cmd)


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
