from new_raspilot.raspilot_framework.base_system_state_recorder import BaseSystemStateRecorder
from new_raspilot.raspilot_implementation.commands.telemetry_update_command import TelemetryUpdateCommand
from new_raspilot.raspilot_implementation.providers.orientation_provider import RaspilotOrientationProvider


class RaspilotSystemStateRecorder(BaseSystemStateRecorder):
    def __init__(self, silent=False):
        super().__init__(silent)
        self.__orientation_provider = None

    def initialize(self, raspilot):
        super().initialize(raspilot)
        self.__orientation_provider = self.raspilot.get_module(RaspilotOrientationProvider)

    def record_state(self):
        state = self.__capture_state()
        self.raspilot.flight_control.send_message(TelemetryUpdateCommand.create_from_system_state(state).serialize())

    def __capture_state(self):
        orientation = self.__orientation_provider.current_orientation().as_json() if self.__orientation_provider else None
        return {'orientation': orientation}
