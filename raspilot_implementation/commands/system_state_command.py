from raspilot_implementation.commands.command import RaspilotCommand


class SystemStateCommand(RaspilotCommand):
    NAME = 'system_state'

    def __init__(self, name, data):
        super().__init__(name, data, None, None)

    @classmethod
    def create_command(cls, utilization):
        data = {}
        if utilization:
            data['utilization'] = utilization
        return cls(SystemStateCommand.NAME, data)
