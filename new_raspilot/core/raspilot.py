from twisted.internet import reactor

from new_raspilot.core.base_started_module import BaseStartedModule
from new_raspilot.core.commands.command_executor import CommandExecutor
from new_raspilot.core.commands.command_receiver import CommandReceiver
from new_raspilot.core.commands.stop_command import BaseStopCommandHandler, BaseStopCommand
from new_raspilot.core.providers.base_rx_provider import BaseRXProvider
from new_raspilot.core.providers.black_box_controller import BlackBoxController
from new_raspilot.core.providers.load_guard_controller import LoadGuardController, BaseLoadGuardStateRecorder
from new_raspilot.core.providers.mission_control_provider import BaseMissionControlProvider
from new_raspilot.core.providers.orientation_provider import BaseOrientationProvider
from new_raspilot.core.providers.telemetry_controller import BaseTelemetryStateRecorder, TelemetryController
from new_raspilot.core.utils.raspilot_logger import RaspilotLogger


class Raspilot:
    def __init__(self, modules, recorders, flight_controller=None):
        self.__logger = RaspilotLogger.get_logger()
        self.__modules = modules
        self.__started_modules = []
        self.__command_receiver = CommandReceiver()
        self.__modules.append(self.__command_receiver)
        self.__command_executor = CommandExecutor()
        self.__modules.append(self.__command_executor)
        self.__flight_controller = flight_controller
        self.__modules.append(self.__flight_controller)
        self.__orientation_provider = None
        self.__flight_control_provider = None
        for module in self.__modules:
            if issubclass(type(module), BaseStartedModule):
                self.__started_modules.append(module)
            if issubclass(type(module), CommandReceiver):
                self.__command_receiver = module
                self.__logger.debug("Command Receiver loaded")
            if issubclass(type(module), CommandExecutor):
                self.__command_executor = module
                self.__logger.debug("Command Executor loaded")
            if issubclass(type(module), BaseOrientationProvider):
                self.__orientation_provider = module
                self.__logger.debug("Orientation Provider loaded")
            if issubclass(type(module), BaseMissionControlProvider):
                self.__flight_control_provider = module
                self.__logger.debug("Flight Control Provider loaded")
            if issubclass(type(module), LoadGuardController):
                self.__logger.debug("Load Guard loaded")
            if issubclass(type(module), BaseRXProvider):
                self._rx_provider = module
                self.__logger.debug("RX Provider loaded")
        for recorder in recorders:
            if issubclass(type(recorder), BaseTelemetryStateRecorder):
                telemetry_controller = TelemetryController(recorder)
                self.__modules.append(telemetry_controller)
                self.__started_modules.append(telemetry_controller)
                self.__logger.debug("Telemetry Controller loaded")
            if issubclass(type(recorder), BaseTelemetryStateRecorder):
                black_box_controller = BlackBoxController(recorder)
                self.__modules.append(black_box_controller)
                self.__started_modules.append(black_box_controller)
                self.__logger.debug("Black Box Controller loaded")
            if issubclass(type(recorder), BaseLoadGuardStateRecorder):
                self.__load_guard_controller = LoadGuardController(recorder)
                self.__modules.append(self.__load_guard_controller)
                self.__started_modules.append(self.__load_guard_controller)
                self.__logger.debug("Load Guard Controller loaded")
        if self.__flight_controller is None:
            self.__logger.info("Flight Controller unavailable")
        self.__register_commands()

    def __register_commands(self):
        self.command_executor.register_command(BaseStopCommand.NAME, BaseStopCommandHandler())

    def initialize(self):
        for module in self.__modules:
            if module:
                module.initialize(self)

    def run(self):
        for module in self.__started_modules:
            if module:
                module.start()
        reactor.run()

    def stop(self):
        for module in self.__started_modules:
            if module:
                module.stop()

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def get_module(self, module_class):
        for module in self.__modules:
            if module.__class__ == module_class:
                return module
        for module in self.__started_modules:
            if module.__class__ == module_class:
                return module
        return None

    @property
    def command_receiver(self) -> CommandReceiver:
        return self.__command_receiver

    @property
    def command_executor(self) -> CommandExecutor:
        return self.__command_executor

    @property
    def orientation_provider(self) -> BaseOrientationProvider:
        return self.__orientation_provider

    @property
    def flight_control(self) -> BaseMissionControlProvider:
        return self.__flight_control_provider

    @property
    def load_guard_controller(self) -> LoadGuardController:
        return self.__load_guard_controller

    @property
    def rx_provider(self) -> BaseRXProvider:
        return self._rx_provider
