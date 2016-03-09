import logging
from threading import Thread

import psutil
import time

from raspilot.providers.base_provider import BaseProvider, BaseProviderConfig

DEFAULT_DELAY = 500 / 1000

DEFAULT_CALM_DOWN_THRESHOLD = 75

DEFAULT_PANIC_THRESHOLD = 85

STATE_WAS_PANIC = 2
STATE_WAS_OK = 3


class Alarmist(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        self.__logger = logging.getLogger('raspilot.log')
        self.__delay = config.delay
        self.__panic_threshold = config.panic_threshold
        self.__calm_down_threshold = config.calm_down_threshold
        self.__control = True
        self.__control_thread = None
        self.__state = STATE_WAS_OK

    def start(self):
        if self.__control_thread is None:
            self.__control_thread = Thread(target=self.__control_loop, name='ALARMIST_THREAD')
            self.__control_thread.start()
        return True

    def __control_loop(self):
        while self.__control:
            utilization = psutil.cpu_percent()
            if utilization > self.__panic_threshold and self.__state is not STATE_WAS_PANIC:
                self.__logger.warn('PANIC MODE, UTILIZATION {}'.format(utilization))
                self.__state = STATE_WAS_PANIC
                self._panic(utilization)
            elif utilization < self.__calm_down_threshold and self.__state is not STATE_WAS_OK:
                self.__logger.warn('CALMED DOWN, UTILIZATION {}'.format(utilization))
                self.__state = STATE_WAS_OK
                self._calm_down(utilization)
            time.sleep(self.__delay)
        self.__control_thread = None

    def stop(self):
        self.__control = False
        return True

    def _panic(self, utilization):
        """
        Called once, when the panic mode is entered. Subclasses should execute operations related to entering panic
        mode.
        :param utilization: cpu utilization percentage when entered panic mode
        :return: returns nothing
        """
        pass

    def _calm_down(self, utilization):
        """
        Called once, when the calm down mode is entered. Subclasses should execute operations related to exiting panic
        mode.
        :param utilization: cpu utilization percentage when entered calm down mode
        :return: returns nothing
        """
        pass


class AlarmistConfig(BaseProviderConfig):
    def __init__(self):
        super().__init__()
        self.__panic_threshold = DEFAULT_PANIC_THRESHOLD
        self.__calm_down_threshold = DEFAULT_CALM_DOWN_THRESHOLD
        self.__delay = DEFAULT_DELAY

    @property
    def panic_threshold(self):
        return self.__panic_threshold

    @panic_threshold.setter
    def panic_threshold(self, value):
        self.__panic_threshold = value

    @property
    def calm_down_threshold(self):
        return self.__calm_down_threshold

    @calm_down_threshold.setter
    def calm_down_threshold(self, value):
        self.__calm_down_threshold = value

    @property
    def delay(self):
        return self.__delay

    @delay.setter
    def delay(self, value):
        self.__delay = value
