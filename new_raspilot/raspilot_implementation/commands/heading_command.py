from new_raspilot.core.commands.command import BaseCommand, BaseCommandHandler


class HeadingCommand(BaseCommand):
    NAME = 'flight_controller.heading'

    def __init__(self):
        super().__init__(HeadingCommand.NAME)


class HeadingCommandHandler(BaseCommandHandler):
    SET_MODE_REQUIRED = 'required'
    SET_MODE_ACTUAL = 'actual'

    def __init__(self, provider):
        super().__init__()
        self.__heading_provider = provider

    def run_action(self, command):
        if command is None:
            return None
        heading = command.data.get('heading', None)
        mode = command.data.get('mode', None)
        if mode == self.SET_MODE_REQUIRED:
            self.heading_provider.required_heading = heading
        elif mode == self.SET_MODE_ACTUAL:
            self.heading_provider.actual_heading = heading
        else:
            self.logger.error("SET MODE '%s' not supported" % mode)

    @property
    def heading_provider(self):
        return self.__heading_provider
