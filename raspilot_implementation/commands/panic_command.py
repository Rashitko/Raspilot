from raspilot_implementation.commands.command import RaspilotCommand


class PanicCommand(RaspilotCommand):
    """
    Custom command used when handling panic mode. Contains the delay with which should the Android device send the
    orientation data. Should be sent to the on-board device.
    """

    NAME = 'panic'
    """
    Name of the command
    """

    def __init__(self, delay):
        super().__init__(PanicCommand.NAME, {'delay': delay}, False, None, target=RaspilotCommand.TARGET_ANDROID)
        self.__delay = delay

    @property
    def delay(self):
        return self.__delay
