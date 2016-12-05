import time

from up.flight_controller.base_flight_controller import BaseFlightController
from raspilot.modules.arduino_provider import ArduinoProvider

from raspilot.commands.flight_mode_command import FlightModeCommand, \
    FlightModeCommandHandler


class RaspilotFlightController(BaseFlightController):
    MAX_ROLL_ANGLE = 45
    MAX_PITCH_ANGLE = 45
    MIN_PWM = 1000
    MAX_PWM = 2000
    MIN_ANGLE = 0
    MAX_ANGLE = 180
    STAB_CONSTRAINT = 250
    RATE_CONSTRAINT = 500

    def __init__(self):
        super().__init__()
        self.__arduino_provider = None
        self.__mode_change_handle = None

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__arduino_provider = self.raspilot.get_module(ArduinoProvider)
        if not self.__arduino_provider:
            raise ValueError("Arduino Provider must be loaded")

    def stop(self):
        super().stop()
        self.raspilot.command_executor.unregister_command(FlightModeCommand.NAME, self.__mode_change_handle)

    def start(self):
        self.__mode_change_handle = self.raspilot.command_executor.register_command(
            FlightModeCommand.NAME,
            FlightModeCommandHandler(self.raspilot.flight_control)
        )
        return True

    def _notify_loop(self):
        while self._run:
            # TODO
            time.sleep(0.5)
