import logging

from raspilot.black_box import BlackBox
from raspilot_implementation.commands.system_state_command import SystemStateCommand
from raspilot_implementation.providers.android_provider import AndroidProvider


class RaspilotBlackBox(BlackBox):
    """
    Custom implementation of the Black Box, which sends the relevant data via HTTP to the server API endpoint.
    """

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger('raspilot.log')

    def record(self, raspilot):
        """
        Caches the black box records and then send them via HTTP to the server. Beside this, sends the relevant data
        (utilization) to the in-flight Android device.
        :param raspilot:
        :return:
        """
        super().record(raspilot)
        android_provider = raspilot.named_provider(AndroidProvider.NAME)
        if android_provider:
            utilization = raspilot.alarmist.utilization
            command = SystemStateCommand.create_command(utilization)
            android_provider.send_command(command)

            # TODO: Implement sending HTTP requests with relevant data
