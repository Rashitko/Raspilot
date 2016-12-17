from up.base_system_state_recorder import BaseSystemStateRecorder
from up.providers.black_box_controller import BaseBlackBoxStateRecorder
from up.providers.telemetry_controller import BaseTelemetryStateRecorder

from raspilot.commands.telemetry_frequency_command import TelemetryFrequencyCommand, \
    TelemetryFrequencyCommandHandler
from raspilot.commands.telemetry_update_command import TelemetryUpdateCommand
from raspilot.modules.altitude_provider import AltitudeProvider
from raspilot.modules.android_battery_provider import AndroidBatteryProvider
from raspilot.modules.android_provider import AndroidProvider
from raspilot.modules.arduino_provider import ArduinoProvider
from raspilot.modules.location_provider import RaspilotLocationProvider
from raspilot.modules.orientation_provider import RaspilotOrientationProvider
from raspilot.modules.rx_provider import RaspilotRXProvider


class RaspilotBlackBoxRecorder(BaseBlackBoxStateRecorder):
    def __init__(self, silent=False):
        super().__init__(silent)
        self.__recorder = RaspilotSystemStateRecorder(silent)
        self.__telemetry_freq_handle = None

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__recorder.initialize(raspilot)

    def record_state(self):
        # self.__recorder.record_state()
        pass


class RaspilotTelemetryRecorder(BaseTelemetryStateRecorder):
    def __init__(self, silent=False):
        super().__init__(silent)
        self.__recorder = RaspilotSystemStateRecorder(silent, True)

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__recorder.initialize(raspilot)
        self.__telemetry_freq_handle = self.up.command_executor.register_command(
            TelemetryFrequencyCommand.NAME,
            TelemetryFrequencyCommandHandler(raspilot.telemetry_controller, raspilot.flight_control)
        )

    def record_state(self):
        self.__recorder.record_state()


class RaspilotSystemStateRecorder(BaseSystemStateRecorder):
    def __init__(self, silent=False, transmit=False):
        super().__init__(silent)
        self.__orientation_provider = None
        self.__location_provider = None
        self.__altitude_provider = None
        self.__android_battery_provider = None
        self.__load_guard = None
        self.__rx_provider = None
        self.__arduino_provider = None
        self.__android_provider = None
        self.__transmit = transmit

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__orientation_provider = self.up.get_module(RaspilotOrientationProvider)
        self.__location_provider = self.up.get_module(RaspilotLocationProvider)
        self.__android_battery_provider = self.up.get_module(AndroidBatteryProvider)
        self.__rx_provider = self.up.get_module(RaspilotRXProvider)
        self.__load_guard = self.up.load_guard_controller.load_guard
        self.__altitude_provider = self.up.get_module(AltitudeProvider)
        self.__arduino_provider = self.up.get_module(ArduinoProvider)
        self.__android_provider = self.up.get_module(AndroidProvider)

    def record_state(self):
        state = self.__capture_state()
        if self.__transmit:
            self.up.flight_control.send_message(
                TelemetryUpdateCommand.create_from_system_state(state).serialize())

    def __capture_state(self):
        if self.__orientation_provider and self.__orientation_provider.current_orientation():
            orientation = self.__orientation_provider.current_orientation().as_json()
        else:
            orientation = None

        if self.__location_provider and self.__location_provider.get_location():
            location = self.__location_provider.get_location().as_json()
        else:
            location = None

        if self.__rx_provider and self.__rx_provider.get_channels():
            channels = self.__rx_provider.get_channels()
        else:
            channels = None

        if self.__altitude_provider:
            altitude = self.__altitude_provider.altitude
        else:
            altitude = None

        flight_controller_status = {'cpu': None, 'batteryLevel': None, 'rx': channels}
        if self.__android_battery_provider and self.__android_battery_provider.get_battery_level():
            flight_controller_status['batteryLevel'] = self.__android_battery_provider.get_battery_level()
        else:
            flight_controller_status['batteryLevel'] = None

        devices_status = {
            'android': self.__android_provider.is_connected,
            'arduino': self.__arduino_provider.is_connected
        }

        if self.__load_guard:
            utilization = self.__load_guard.utilization
            flight_controller_status['cpu'] = utilization
        else:
            flight_controller_status['cpu'] = None

        return {'orientation': orientation, 'location': location,
                'flightControllerStatus': flight_controller_status, 'altitude': altitude,
                'devicesStatus': devices_status}

    def load(self):
        return False
