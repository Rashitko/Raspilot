from abc import abstractmethod

from new_raspilot.core.base_started_module import BaseStartedModule


class BaseOrientationProvider(BaseStartedModule):
    @abstractmethod
    def current_orientation(self):
        pass

    def load(self):
        return True
