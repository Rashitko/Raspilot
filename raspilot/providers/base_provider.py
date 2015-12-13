class BaseProvider(object):
    """
    Base provider class, which all other provider should extend. Defines the basic methods, which are common for
    all providers.
    """

    def __init__(self, config, name=None):
        """
        Constructs a new 'BaseProvider'
        :param config: configuration for this provider
        :return: returns nothing
        """
        self.__raspilot = None
        if name:
            self.__name = name
        else:
            self.__name = self.__class__.name

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
        if not self.__raspilot:
            raise ValueError("Raspilot must be set prior to start")
        return False

    def stop(self):
        """
        Called when the provider should stop, usually when exiting the application.
        :return: returns True, if start was successful, False otherwise
        """
        return True

    @property
    def raspilot(self):
        return self.__raspilot

    @raspilot.setter
    def raspilot(self, value):
        self.__raspilot = value

    @property
    def name(self):
        return self.__name


class BaseProviderConfig:
    """
    Base class for providers config, all other providers config should extend this class.
    """

    def __init__(self):
        pass

