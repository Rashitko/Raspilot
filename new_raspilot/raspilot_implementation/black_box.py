from new_raspilot.raspilot_framework.providers.black_box_controller import BaseBlackBox


class RaspilotBlackBox(BaseBlackBox):

    def record_state(self):
        self.logger.info("Recording state")
