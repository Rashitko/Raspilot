from new_raspilot.core.commands.command import BaseCommandHandler
from new_raspilot.core.providers.orientation_provider import BaseOrientationProvider
from new_raspilot.raspilot_implementation.commands.orientation_command import OrientationCommand


class RaspilotOrientationProvider(BaseOrientationProvider):
    COUNT_DOWN_LIMIT_IN_SEC = 5

    def __init__(self):
        super().__init__()
        self.__orientation = None

    def _execute_initialization(self):
        super()._execute_initialization()
        self.raspilot.command_executor.register_command(OrientationCommand.NAME,
                                                        OrientationUpdateCommandHandler(self))

    def _execute_start(self):
        return True

    def set_orientation(self, orientation):
        self.__orientation = orientation

    def current_orientation(self):
        return self.__orientation

    @property
    def roll(self):
        if self.__orientation:
            return self.__orientation.roll
        return 0

    @property
    def pitch(self):
        if self.__orientation:
            return self.__orientation.pitch
        return 0


class Orientation:
    def __init__(self, roll, pitch, azimuth):
        self.__roll = roll
        self.__pitch = pitch
        self.__azimuth = azimuth

    def as_json(self):
        return {'roll': self.roll, 'pitch': self.pitch, 'azimuth': self.__azimuth}

    @property
    def roll(self):
        return self.__roll

    @property
    def pitch(self):
        return self.__pitch

    @property
    def azimuth(self):
        return self.__azimuth


class OrientationUpdateCommandHandler(BaseCommandHandler):
    def __init__(self, orientation_provider):
        super().__init__()
        self.__orientation_provider = orientation_provider

    def run_action(self, command):
        orientation = Orientation(command.roll, command.pitch, command.yaw)
        self.orientation_provider.set_orientation(orientation)

    @property
    def orientation_provider(self):
        return self.__orientation_provider
