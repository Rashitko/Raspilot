from abc import abstractmethod

from new_raspilot.raspilot_framework.base_module import BaseModule


class BaseSystemStateRecorder(BaseModule):
    @abstractmethod
    def record_state(self):
        pass
