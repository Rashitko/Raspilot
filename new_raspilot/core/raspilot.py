from twisted.internet import reactor

from new_raspilot.core.base_started_module import BaseStartedModule
from new_raspilot.core.base_system_state_recorder import BaseSystemStateRecorder
from new_raspilot.core.commands.command_executor import CommandExecutor
from new_raspilot.core.commands.command_receiver import CommandReceiver
from new_raspilot.core.providers.black_box_controller import BlackBoxController
from new_raspilot.core.providers.flight_control_provider import BaseFlightControlProvider
from new_raspilot.core.providers.load_guard_controller import LoadGuardController, BaseLoadGuardStateRecorder
from new_raspilot.core.providers.orientation_provider import BaseOrientationProvider
from new_raspilot.core.providers.telemetry_controller import BaseTelemetryStateRecorder, TelemetryController
from new_raspilot.core.utils.raspilot_logger import RaspilotLogger


class Raspilot:
    def __init__(self, modules, recorders):
        self.__logger = RaspilotLogger.get_logger()
        self.__modules = modules
        self.__started_modules = []
        self.__command_receiver = CommandReceiver()
        self.__command_executor = CommandExecutor()
        self.__orientation_provider = None
        self.__flight_control_provider = None
        self.__load_guard = None
        for module in self.__modules:
            if issubclass(type(module), BaseStartedModule):
                self.__started_modules.append(module)
            if issubclass(type(module), CommandReceiver):
                self.__command_receiver = module
                self.__logger.debug("Custom Command Receiver set")
            if issubclass(type(module), CommandExecutor):
                self.__command_executor = module
                self.__logger.debug("Custom Command Executor set")
            if issubclass(type(module), BaseOrientationProvider):
                self.__orientation_provider = module
                self.__logger.debug("Custom Orientation Provider set")
            if issubclass(type(module), BaseFlightControlProvider):
                self.__flight_control_provider = module
                self.__logger.debug("Custom Flight Control Provider set")
            if issubclass(type(module), LoadGuardController):
                self.__load_guard = module
                self.__logger.debug("Custom Load Guard set")
        for recorder in recorders:
            if issubclass(type(recorder), BaseTelemetryStateRecorder):
                self.__started_modules.append(TelemetryController(recorder))
                self.__logger.debug("Telemetry Controller loaded")
            if issubclass(type(recorder), BaseTelemetryStateRecorder):
                self.__started_modules.append(BlackBoxController(recorder))
                self.__logger.debug("Black Box Controller loaded")
            if issubclass(type(recorder), BaseLoadGuardStateRecorder):
                self.__started_modules.append(LoadGuardController(recorder))
                self.__logger.debug("Load Guard Controller loaded")

    def initialize(self):
        for module in self.__modules:
            if module:
                module.initialize(self)
        for module in self.__started_modules:
            if module:
                module.initialize(self)

    def run(self):
        for module in self.__started_modules:
            if module:
                module.start()
        self.__logger.debug("Running Twisted reactor")
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
    def flight_control(self) -> BaseFlightControlProvider:
        return self.__flight_control_provider

    @property
    def load_guard(self) -> LoadGuardController:
        return self.__load_guard


class RaspilotBuilder:
    def __init__(self):
        self.__custom_providers = []
        self.__command_receiver = CommandReceiver()
        self.__command_executor = CommandExecutor()
        self.__orientation_provider = None
        self.__location_provider = None
        self.__black_box = None
        self.__telemetry = None
        self.__telemetry_enabled = False
        self.__flight_control_provider = None
        self.__load_guard = None

    def add_custom_provider(self, provider):
        self.__custom_providers.append(provider)
        return self

    def with_command(self, name, handler):
        self.__command_executor.register_command(name, handler)
        return self

    def with_orientation_provider(self, provider):
        self.__orientation_provider = provider
        return self

    def with_location_provider(self, provider):
        self.__location_provider = provider
        return self

    def with_blackbox(self, blackbox):
        self.__black_box = blackbox
        return self

    def with_telemetry(self, telemetry):
        self.__telemetry = telemetry
        return self

    def with_flight_control_provider(self, flight_control):
        self.__flight_control_provider = flight_control
        return self

    def with_load_guard(self, load_guard):
        self.__load_guard = load_guard
        return self

    def build(self):
        """
        Build Raspilot instance with specified configuration
        :rtype Raspilot
        """
        self.__validate()
        return Raspilot(self)

    def __validate(self):
        if not self.orientation_provider:
            raise ValueError("Orientation Provider must be set")
        if not self.__location_provider:
            raise ValueError("Location Provider must be set")
        if not self.blackbox:
            raise ValueError("BlackBox must be set")

    @property
    def custom_providers(self) -> list:
        return self.__custom_providers

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
    def location_provider(self):
        return self.__location_provider

    @property
    def blackbox(self) -> BaseSystemStateRecorder:
        return self.__black_box

    @property
    def telemetry(self) -> BaseSystemStateRecorder:
        return self.__telemetry

    @property
    def flight_control(self) -> BaseFlightControlProvider:
        return self.__flight_control_provider

    @property
    def load_guard(self) -> BaseLoadGuardStateRecorder:
        return self.__load_guard
