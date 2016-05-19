import os
import signal

from new_raspilot.core.commands.command import BaseCommand, BaseCommandHandler


class BaseStopCommand(BaseCommand):
    NAME = "system.stop"

    def __init__(self):
        super().__init__(BaseStopCommand.NAME)
        self.name = BaseStopCommand.NAME


class BaseStopCommandHandler(BaseCommandHandler):
    def run_action(self, command):
        self.logger.info("Stop command received. Stopping Raspilot")
        os.kill(os.getpid(), signal.SIGINT)
