import time
from abc import abstractmethod
from threading import Thread

from new_raspilot.raspilot_framework.base_module import BaseModule
from new_raspilot.raspilot_framework.base_started_module import BaseStartedModule


class BlackBoxController(BaseStartedModule):
    def __init__(self, black_box):
        super().__init__()
        self.__thread = None
        self.__run = False
        self.__black_box = black_box

    def _execute_initialization(self):
        self.__black_box.initialize(self.raspilot)
        self.__thread = Thread(target=self.__notify_loop, daemon=True)

    def _execute_stop(self):
        self.__run = False

    def _execute_start(self):
        self.__run = True
        self.__thread.start()
        return True

    def __notify_loop(self):
        while self.__run:
            try:
                self.__black_box.record_state()
            except Exception as e:
                self.logger.critical("Error occurred during BlackBox data recording. Error was {}".format(e))
            time.sleep(0.5)


class BaseBlackBox(BaseModule):
    @abstractmethod
    def record_state(self):
        pass
