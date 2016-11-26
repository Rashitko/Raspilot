from new_raspilot.core.base_module import BaseModule
from new_raspilot.raspilot_implementation.commands.altitude_change_command import AltitudeChangeCommand


class CommandExecutor(BaseModule):
    def __init__(self):
        super().__init__()
        self.__handlers = {}

    def register_command(self, name, handler):
        self.__handlers[name] = handler
        self._log_debug("Handler for {} registered".format(name))

    def unregister_command(self, name):
        self.__handlers[name] = None
        self._log_debug("Handler for {} unregistered".format(name))

    def remote_handler(self, command_name):
        self.__handlers[command_name] = None

    def execute_command(self, command):
        handler = self.__handlers.get(command.name, None)
        if handler:
            if not command.name == AltitudeChangeCommand.NAME:
                self._log_debug("Executing command {}".format(command.name))
            handler.run_action(command)
        else:
            self._log_warning("Unknown command {} received".format(command.name))
