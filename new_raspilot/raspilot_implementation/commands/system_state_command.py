from new_raspilot.raspilot_framework.commands.command import Command


class SystemStateCommand(Command):
    NAME = 'system_state'

    def __init__(self, utilization):
        super().__init__(SystemStateCommand.NAME, self.__create_data(utilization))

    @staticmethod
    def __create_data(utilization):
        data = {'utilization': utilization}
        return data
