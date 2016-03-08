import logging

from raspilot.raspilot import Raspilot, RaspilotBuilder
from raspilot_implementation.disocvery.discovery_service import DiscoveryService


class RaspilotImpl(Raspilot):
    def __init__(self, raspilot_builder):
        super().__init__(raspilot_builder)
        self.__logger = logging.getLogger('raspilot.log')
        self.__discovery_service = DiscoveryService(raspilot_builder.discovery_port, raspilot_builder.reply_port)

    def _after_start(self):
        """
        Starts the discovery service after calling the super
        :return:
        """
        super()._after_start()
        self.__discovery_service.enable_discovery()

    def _after_stop(self):
        """
        Stops the discovery service after calling the super
        :return:
        """
        super()._after_stop()
        self.__discovery_service.disable_discovery()

    def _start_flight_controller(self):
        """
        Starts the flight controller only if the RX provider is available. Otherwise false is returned.
        :return: result of the controller's start, or False if the RX provider is not available
        """
        if self.rx_provider.started:
            return super()._start_flight_controller()
        else:
            self.__logger.warn('RX provider not available, skipping start of the flight controller')
            return False


class RaspilotImplBuilder(RaspilotBuilder):
    def __init__(self, discovery_port, reply_port):
        super().__init__()
        self.__discovery_port = discovery_port
        self.__reply_port = reply_port

    @property
    def discovery_port(self):
        return self.__discovery_port

    @discovery_port.setter
    def discovery_port(self, value):
        self.__discovery_port = value

    @property
    def reply_port(self):
        return self.__reply_port

    @reply_port.setter
    def reply_port(self, value):
        self.__reply_port = value

    def build(self):
        return RaspilotImpl(self)
