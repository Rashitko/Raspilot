import logging
import time
from threading import Thread

from raspilot.providers.base_provider import BaseProvider, BaseProviderConfig

DEFAULT_DELAY = 200 / 1000


class BlackBoxController(BaseProvider):
    """
    Controller of the Black box, which should be used to save relevant data for additional analysis.
    """

    def __init__(self, config):
        super().__init__(config)
        self.__delay = config.delay
        self.__black_box = config.black_box
        self.__logger = logging.getLogger('raspilot.log')
        self.__record = True
        self.__recording_thread = None

    def start(self):
        """
        Creates and starts the recording loop thread.
        :return: True if start was successful
        """
        if self.__recording_thread is None:
            self.__recording_thread = Thread(target=self.__recording_loop, name='BLACK_BOX_CONTROLLER_THREAD')
            self.__recording_thread.start()
        return True

    def __recording_loop(self):
        """
        Notifies the black box to record the current status and sleeps for the specified amount of time
        :return: returns nothing
        """
        self.__logger.debug('Starting BlackBox with delay interval {}ms'.format(self.__delay * 1000))
        while self.__record:
            self.__black_box.record(self.raspilot)
            time.sleep(self.__delay)
        self.__logger.info('BlackBox recordings stopped.')
        self.__recording_thread = None

    def stop(self):
        """
        Stops the recording
        :return: True
        """
        self.__record = False
        return True


class BlackBoxControllerConfig(BaseProviderConfig):
    def __init__(self):
        super().__init__()
        self.__black_box = BlackBox()
        self.__delay = DEFAULT_DELAY

    @property
    def black_box(self):
        return self.__black_box

    @black_box.setter
    def black_box(self, value):
        self.__black_box = value

    @property
    def delay(self):
        return self.__delay

    @delay.setter
    def delay(self, value):
        self.__delay = value


class BlackBox:
    """
    Base BlackBox class, which does nothing. Subclasses should override the record method and should persist the
    relevant data in this method.
    """

    def record(self, raspilot):
        """
        Called periodically by the BlackBoxController. Relevant data should be persisted for additional analysis.
        :param raspilot raspilot instance
        :return: returns nothing
        """
        pass
