from new_raspilot.core.flight_controller.base_flight_controller import BaseFlightController


class RaspilotFlightController(BaseFlightController):
    def _execute_start(self):
        return True
