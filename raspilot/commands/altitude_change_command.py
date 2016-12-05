from up.commands.command import BaseCommand, BaseCommandHandler


class AltitudeChangeCommand(BaseCommand):
    NAME = 'altitude.change'

    def __init__(self):
        super().__init__(AltitudeChangeCommand.NAME)


class AltitudeChangeCommandHandler(BaseCommandHandler):
    def __init__(self, provider):
        super().__init__()
        self.__location_provider = provider

    def run_action(self, command):
        if command.data['altitude'] is not None:
            self.__location_provider.altitude = command.data['altitude']
