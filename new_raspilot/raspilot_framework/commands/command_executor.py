from new_raspilot.raspilot_framework.base_module import BaseModule


class CommandExecutor(BaseModule):
    def __init__(self):
        super().__init__()
        self.__handlers = {}

    def register_command(self, name, handler):
        self.__handlers[name] = handler

    def remote_handler(self, command_name):
        self.__handlers[command_name] = None

    def execute_command(self, command):
        handler = self.__handlers.get(command.name, None)
        if handler:
            self._log_debug("Executing command {}".format(command.name))
            handler.run_action(command)
        else:
            self._log_warning("Unknown command {} received".format(command.name))
