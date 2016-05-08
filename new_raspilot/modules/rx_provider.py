from new_raspilot.core.providers.base_rx_provider import BaseRXProvider


class RaspilotRXProvider(BaseRXProvider):
    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__rx = RXValues(1500, 1500, 1000, 1500)

    def get_channels(self):
        return self.__rx

    def _execute_start(self):
        return True

    def set_channels(self, channels):
        self.__rx = channels

    @property
    def ailerons(self):
        return self.__rx[0]

    @property
    def elevator(self):
        return self.__rx[1]


class RXValues:
    """
    Will be used as a wrapper around RX PWM values read by Arduino. Currently returns mocked data.
    """

    def __init__(self, ailerons, elevator, throttle, rudder):
        self.__channels = (ailerons, elevator, throttle, rudder)

    def __str__(self):
        return str({'AIL': self.__channels[0], 'ELE': self.__channels[1], 'THR': self.__channels[2],
                    'RUD': self.__channels[3]})

    def __getitem__(self, item):
        return self.__channels[item]
