class BaseProvider:
    """
    Base provider class, which all other provider should extend. Defines the basic methods, which are common for
    all providers.
    """

    def __init__(self, config):
        """
        Constructs a new 'BaseProvider'
        :param config: configuration for this provider
        :return: returns nothing
        """
        if config is None:
            raise ValueError("Config must be set")
        self.__raspilot_ = None

    def initialize(self):
        """
        Called once, during Raspilot initialization. Before this call, self.__raspilot(raspilot_instance) is called.
        :return: returns nothing
        """
        pass

    def start(self):
        """
        Called after initializations, can be called multiple times.
        :return: returns True, if start was successful, False otherwise
        """
        return False

    def stop(self):
        """
        Called when the provider should stop, usually when exiting the application.
        :return: returns True, if start was successful, False otherwise
        """
        return True

    @property
    def __raspilot(self):
        return self.__raspilot_

    @__raspilot.setter
    def __raspilot(self, value):
        self.__raspilot_ = value


class BaseProviderConfig:
    """
    Base class for providers config, all other providers config should extend this class.
    """

    def __init__(self):
        pass

