from new_raspilot.core.providers.base_rx_provider import BaseRXProvider


class RaspilotRXProvider(BaseRXProvider):
    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        # FIXME: remove the mock of the RXValues
        self.__rx = RXValues()

    def get_channels(self):
        return self.__rx

    def _execute_start(self):
        return True

    def set_channels(self, channels):
        self.__rx = channels


class RXValues:
    """
    Will be used as a wrapper around RX PWM values read by Arduino. Currently returns mocked data.
    """

    def __init__(self):
        self.__channels = (1500, 1500, 1000, 1500)
