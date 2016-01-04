from raspilot_implementation.commands.command import RaspilotCommand


class SpeakCommand(RaspilotCommand):

    NAME = 'speak'

    def __init__(self, texts):
        super().__init__(SpeakCommand.NAME, {'texts': texts}, False, None)
