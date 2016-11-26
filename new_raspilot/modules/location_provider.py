from new_raspilot.core.providers.location_provider import BaseLocationProvider
from new_raspilot.core.utils.raspilot_logger import RaspilotLogger
from new_raspilot.modules.arduino_provider import ArduinoProvider
from new_raspilot.raspilot_implementation.commands.location_update_command import LocationUpdateCommand, \
    LocationUpdateCommandHandler


class RaspilotLocationProvider(BaseLocationProvider):
    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__location = None
        self.__arduino_provider = None

    def get_location(self):
        return self.location

    def _execute_start(self):
        self.raspilot.command_executor.register_command(LocationUpdateCommand.NAME, LocationUpdateCommandHandler(self))
        self.__arduino_provider = self.raspilot.get_module(ArduinoProvider)
        return True

    def _execute_stop(self):
        self.raspilot.command_executor.unregister_command(LocationUpdateCommand.NAME)

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, value):
        self.__location = value
        self.arduino_provider.set_location(value.latitude, value.longitude)

    @property
    def arduino_provider(self):
        return self.__arduino_provider


class Location:
    def __init__(self):
        self.__latitude = None
        self.__longitude = None
        self.__accuracy = None
        self.__logger = RaspilotLogger.get_logger()

    @property
    def latitude(self):
        return self.__latitude

    @latitude.setter
    def latitude(self, value):
        self.__latitude = value

    @property
    def longitude(self):
        return self.__longitude

    @longitude.setter
    def longitude(self, value):
        self.__longitude = value

    @property
    def accuracy(self):
        return self.__accuracy

    @accuracy.setter
    def accuracy(self, value):
        self.__accuracy = value

    def as_json(self):
        return {'latitude': self.latitude, 'longitude': self.longitude, 'accuracy': self.accuracy}

    def __str__(self, *args, **kwargs):
        return str(self.as_json())

    @classmethod
    def create_from_command(cls, command):
        l = Location()
        if command is None:
            l.__logger.error("Cannot create from None")
            return None
        if not command.name == LocationUpdateCommand.NAME:
            l.__logger.error("Can create location from {} command".format(command.name))
            return None
        try:
            l.accuracy = command.data.get('accuracy', None)
            l.latitude = command.data.get('latitude', None)
            l.longitude = command.data.get('longitude', None)
            return l
        except Exception as e:
            l.__logger.critical(
                "An error occurred during creating location from command. Error was {}\n\tData were {}".format(e,
                                                                                                               command.data))
        return None
