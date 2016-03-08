from raspilot.black_box import BlackBox


class RaspilotBlackBox(BlackBox):
    """
    Custom implementation of the Black Box, which sends the relevant data via HTTP to the server API endpoint.
    """
    def record(self):
        super().record()
        # TODO: Implement sending HTTP requests with relevant data
