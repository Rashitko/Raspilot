from new_raspilot.core.commands.command import BaseCommand


class SystemStateCommand(BaseCommand):
    NAME = 'system_state'

    def __init__(self, utilization):
        super().__init__(SystemStateCommand.NAME, self.__create_data(utilization))

    @staticmethod
    def __create_data(utilization):
        return {'utilization': utilization}
