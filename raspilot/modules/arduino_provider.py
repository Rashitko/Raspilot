import struct
from threading import Thread, Event
from time import sleep

import serial
import serial.tools.list_ports
from up.base_started_module import BaseStartedModule
from up.utils.config_reader import ConfigReader
from up.utils.up_logger import UpLogger

import raspilot.flight_controller.flight_controller


class ArduinoProvider(BaseStartedModule):
    BAUD_RATE = 9600

    DISCOVERY_RETRY_INTERVAL = 1

    FLIGHT_MODE_RATE = b'r'
    FLIGHT_MODE_FBW = b'f'
    FLIGHT_MODE_RTH = b'h'

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
        self.__receive_loop_lock = None
        self.__is_connected = False

    def _execute_initialization(self):
        super()._execute_initialization()
        self.__arduino_port = self.__discover_arduino()
        self.__handler.add_handler(ArduinoCommandHandler.START_COMMAND_TYPE, self.__handle_start)
        self.__handler.add_handler(ArduinoCommandHandler.ARM_COMMAND_TYPE, self.__handle_armed_change, 0, True)
        self.__handler.add_handler(ArduinoCommandHandler.DISARM_COMMAND_TYPE, self.__handle_armed_change, 0, False)
        self.__handler.add_handler(ArduinoCommandHandler.ALTITUDE_COMMAND_TYPE, self.__handle_altitude_confirmation, 2)
        self.__handler.add_handler(ArduinoCommandHandler.LOCATION_COMMAND_TYPE, self.__handle_location_confirmation, 8)
        self.__handler.add_handler(ArduinoCommandHandler.ACTUAL_HEADING_COMMAND_TYPE,
                                   self.__handle_actual_heading_confirmation, 2)
        self.__handler.add_handler(ArduinoCommandHandler.REQUIRED_HEADING_COMMAND_TYPE,
                                   self.__handle_required_heading_confirmation, 2)

    def _execute_start(self):
        if self.__arduino_port:
            self.__serial.port = self.__arduino_port
            self.__serial.open()
            self.__receive_loop_lock = Event()
            Thread(target=self.__receive_loop).start()
            self.__receive_loop_lock.wait(10)
            self.send_arduino_command(ArduinoCommandHandler.START_COMMAND_TYPE)
            self.send_arduino_command(ArduinoCommandHandler.DISARM_COMMAND_TYPE)
            return self.__serial.is_open
        else:
            self._log_warning("Arduino not found")
            return True

    def _execute_stop(self):
        if self.__serial and self.__serial.is_open:
            self.__serial.close()
            self.__is_connected = False

    def load(self):
        return True

    def send_arduino_command(self, cmd_type_bytes, data=None):
        if self.__serial and self.__serial.is_open:
            if not isinstance(cmd_type_bytes, bytes):
                type_bytes = bytes(cmd_type_bytes, "utf-8")
            else:
                type_bytes = cmd_type_bytes
            try:
                self.logger.debug("Sending command %s" % type_bytes.decode("utf-8"))
                self.__serial.write(type_bytes)
                if data:
                    self.__serial.write(data)
            except serial.SerialException as e:
                self._log_error("An error occurred during transmission to Arduino. Error was {}".format(e))

    def set_altitude(self, altitude):
        data = struct.pack("h", altitude)
        self.send_arduino_command(ArduinoCommandHandler.ALTITUDE_COMMAND_TYPE, data)

    def set_location(self, latitude, longitude):
        data = struct.pack("!ff", latitude, longitude)
        self.send_arduino_command(ArduinoCommandHandler.LOCATION_COMMAND_TYPE, data)

    def set_required_heading(self, heading):
        data = struct.pack("!h", round(heading))
        self.send_arduino_command(ArduinoCommandHandler.REQUIRED_HEADING_COMMAND_TYPE, data)

    def set_actual_heading(self, heading):
        data = struct.pack("!h", round(heading))
        self.send_arduino_command(ArduinoCommandHandler.ACTUAL_HEADING_COMMAND_TYPE, data)

    def set_flight_mode(self, mode):
        if mode == raspilot.flight_controller.flight_controller.RaspilotFlightController.FLIGHT_MODE_RATE:
            arduino_mode = self.FLIGHT_MODE_RATE
        elif mode == raspilot.flight_controller.flight_controller.RaspilotFlightController.FLIGHT_MODE_FBW:
            arduino_mode = self.FLIGHT_MODE_FBW
        elif mode == raspilot.flight_controller.flight_controller.RaspilotFlightController.FLIGHT_MODE_RTH:
            arduino_mode = self.FLIGHT_MODE_RTH
        else:
            self.logger.error('Flight Mode %s not supported' % mode)
            return
        data = struct.pack("!c", arduino_mode)
        self.send_arduino_command(ArduinoCommandHandler.FLIGHT_MODE_SET_COMMAND_TYPE, data)

    @staticmethod
    def __command_type_to_bytes(cmd_type):
        return bytes([ord(cmd_type)])

    def __receive_loop(self):
        while self.__serial.is_open:
            try:
                if self.__receive_loop_lock:
                    self.__receive_loop_lock.set()
                cmd_type = self.__serial.read(1)
                self.__is_connected = True
                payload_size = self.__handler.get_command_payload_size(cmd_type)
                payload = self.__serial.read(payload_size)
                self.__handler.execute_action(cmd_type, payload)
            except serial.SerialException as e:
                if self.started:
                    self._log_critical("Error during receiving Arduino data. Error was {}".format(e))
            except TypeError as e:
                if not self.started:
                    pass
                else:
                    raise e

    def __handle_start(self, payload):
        self.logger.info("Arduino Started")

    def __handle_armed_change(self, *args):
        if args[0]:
            self.logger.warn("Arduino ARMED")
        else:
            self.logger.warn("Arduino DISARMED")

    def __discover_arduino(self):
        config = ConfigReader.instance().global_config
        arduino_required = config.get('DEFAULT', 'WAIT FOR ARDUINO', fallback='false')
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "Arduino" in port[1]:
                self._log_info("Arduino found on port {}".format(port))
                return port[0]
        while arduino_required.lower() == 'true':
            self.logger.warning('Arduino required but not found yet. Will try again in 1s')
            sleep(self.DISCOVERY_RETRY_INTERVAL)
        return None

    def __handle_altitude_confirmation(self, payload):
        altitude, = struct.unpack("h", payload)
        self.logger.debug("Arduino confirmed altitude %s" % altitude)

    def __handle_location_confirmation(self, payload):
        latitude, longitude = struct.unpack("!ff", payload)
        self.logger.debug("Arduino confirmed location LAT: %s, LON: %s" % (latitude, longitude))

    def __handle_actual_heading_confirmation(self, payload):
        (heading,) = struct.unpack("!h", payload)
        self.logger.debug("Arduino has confirmed actual heading %s˚" % heading)

    def __handle_required_heading_confirmation(self, payload):
        (heading,) = struct.unpack("!h", payload)
        self.logger.debug("Arduino has confirmed required heading %s˚" % heading)

    @property
    def is_connected(self):
        return self.__is_connected


