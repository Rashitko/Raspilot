import logging
from threading import Thread

from twisted.internet import reactor
from twisted.web import client

from raspilot.raspilot import Raspilot, RaspilotBuilder
from raspilot_implementation.disocvery.discovery_service import DiscoveryService


class RaspilotImpl(Raspilot):
    """
    Custom implementation of the Raspilot. Adds the discovery service for the Android devices.
    """

    MODE_BLACK_BOX = 1

    def __init__(self, raspilot_builder):
        super().__init__(raspilot_builder)
        self.__logger = logging.getLogger('raspilot.log')
        self.__discovery_service = DiscoveryService(raspilot_builder.discovery_port, raspilot_builder.reply_port, self)
        self.__mode = raspilot_builder.mode

    def _after_start(self):
        """
        Starts the discovery service after calling the super
        :return:
        """
        super()._after_start()
        Thread(target=reactor.run, args=(False,)).start()
        if self.__mode != RaspilotImpl.MODE_BLACK_BOX:
            self.__discovery_service.enable_discovery()

    def stop(self):
        reactor.callFromThread(reactor.stop)
        super().stop()

    def _after_stop(self):
        """
        Stops the discovery service after calling the super
        :return:
        """
        super()._after_stop()
        if self.__mode != RaspilotImpl.MODE_BLACK_BOX:
            self.__discovery_service.disable_discovery()


class RaspilotImplBuilder(RaspilotBuilder):
    def __init__(self, discovery_port, reply_port, mode=RaspilotImpl.MODE_BLACK_BOX):
        super().__init__()
        self.__discovery_port = discovery_port
        self.__reply_port = reply_port
        self.__mode = mode

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

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, value):
        self.__mode = value

    def build(self):
        return RaspilotImpl(self)
