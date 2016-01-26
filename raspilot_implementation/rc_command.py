class RCChannelValues:
    CHANNELS_MAP = {'ailerons': 1, 'elevator': 2, 'throttle': 3, 'rudder': 4, 'aux': 5}

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