class ArduinoCommandHandler:
    START_COMMAND_TYPE = 's'
    ARM_COMMAND_TYPE = 'a'
    DISARM_COMMAND_TYPE = 'd'
    ALTITUDE_COMMAND_TYPE = 'h'
    FLIGHT_MODE_SET_COMMAND_TYPE = 'M'
    FLIGHT_MODE_GET_COMMAND_TYPE = 'm'
    LOCATION_COMMAND_TYPE = 'l'
    ACTUAL_HEADING_COMMAND_TYPE = 'b'
    REQUIRED_HEADING_COMMAND_TYPE = 'B'

    def __init__(self):
        self.__handlers = {}
        self.__logger = UpLogger.get_logger()

    def add_handler(self, cmd_type_bytes, handler, payload_size=0, args=None):
        if not callable(handler):
            raise ValueError("Handler argument must be callable")
        if not isinstance(cmd_type_bytes, bytes):
            type_bytes = bytes(cmd_type_bytes, 'utf-8')
        else:
            type_bytes = cmd_type_bytes
        self.__handlers[type_bytes] = (handler, payload_size, args)
        self.__logger.debug("Handler for command type '%s' registered" % cmd_type_bytes)

    def remove_handler(self, cmd_type_bytes):
        self.__handlers[cmd_type_bytes] = None

    def execute_action(self, cmd_type_bytes, payload):
        self.__logger.debug("Executing action for cmd type '%s'" % cmd_type_bytes.decode('utf-8'))
        handler = self.__handlers.get(cmd_type_bytes, None)
        if handler:
            args = handler[2]
            method = handler[0]
            if args is not None:
                method(payload, args)
            else:
                method(payload)
        else:
            self.__logger.warn("No handler for cmd type '%s' found" % cmd_type_bytes.decode('utf-8'))

    def get_command_payload_size(self, cmd_type_bytes):
        handler = self.__handlers.get(cmd_type_bytes, None)
        if handler:
            return handler[1]
        return 0
