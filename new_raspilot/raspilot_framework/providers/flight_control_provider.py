from abc import abstractmethod

from new_raspilot.raspilot_framework.base_started_module import BaseStartedModule


class BaseFlightControlProvider(BaseStartedModule):
    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)

    @abstractmethod
    def send_message(self, data):
        pass
