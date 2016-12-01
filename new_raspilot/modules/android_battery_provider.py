from new_raspilot.core.base_started_module import BaseStartedModule
from new_raspilot.raspilot_implementation.commands.android_battery_command import AndroidBatteryCommand, \
    AndroidBatteryCommandHandler


class AndroidBatteryProvider(BaseStartedModule):
    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__battery_level = None
        self.__battery_level_handle = None

    def _execute_start(self):
        self.__battery_level_handle = self.raspilot.command_executor.register_command(
            AndroidBatteryCommand.NAME, AndroidBatteryCommandHandler(self)
        )
        return True

    def _execute_stop(self):
        self.raspilot.command_executor.unregister_command(AndroidBatteryCommand.NAME, self.__battery_level_handle)

    def get_battery_level(self):
        return self.battery_level

    def load(self):
        return True

    @property
    def battery_level(self):
        return self.__battery_level

    @battery_level.setter
    def battery_level(self, value):
        self.__battery_level = value
