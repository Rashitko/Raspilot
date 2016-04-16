from abc import abstractmethod

from new_raspilot.raspilot_framework.base_started_module import BaseStartedModule


class BaseLocationProvider(BaseStartedModule):
    @abstractmethod
    def get_location(self):
        pass
