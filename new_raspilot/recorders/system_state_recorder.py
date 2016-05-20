from new_raspilot.core.base_system_state_recorder import BaseSystemStateRecorder
from new_raspilot.core.providers.black_box_controller import BaseBlackBoxStateRecorder
from new_raspilot.core.providers.telemetry_controller import BaseTelemetryStateRecorder
from new_raspilot.modules.android_battery_provider import AndroidBatteryProvider
from new_raspilot.modules.location_provider import RaspilotLocationProvider
from new_raspilot.modules.orientation_provider import RaspilotOrientationProvider
from new_raspilot.raspilot_implementation.commands.telemetry_update_command import TelemetryUpdateCommand


class RaspilotBlackBoxRecorder(BaseBlackBoxStateRecorder):
    def __init__(self, silent=False):
        super().__init__(silent)
        self.__recorder = RaspilotSystemStateRecorder(silent)

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__recorder.initialize(raspilot)

    def record_state(self):
        self.__recorder.record_state()


class RaspilotTelemetryRecorder(BaseTelemetryStateRecorder):
    def __init__(self, silent=False):
        super().__init__(silent)
        self.__recorder = RaspilotSystemStateRecorder(silent)

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__recorder.initialize(raspilot)

    def record_state(self):
        self.__recorder.record_state()


class RaspilotSystemStateRecorder(BaseSystemStateRecorder):
    def __init__(self, silent=False):
        super().__init__(silent)
        self.__orientation_provider = None
        self.__location_provider = None
        self.__android_battery_provider = None
        self.__load_guard = None

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__orientation_provider = self.raspilot.get_module(RaspilotOrientationProvider)
        self.__location_provider = self.raspilot.get_module(RaspilotLocationProvider)
        self.__android_battery_provider = self.raspilot.get_module(AndroidBatteryProvider)
        self.__load_guard = self.raspilot.load_guard_controller.load_guard

    def record_state(self):
        state = self.__capture_state()
        self.raspilot.flight_control.send_message(TelemetryUpdateCommand.create_from_system_state(state).serialize())

    def __capture_state(self):
        if self.__orientation_provider and self.__orientation_provider.current_orientation():
            orientation = self.__orientation_provider.current_orientation().as_json()
        else:
            orientation = None
        if self.__location_provider and self.__location_provider.get_location():
            location = self.__location_provider.get_location().as_json()
        else:
            location = None
        flight_controller_status = {'cpu': None, 'batteryLevel': None}
        if self.__android_battery_provider and self.__android_battery_provider.get_battery_level():
            flight_controller_status['batteryLevel'] = self.__android_battery_provider.get_battery_level()
        else:
            flight_controller_status['batteryLevel'] = None
        if self.__load_guard:
            utilization = self.__load_guard.utilization
            flight_controller_status['cpu'] = utilization
        else:
            flight_controller_status['cpu'] = None

        return {'orientation': orientation, 'location': location, 'flightControllerStatus': flight_controller_status}

    def load(self):
        return False
