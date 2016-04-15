from new_raspilot.raspilot_framework.commands.command import Command


class PanicCommand(Command):
    NAME = 'panic'

    def __init__(self, in_panic, delay, utilization):
        super().__init__(PanicCommand.NAME, self.__create_data(in_panic, delay, utilization))

    @staticmethod
    def __create_data(in_panic, delay, utilization):
        return {'delay': delay, 'panic': in_panic, 'utilization': utilization}
