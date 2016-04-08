from abc import abstractmethod

from new_raspilot.raspilot_framework.base_started_module import BaseStartedModule


class OrientationProvider(BaseStartedModule):
    @abstractmethod
    def current_orientation(self):
        pass
