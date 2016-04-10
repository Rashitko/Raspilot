from new_raspilot.raspilot_framework.base_system_state_recorder import BaseSystemStateRecorder
from new_raspilot.raspilot_implementation.commands.telemetry_update_command import TelemetryUpdateCommand


class RaspilotSystemStateRecorder(BaseSystemStateRecorder):
    def record_state(self):
        state = self.__capture_state()
        self.raspilot.flight_control.send_message(TelemetryUpdateCommand.create_from_system_state(state).serialize())

    def __capture_state(self):
        return {}
