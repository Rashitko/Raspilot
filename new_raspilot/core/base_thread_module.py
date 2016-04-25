from abc import abstractmethod
from threading import Thread

from new_raspilot.core.base_started_module import BaseStartedModule


class BaseThreadModule(BaseStartedModule):
    def __init__(self):
        super().__init__()
        self.__thread = None

    def _execute_initialization(self):
        self.__thread = Thread(target=self._notify_loop)

    def _execute_start(self):
        self.__run = True
        self.__thread.start()
        return True

    def _execute_stop(self):
        self.__run = False

    @abstractmethod
    def _notify_loop(self):
        pass

    @property
    def _run(self):
        return self.__run
