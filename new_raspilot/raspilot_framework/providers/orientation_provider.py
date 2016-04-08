from abc import abstractmethod

from new_raspilot.raspilot_framework.providers.base_provider import BaseProvider


class OrientationProvider(BaseProvider):
    @abstractmethod
    def current_orientation(self):
        pass
