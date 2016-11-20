from new_raspilot.core.commands.command import BaseCommand, BaseCommandHandler


class PIDTuningsCommand(BaseCommand):
    NAME = 'pid.tunings'


class PIDTuningsCommandHandler(BaseCommandHandler):
    def run_action(self, command):
        print(command.data)


class PIDSyncCommand(BaseCommand):
    NAME = 'pid.sync'


class PIDSyncCommandHandler(BaseCommandHandler):
    def run_action(self, command):
        print(command.data)
