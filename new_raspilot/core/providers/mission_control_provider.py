from abc import abstractmethod

from new_raspilot.core.base_started_module import BaseStartedModule


class BaseMissionControlProvider(BaseStartedModule):
    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)

    @abstractmethod
    def send_message(self, data):
        pass

    def load(self):
        return True
