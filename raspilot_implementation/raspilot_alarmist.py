from raspilot.alarmist import Alarmist, AlarmistConfig
from raspilot_implementation.commands.panic_command import PanicCommand

DEFAULT_CALM_DOWN_DELAY = 10

DEFAULT_PANIC_DELAY = 100


class RaspilotAlarmist(Alarmist):
    """
    Custom implementation of the Alarmist. When panic mode is entered, the delay between sending the android device
    orientation is increased as well as the delay of the Arduino's RX readings.
    """

    def __init__(self, config):
        super().__init__(config)
        self.__panic_delay = config.panic_delay
        self.__calm_down_delay = config.calm_down_delay

    def _panic(self, utilization):
        """
        Sends command to the Android and Arduino which increases the delay in the relevant data transmissions
        (orientation data for Android device and RX data for Arduino).
        :param utilization: cpu utilization percentage when panic mode is entered
        :return: returns nothing
        """
        super()._panic(utilization)
        self.raspilot.send_command(PanicCommand(self.__panic_delay))
        # TODO: Send message to Android
        # TODO: Send message to Arduino

    def _calm_down(self, utilization):
        """
        Sends command to the Android and Arduino which sets the delay in the relevant data transmissions
        (orientation data for Android device and RX data for Arduino) to the normal state.
        :param utilization: cpu utilization percentage when calm down mode is entered
        :return: returns nothing
        """
        super()._calm_down(utilization)
        # TODO: Send message to Android
        # TODO: Send message to Arduino


class RaspilotAlarmistConfig(AlarmistConfig):
    """
    Config object for the RaspilotAlarmist.
    """
    def __init__(self):
        super().__init__()
        self.__panic_delay = DEFAULT_PANIC_DELAY
        self.__calm_down_delay = DEFAULT_CALM_DOWN_DELAY

    @property
    def panic_delay(self):
        return self.__panic_delay

    @panic_delay.setter
    def panic_delay(self, value):
        self.__panic_delay = value

    @property
    def calm_down_delay(self):
        return self.__calm_down_delay

    @calm_down_delay.setter
    def calm_down_delay(self, value):
        self.__calm_down_delay = value
