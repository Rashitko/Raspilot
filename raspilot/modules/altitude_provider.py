from up.base_started_module import BaseStartedModule
from raspilot.modules.arduino_provider import ArduinoProvider

from raspilot.commands.altitude_change_command import AltitudeChangeCommand, \
    AltitudeChangeCommandHandler


class AltitudeProvider(BaseStartedModule):
    def __init__(self):
        super().__init__()
        self.__altitude = None
        self.__arduino_provider = None
        self.__altitude_change_handle = None

    def _execute_start(self):
        self.__altitude_change_handle = self.up.command_executor.register_command(AltitudeChangeCommand.NAME,
                                                                                        AltitudeChangeCommandHandler(
                                                                                            self))
        self.__arduino_provider = self.up.get_module(ArduinoProvider)
        if self.arduino_provider is None:
            raise ValueError("Arduino Provider not found")
        return True

    def _execute_stop(self):
        self.up.command_executor.unregister_command(AltitudeChangeCommand.NAME, self.__altitude_change_handle)

    def load(self):
        return True

    @property
    def altitude(self):
        return self.__altitude

    @altitude.setter
    def altitude(self, value):
        if value != self.altitude:
            self.arduino_provider.set_altitude(value)
        self.__altitude = value

    @property
    def arduino_provider(self) -> ArduinoProvider:
        return self.__arduino_provider
