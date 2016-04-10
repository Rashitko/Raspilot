from threading import Thread

from twisted.internet import reactor

from new_raspilot.raspilot_framework.base_system_state_recorder import BaseSystemStateRecorder
from new_raspilot.raspilot_framework.commands.command_executor import CommandExecutor
from new_raspilot.raspilot_framework.commands.command_receiver import CommandReceiver
from new_raspilot.raspilot_framework.providers.black_box_controller import BlackBoxController
from new_raspilot.raspilot_framework.providers.notifier import TelemetryController
from new_raspilot.raspilot_framework.providers.orientation_provider import OrientationProvider
from new_raspilot.raspilot_framework.utils.raspilot_logger import RaspilotLogger


class Raspilot:
    def __init__(self, builder):
        """
        :param builder: RaspilotBuilder used to configure this instance
        :type builder: RaspilotBuilder
        """
        self.__modules = []
        self.__started_modules = []
        self.__logger = RaspilotLogger.get_logger()

        self.__command_executor = builder.command_executor
        self.__modules.append(self.__command_executor)

        self.__command_receiver = builder.command_receiver
        self.__modules.append(self.__command_executor)

        self.__orientation_provider = builder.orientation_provider
        self.__started_modules.append(self.__orientation_provider)

        self.__black_box_controller = BlackBoxController(builder.blackbox)
        self.__started_modules.append(self.__black_box_controller)

        self.__flight_control_provider = builder.fligh_control
        self.__started_modules.append(self.__flight_control_provider)

        for provider in builder.custom_providers:
            self.__started_modules.append(provider)

        if builder.telemetry_enabled:
            self.__telemetry_controller = TelemetryController(builder.telemetry)
            self.__started_modules.append(self.__telemetry_controller)
        else:
            self.__telemetry_controller = None
            self.__logger.warning("Telemetry is disabled")

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

    @property
    def command_receiver(self):
        return self.__command_receiver

    @property
    def command_executor(self):
        return self.__command_executor

    @property
    def orientation_provider(self):
        return self.__orientation_provider

    @property
    def flight_control(self):
        return self.__flight_control_provider


class RaspilotBuilder:
    def __init__(self):
        self.__custom_providers = []
        self.__command_receiver = CommandReceiver()
        self.__command_executor = CommandExecutor()
        self.__orientation_provider = None
        self.__black_box = None
        self.__telemetry = None
        self.__telemetry_enabled = False
        self.__flight_control_provider = None

    def add_custom_provider(self, provider):
        self.__custom_providers.append(provider)
        return self

    def with_command(self, name, handler):
        self.__command_executor.register_command(name, handler)
        return self

    def with_orientation_provider(self, provider):
        self.__orientation_provider = provider
        return self

    def with_blackbox(self, blackbox):
        self.__black_box = blackbox
        return self

    def with_telemetry(self, telemetry):
        self.__telemetry = telemetry
        self.__telemetry_enabled = telemetry is not None
        return self

    def enable_telemetry(self, enabled):
        self.__telemetry_enabled = enabled
        if not enabled:
            self.__telemetry = None
        return self

    def with_flight_control_provider(self, flight_control):
        self.__flight_control_provider = flight_control
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
        if not self.blackbox:
            raise ValueError("BlackBox must be set")
        if not self.telemetry_enabled and self.telemetry is None:
            raise ValueError("If telemetry is enabled it must be set")

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
    def orientation_provider(self) -> OrientationProvider:
        return self.__orientation_provider

    @property
    def blackbox(self) -> BaseSystemStateRecorder:
        return self.__black_box

    @property
    def telemetry(self) -> BaseSystemStateRecorder:
        return self.__telemetry

    @property
    def telemetry_enabled(self):
        return self.__telemetry_enabled

    @property
    def fligh_control(self):
        return self.__flight_control_provider
