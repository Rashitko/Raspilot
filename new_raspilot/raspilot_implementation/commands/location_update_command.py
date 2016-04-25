from new_raspilot.core.commands.command import BaseCommand, BaseCommandHandler


class LocationUpdateCommand(BaseCommand):
    NAME = 'location.update'

    def __init__(self, latitude, longitude, accuracy):
        super().__init__(LocationUpdateCommand.NAME, self.__create_data(latitude, longitude, accuracy))

    @staticmethod
    def __create_data(latitude, longitude, accuracy):
        return {'latitude': latitude, 'longitude': longitude, 'accuracy': accuracy}


class LocationUpdateCommandHandler(BaseCommandHandler):
    def __init__(self, provider):
        super().__init__()
        self.__location_provider = provider

    def run_action(self, command):
        from new_raspilot.modules.location_provider import Location
        self.__location_provider.location = Location.create_from_command(command)
        self.logger.debug("New location set. {}".format(self.__location_provider.location))
        pass
