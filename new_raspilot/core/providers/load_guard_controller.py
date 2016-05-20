import time

from new_raspilot.core.base_system_state_recorder import BaseSystemStateRecorder
from new_raspilot.core.base_thread_module import BaseThreadModule


class LoadGuardController(BaseThreadModule):
    def __init__(self, load_guard, delay=0.1):
        super().__init__()
        self.__delay = delay
        self.__load_guard = load_guard

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__load_guard.initialize(raspilot)

    def _notify_loop(self):
        while self._run:
            try:
                self.__load_guard.record_state()
            except Exception as e:
                self.logger.critical("Error occurred checking system load. Error was {}".format(e))
            time.sleep(self.__delay)

    @property
    def load_guard(self):
        return self.__load_guard


class BaseLoadGuardStateRecorder(BaseSystemStateRecorder):
    pass
