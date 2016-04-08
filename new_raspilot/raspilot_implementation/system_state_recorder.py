from new_raspilot.raspilot_framework.base_system_state_recorder import BaseSystemStateRecorder


class RaspilotSystemStateRecorder(BaseSystemStateRecorder):

    def record_state(self):
        self.logger.info("Recording state")
