class FlightController:
    def __init__(self):
        self.__raspilot = None
        self.__started = False
        self.__stopped = True

    def initialize(self):
        pass

    def on_start(self):
        """
        Called by the Raspilot, starts the provider. Subclasses should override start method instead of this one.
        :return: returns nothing
        """
        self.__started = self.start()
        return self.__started

    def start(self):
        if self.__raspilot is None:
            raise ValueError("Raspilot must be set prior start")
        return False

    def on_stop(self):
        """
        Called by the Raspilot, starts the provider. Subclasses should override start method instead of this one.
        :return: returns nothing
        """
        self.__stopped = self.stop()
        return self.__stopped

    def stop(self):
        return True

    @property
    def raspilot(self):
        return self.__raspilot

    @raspilot.setter
    def raspilot(self, value):
        self.__raspilot = value
