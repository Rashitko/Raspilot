from raspilot.commands.command import Command


class SpeakCommand(Command):

    NAME = 'speak'

    def __init__(self, texts):
        super().__init__(SpeakCommand.NAME, {'texts': texts}, False, None)
