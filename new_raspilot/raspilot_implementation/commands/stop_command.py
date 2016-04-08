import os
import signal

from new_raspilot.raspilot_framework.commands.command import Command, CommandHandler


class StopCommand(Command):
    NAME = "system.stop"

    def __init__(self):
        super().__init__()
        self.name = StopCommand.NAME


class StopCommandHandler(CommandHandler):
    def run_action(self, command):
        self.logger.info("Stop command received. Stopping Raspilot")
        os.kill(os.getpid(), signal.SIGINT)
