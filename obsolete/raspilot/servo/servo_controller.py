from obsolete.raspilot.providers import BaseProvider, BaseProviderConfig

DEFAULT_MAX_PWM = 2000
DEFAULT_MIN_PWM = 1000
AILERONS_DEFAULT_CHANNEL = 1
AILERONS_KEY = 'ailerons'
ELEVATOR_DEFAULT_CHANNEL = 2
ELEVATOR_KEY = 'elevator'
THROTTLE_DEFAULT_CHANNEL = 3
THROTTLE_KEY = 'throttle'
RUDDER_DEFAULT_CHANNEL = 4
RUDDER_KEY = 'rudder'
DEFAULT_CHANNEL_MAP = {AILERONS_KEY: AILERONS_DEFAULT_CHANNEL, ELEVATOR_KEY: ELEVATOR_DEFAULT_CHANNEL,
                       THROTTLE_KEY: THROTTLE_DEFAULT_CHANNEL, RUDDER_KEY: RUDDER_DEFAULT_CHANNEL}


class ServoController(BaseProvider):
    def __init__(self, config):
        BaseProvider.__init__(self, config)


class ServoControllerConfig(BaseProviderConfig):
    def __init__(self):
        BaseProviderConfig.__init__(self)
        self.__min_pwm = DEFAULT_MIN_PWM
        self.__max_pwm = DEFAULT_MAX_PWM
        self.channels_map = DEFAULT_CHANNEL_MAP

    @property
    def min_pwm(self):
        return self.__min_pwm

    @min_pwm.setter
    def min_pwm(self, value):
        self.__min_pwm = value

    @property
    def max_pwm(self):
        return self.__max_pwm

    @max_pwm.setter
    def max_pwm(self, value):
        self.__max_pwm = value

    @property
    def channels_map(self):
        return self.channels_map

    @channels_map.setter
    def channels_map(self, value):
        self.__channels_map = value
