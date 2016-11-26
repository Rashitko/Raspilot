from new_raspilot.core.base_module import BaseModule
from new_raspilot.raspilot_implementation.commands.altitude_change_command import AltitudeChangeCommand


class CommandReceiver(BaseModule):
    def execute_command(self, command):
        if not command.name == AltitudeChangeCommand.NAME:
            self.logger.debug("Received command {}".format(command.name))
        self.raspilot.command_executor.execute_command(command)
