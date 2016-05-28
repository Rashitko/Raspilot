import psutil

from new_raspilot.core.providers.load_guard_controller import BaseLoadGuardStateRecorder
from new_raspilot.modules.android_provider import AndroidProvider
from new_raspilot.raspilot_implementation.commands.panic_command import PanicCommand
from new_raspilot.raspilot_implementation.commands.system_state_command import SystemStateCommand


class RaspilotLoadGuardStateRecorder(BaseLoadGuardStateRecorder):
    STATE_WAS_PANIC = 2
    STATE_WAS_OK = 3

    def __init__(self, panic_limit=85, calm_down_limit=70, panic_delay=100, calm_down_delay=20):
        super().__init__()
        self.__panic_limit = panic_limit
        self.__calm_down_limit = calm_down_limit
        self.__panic_delay = panic_delay
        self.__calm_down_delay = calm_down_delay
        self.__state = RaspilotLoadGuardStateRecorder.STATE_WAS_OK
        self.__android_provider = None
        self.__utilization = None

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__android_provider = self.raspilot.get_module(AndroidProvider)
        if not self.__android_provider:
            self._log_warning("AndroidProvider NOT found")

    def record_state(self):
        self.__utilization = psutil.cpu_percent()
        if self.__utilization > self.__panic_limit and self.__state is not RaspilotLoadGuardStateRecorder.STATE_WAS_PANIC:
            self.logger.warn('PANIC mode entered, UTILIZATION {}'.format(self.__utilization))
            self.__state = RaspilotLoadGuardStateRecorder.STATE_WAS_PANIC
            self._panic()
        elif self.__utilization < self.__calm_down_limit and self.__state is not RaspilotLoadGuardStateRecorder.STATE_WAS_OK:
            self.logger.info('CALMED DOWN mode entered, UTILIZATION {}'.format(self.__utilization))
            self.__state = RaspilotLoadGuardStateRecorder.STATE_WAS_OK
            self._calm_down()

        if self.android_provider:
            command = SystemStateCommand(self.__utilization)
            self.android_provider.send_data(command.serialize())

    def _panic(self):
        if self.android_provider:
            command = PanicCommand(True, self.__panic_delay, self.__utilization)
            self.android_provider.send_data(command.serialize())
            # TODO: Send message to Arduino

    def _calm_down(self):
        if self.android_provider:
            command = PanicCommand(False, self.__calm_down_delay, self.__utilization)
            self.android_provider.send_data(command.serialize())
            # TODO: Send message to Arduino

    @property
    def android_provider(self):
        return self.__android_provider

    @property
    def utilization(self):
        return self.__utilization
