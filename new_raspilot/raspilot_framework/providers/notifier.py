import time

from new_raspilot.raspilot_framework.base_thread_module import BaseThreadModule


class TelemetryController(BaseThreadModule):
    def __init__(self, state_recorder):
        super().__init__()
        self.__state_recorder = state_recorder

    def _notify_loop(self):
        while self._run:
            try:
                self.__state_recorder.record_state()
            except Exception as e:
                self.logger.critical("Telemetry transmission failed. Error was {}".format(e))
            time.sleep(0.1)
