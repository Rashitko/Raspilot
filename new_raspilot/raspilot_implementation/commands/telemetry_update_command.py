import uuid

from new_raspilot.core.commands.command import BaseCommand


class TelemetryUpdateCommand(BaseCommand):
    NAME = 'telemetry.update'

    def __init__(self, data):
        super().__init__(TelemetryUpdateCommand.NAME, data)
        self.id = str(uuid.uuid1())

    @classmethod
    def create_from_system_state(cls, system_state):
        data = {'orientation': system_state.get('orientation', None), 'location': system_state.get('location', None),
                'flightControllerStatus': system_state.get('flightControllerStatus', None)}
        c = TelemetryUpdateCommand(data)
        return c
