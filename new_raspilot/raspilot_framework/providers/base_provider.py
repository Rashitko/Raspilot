from abc import abstractmethod

from new_raspilot.raspilot_framework.base_component import BaseModule
from new_raspilot.raspilot_framework.utils.raspilot_logger import RaspilotLogger


class BaseProvider(BaseModule):
    def __init__(self, config=None, silent=False):
        super().__init__(silent)
        self.__config = config
        self.__logger = RaspilotLogger.get_logger()
        self.__started = False

    def initialize(self, raspilot):
        """
        Called once, use for one time initialization
        :param raspilot: raspilot instance
        :return: None
        """
        super().initialize(raspilot)
        self._log_debug("Initializing {}".format(self.class_name))
        self._execute_initialization()

    @abstractmethod
    def _execute_initialization(self):
        """
        Subclasses must override this method. Initialize the provider here.
        :return: None
        """
        return None

    def start(self):
        """
        Called by the Raspilot after initialization, used to start the provider.
        :return: True if the provided started successfully, False otherwise
        """
        try:
            self._log_debug("Starting {}".format(self.class_name))
            self.__started = self._execute_start()
            start_result = 'successfully' if self.__started else 'failed'
            self._log_info("{} start {}".format(self.class_name, start_result))
        except Exception as e:
            self.logger.error("Error during the start of {} occurred. Error was {}".format(self.class_name, e))
        return self.__started

    @abstractmethod
    def _execute_start(self):
        """
        Subclasses must override this method. Start the provider here.
        :return: True if the provided started successfully, False otherwise
        """
        return False

    def stop(self):
        """
        Called after start, used to stop the provider.
        :return: None
        """
        self._log_debug("Stopping {}".format(self.class_name))
        self.__started = False
        self._execute_stop()

    @abstractmethod
    def _execute_stop(self):
        """
        Subclasses must override this method. Stop the provider here.
        :return: None
        """
        pass

    @property
    def config(self):
        return self.__config
