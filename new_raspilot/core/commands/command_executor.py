import uuid

from new_raspilot.core.base_module import BaseModule
from new_raspilot.raspilot_implementation.commands.altitude_change_command import AltitudeChangeCommand


class CommandExecutor(BaseModule):
    def __init__(self):
        super().__init__()
        self.__handlers = {}

    def register_command(self, name, handler):
        handle = uuid.uuid1()
        if self.__handlers.get(name, None) is None:
            self.__handlers[name] = {}
        self.__handlers[name][handle] = handler
        self._log_debug("Handler {} for {} registered".format(handle, name))

    def unregister_command(self, name, handle):
        if self.__handlers.get(name, None) is not None:
            if handle in self.__handlers[name]:
                self._log_debug("Handler {} for {} unregistered".format(handle, name))
                return self.__handlers.pop(handle, None)
        return None

    def remote_handler(self, command_name):
        self.__handlers[command_name] = None

    def execute_command(self, command):
        handlers = self.__handlers.get(command.name, None)
        if handlers:
            for handler in handlers.values():
                if not command.name == AltitudeChangeCommand.NAME:
                    self._log_debug("Executing command {}".format(command.name))
                handler.run_action(command)
        else:
            self._log_warning("Unknown command {} received".format(command.name))
