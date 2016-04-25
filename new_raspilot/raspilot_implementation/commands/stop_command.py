import os
import signal

from new_raspilot.core.commands.command import BaseCommand, BaseCommandHandler


class StopCommand(BaseCommand):
    NAME = "system.stop"

    def __init__(self):
        super().__init__(StopCommand.NAME)
        self.name = StopCommand.NAME


class StopCommandHandler(BaseCommandHandler):
    def run_action(self, command):
        self.logger.info("Stop command received. Stopping Raspilot")
        os.kill(os.getpid(), signal.SIGINT)
