from new_raspilot.core.commands.command import BaseCommandHandler
from new_raspilot.core.providers.base_rx_provider import BaseRXProvider
from new_raspilot.raspilot_implementation.commands.rx_update_command import RXUpdateCommand


class RaspilotRXProvider(BaseRXProvider):
    def get_channels(self):
        return [self.__ailerons, self.__elevator, self.__throttle, self.__rudder]

    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__ailerons = None
        self.__elevator = None
        self.__throttle = None
        self.__rudder = None

    def _execute_initialization(self):
        self.raspilot.command_executor.register_command(RXUpdateCommand.NAME, RXUpdateCommandHandler(self))

    def _execute_start(self):
        return True

    def set_rx(self, ailerons, elevator, throttle, rudder):
        self.__ailerons = ailerons
        self.__elevator = elevator
        self.__throttle = throttle
        self.__rudder = rudder


class RXUpdateCommandHandler(BaseCommandHandler):
    def __init__(self, provider):
        super().__init__()
        self.__provider = provider

    def run_action(self, command):
        self.rx_provider.set_rx(command.ailerons, command.elevator, command.throttle, command.rudder)

    @property
    def rx_provider(self):
        return self.__provider
