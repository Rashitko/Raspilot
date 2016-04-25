from obsolete.raspilot_implementation.commands.command import RaspilotCommand


class PanicCommand(RaspilotCommand):
    """
    Custom command used when handling panic mode. Contains the delay with which should the Android device send the
    orientation data. Should be sent to the on-board device.
    """

    NAME = 'panic'
    """
    Name of the command
    """

    def __init__(self, panic, delay, utilization):
        super().__init__(PanicCommand.NAME, {'delay': delay, 'panic': panic, 'utilization': utilization}, False, None,
                         target=RaspilotCommand.TARGET_ANDROID)
        self.__delay = delay
        self.__panic = panic
        self.__utilization = utilization

    @property
    def delay(self):
        return self.__delay

    @property
    def panic(self):
        return self.__panic

    @property
    def utilization(self):
        return self.__utilization
