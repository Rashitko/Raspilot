import logging

from raspilot.black_box import BlackBox
from raspilot_implementation.commands.system_state_command import SystemStateCommand

from obsolete.raspilot_implementation.providers.android_provider import AndroidProvider


class RaspilotBlackBox(BlackBox):
    """
    Custom implementation of the Black Box, which sends the relevant data via HTTP to the server API endpoint.
    """

    CACHE_SIZE = 50

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger('raspilot.log')
        self.__cached_data = []

    def record(self, raspilot):
        """
        Caches the black box records and then send them via HTTP to the server. Beside this, sends the relevant data
        (utilization) to the in-flight Android device.
        :param raspilot:
        :return:
        """
        super().record(raspilot)
        recorded_data = raspilot.notifier.create_message
        self.cached_data.append(recorded_data)
        if len(self.cached_data) >= RaspilotBlackBox.CACHE_SIZE:
            self.__logger.debug('Sending data')
            if self.__send_data(raspilot, self.__cached_data.copy()):
                self.__logger.info('BlackBox update transmission successful')
                self.__cached_data = []
            else:
                self.__logger.error('BlackBox update transmission failed')
        android_provider = raspilot.named_provider(AndroidProvider.NAME)
        if android_provider:
            utilization = raspilot.alarmist.utilization
            command = SystemStateCommand.create_command(utilization)
            android_provider.send_command(command)

    def __send_data(self, raspilot, data):
        """
        Sends the data via HTTP to the server.
        :param raspilot: raspilot instance
        :param data: data to be sent
        :return: True if transmission was successful, False otherwise
        """
        self.__logger.debug('Transmitting BlackBox update. Size: {}'.format(len(data)))
        # TODO: Implement sending HTTP requests with relevant data
        return True

    @property
    def cached_data(self):
        return self.__cached_data
