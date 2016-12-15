from up.base_started_module import BaseStartedModule

from raspilot.commands.heading_command import HeadingCommand, HeadingCommandHandler
from raspilot.modules.arduino_provider import ArduinoProvider


class HeadingProvider(BaseStartedModule):
    def __init__(self):
        super().__init__()
        self.__actual_heading = None
        self.__required_heading = None
        self.__arduino_provider = None
        self.__command_handle = None

    def _execute_start(self):
        self.__command_handle = self.up.command_executor.register_command(HeadingCommand.NAME,
                                                                                HeadingCommandHandler(self))
        self.__arduino_provider = self.up.get_module(ArduinoProvider)
        if self.arduino_provider is None:
            raise ValueError("Arduino Provider not found")
        return True

    def _execute_stop(self):
        self.up.command_executor.unregister_command(HeadingCommand.NAME, self.__command_handle)
        pass

    def load(self):
        return True

    @property
    def actual_heading(self):
        return self.__actual_heading

    @actual_heading.setter
    def actual_heading(self, value):
        self.__actual_heading = value
        self.arduino_provider.set_actual_heading(self.actual_heading)

    @property
    def required_heading(self):
        return self.__required_heading

    @required_heading.setter
    def required_heading(self, value):
        self.__required_heading = value
        self.arduino_provider.set_required_heading(self.required_heading)

    @property
    def arduino_provider(self) -> ArduinoProvider:
        return self.__arduino_provider
