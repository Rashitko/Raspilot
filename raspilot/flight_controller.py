class FlightController:
    def __init__(self):
        self.__raspilot = None

    def initialize(self):
        pass

    def start(self):
        if self.__raspilot is None:
            raise ValueError("Raspilot must be set prior start")
        return False

    def stop(self):
        pass

    @property
    def raspilot(self):
        return self.__raspilot

    @raspilot.setter
    def raspilot(self, value):
        self.__raspilot = value
