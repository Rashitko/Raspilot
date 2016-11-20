from new_raspilot.core.commands.command import BaseCommand, BaseCommandHandler


class TelemetryFrequencyCommand(BaseCommand):
    NAME = 'telemetry.frequency'

    def __init__(self, frequency):
        super().__init__(self.NAME, self.__create_data(frequency))

    @staticmethod
    def __create_data(frequency):
        return {'frequency': frequency, 'isRequest': False}


class TelemetryFrequencyCommandHandler(BaseCommandHandler):
    def __init__(self, controller, flight_control):
        super().__init__()
        self.__controller = controller
        self.__flight_control = flight_control

    @property
    def controller(self):
        return self.__controller

    def run_action(self, command):
        if command.data['isRequest']:
            self.__send_current_delay()
        elif command.data['frequency']:
            self.controller.delay = command.data['frequency']
            self.__send_current_delay()

    def __send_current_delay(self):
        delay = self.controller.delay
        command = TelemetryFrequencyCommand(delay)
        self.__flight_control.send_message(command.serialize())
