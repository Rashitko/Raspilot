from new_raspilot.core.base_started_module import BaseStartedModule


class BaseFlightController(BaseStartedModule):
    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__rx_provider = None
        self.__orientation_provider = None

    def _execute_initialization(self):
        self.__rx_provider = self.raspilot.rx_provider
        if not self.__rx_provider:
            raise ValueError("Flight Controller cannot be used without RX Provider")
        self.__orientation_provider = self.raspilot.orientation_provider
        if not self.__orientation_provider:
            raise ValueError("Flight Controller cannot be used without Orientation Provider")

    def load(self):
        return True
