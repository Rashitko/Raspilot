from new_raspilot.core.base_module import BaseModule


class CommandReceiver(BaseModule):
    def execute_command(self, command):
        self.logger.debug("Received command {}".format(command.name))
        self.raspilot.command_executor.execute_command(command)
