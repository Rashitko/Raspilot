from up.commands.command import BaseCommand, BaseCommandHandler


class FlightModeCommand(BaseCommand):
    NAME = 'flight_controller.flight_mode'

    MODE_RATE = 'Rate'
    MODE_FBW = 'FBW'
    MODE_RTH = 'RTH'
    MODE_NOT_AVAILABLE = 'Not Available'

    def __init__(self, mode):
        super().__init__(self.NAME, self.__create_data(mode))

    @staticmethod
    def __create_data(mode):
        return {'flightMode': mode, 'isRequest': False}


class FlightModeCommandHandler(BaseCommandHandler):
    def __init__(self, flight_control):
        super().__init__()
        self.__mode = FlightModeCommand.MODE_NOT_AVAILABLE
        self.__flight_control = flight_control

    def run_action(self, command):
        print(command.data)
        if command.data['isRequest']:
            self.__send_current_mode()
        elif command.data['flightMode']:
            self.mode = command.data['flightMode']
            self.__send_current_mode()

    def __send_current_mode(self):
        command = FlightModeCommand(self.mode)
        self.__flight_control.send_message(command.serialize())

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, value):
        self.__mode = value
