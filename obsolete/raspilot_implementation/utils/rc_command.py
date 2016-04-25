class RCChannelValues:
    """
    Wrapper class for PWM values read by Arduino from the radio RX.
    """

    CHANNELS_MAP = {'ailerons': 0, 'elevator': 1, 'throttle': 2, 'rudder': 3, 'aux': 4}
    """
    Default mapping of channels to their indices in the channels tuple
    """

    def __init__(self, channels):
        self.__channels = channels

    @property
    def channels_count(self):
        if self.__channels:
            return len(self.__channels)
        else:
            return 0

    @property
    def channels(self):
        return self.__channels

    @channels.setter
    def channels(self, value):
        self.__channels = value

    @property
    def ailerons(self):
        return self.__channels[RCChannelValues.CHANNELS_MAP['ailerons']]

    @property
    def elevator(self):
        return self.__channels[RCChannelValues.CHANNELS_MAP['elevator']]

    @property
    def throttle(self):
        return self.__channels[RCChannelValues.CHANNELS_MAP['throttle']]

    @property
    def rudder(self):
        return self.__channels[RCChannelValues.CHANNELS_MAP['rudder']]

    @property
    def aux(self):
        return self.__channels[RCChannelValues.CHANNELS_MAP['aux']]
