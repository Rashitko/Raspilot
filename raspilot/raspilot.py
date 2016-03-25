import logging
from threading import Event

from raspilot.alarmist import AlarmistConfig, Alarmist
from raspilot.black_box import BlackBoxController, BlackBoxControllerConfig
from raspilot.commands.commands_executor import CommandsExecutor, CommandExecutionError
from raspilot.providers.orientation_provider import OrientationProvider
from raspilot.providers.websockets_provider import WebsocketsProvider
from raspilot.starter import Starter


def nop():
    pass


class Raspilot:
    """
    The Raspilot itself.
    """

    def __init__(self, raspilot_builder):
        """
        Constructs a new 'Raspilot' from the builder.
        :param raspilot_builder: builder to construct Raspilot from
        :return: returns nothing
        """
        self.__logger = logging.getLogger('raspilot.log')
        self.__rx_provider = raspilot_builder.rx_provider
        self.__websockets_provider = raspilot_builder.websockets_provider
        self.__orientation_provider = raspilot_builder.orientation_provider
        self.__gps_provider = raspilot_builder.gps_provider
        self.__servo_controller = raspilot_builder.servo_controller
        self.__black_box_controller = raspilot_builder.black_box_controller or BlackBoxController(
            BlackBoxControllerConfig())
        self.__alarmist = raspilot_builder.alarmist or Alarmist(AlarmistConfig())
        self.__stop_self_event = Event()
        self.__init_complete_event = Event()
        self.__commands_executor = raspilot_builder.commands_executor
        if not self.__commands_executor:
            self.__commands_executor = CommandsExecutor()
        self.__commands_executor.raspilot = self
        self.__custom_providers = raspilot_builder.custom_providers
        self.__notifier = raspilot_builder.notifier
        self.__flight_controller = raspilot_builder.flight_controller
        self.__starter = raspilot_builder.starter

        self.__initialized_providers = []
        self.__started_providers = []
        self.__skipped_providers = []
        self.__failed_providers = []

        self.__providers = [(self.__alarmist, 'Alarmist not available'),
                            (self.__black_box_controller, 'Black Box controller not available'),
                            (self.__rx_provider, 'RX input not available'),
                            (self.__websockets_provider, 'Websocket input not available'),
                            (self.__orientation_provider, 'Orientation input not available'),
                            (self.__gps_provider, 'GPS input not available'),
                            (self.__servo_controller, 'Servo controller not available'),
                            (self.__flight_controller, 'Flight controller not available'),
                            (self.__notifier, 'Notifier not available')]

        self.__init_messages = []
        self.__init_providers()

    def __init_providers(self):
        """
        Initializes all providers
        :return: returns nothing
        """
        for (provider, message) in self.__providers:
            self.__init_provider(provider, message, self.__initialized_providers)
        self.__init_custom_providers(self.__initialized_providers)
        self.__logger.info("Initialized providers: {}".format(self.__initialized_providers))

    def __init_provider(self, provider, message, initialized_providers):
        """
        Initialize the given provider. If the provider is None, provided message is logged as warning.
        :param provider: provider to initialize
        :param message: message to log if provider is None
        :return:
        """
        if provider is not None:
            initialized_providers.append(provider.__class__.__name__)
            provider.raspilot = self
            provider.initialize()
        else:
            self.__logger.warning(message)

    def __init_custom_providers(self, initialized_providers):
        """
        Initializes the custom providers if any.
        :return: returns nothing
        """
        for provider in self.__custom_providers:
            self.__init_provider(provider, '', initialized_providers)

    def start(self):
        """
        Starts the Raspilot with available providers and blocks till the Raspilot is running.
        :return: return nothing
        """

        self.__logger.info('Starting Raspilot...')
        self.__start_providers()

        self.__logger.info(
            'Initialization complete.')
        self.__logger.info('Started providers:{}\n\tSkipped providers:{}'
                           '\n\tProviders which fail to start:{}'.format(self.__started_providers,
                                                                         self.__skipped_providers,
                                                                         self.__failed_providers))
        self.__init_complete_event.set()
        self._after_start()
        self.__stop_self_event.wait()

    def __start_providers(self):
        for (provider, _) in self.__providers:
            self.__start_provider(provider)
        self._start_custom_providers()

    def __start_provider(self, provider):
        if provider is not None:
            provider_name = provider.__class__.__name__
            if self.__starter.should_start(provider, self):
                if not provider.on_start():
                    self.__failed_providers.append(provider_name)
                else:
                    self.__started_providers.append(provider_name)
            else:
                self.__skipped_providers.append(provider_name)

    def _after_start(self):
        """
        Callback after start of the Raspilot.
        :return: returns nothing
        """
        if self.__failed_providers:
            self.__logger.critical(
                'Some providers failed to start. Not started providers are {}'.format(self.__failed_providers))
        else:
            self.__logger.info('All providers started successfully')

    def _start_custom_providers(self):
        """
        Starts custom providers, if any.
        :return: returns nothing
        """
        for provider in self.__custom_providers:
            self.__start_provider(provider)

    def stop(self):
        """
        Stops all available providers, notifier, black box and then stops self.
        :return: return nothing
        """
        self.__logger.info('Stopping Raspilot')
        stopped = []
        for (provider, _) in self.__providers:
            self.__stop_provider(provider, stopped)
        if self.__commands_executor:
            self.__commands_executor.stop()
        self.__stop_custom_providers(stopped)
        self.__logger.info("Stopped providers: {}".format(stopped))
        self._after_stop()
        self.__stop_self_event.set()

    def __stop_provider(self, provider, stopped):
        if provider is not None and self.__starter.should_start(provider, self):
            stopped.append(provider.__class__.__name__)
            provider.on_stop()

    def _after_stop(self):
        """
        Callback after stop of the Raspilot
        :return: returns nothing
        """
        pass

    def __stop_custom_providers(self, stopped):
        """
        Stops custom providers, if any.
        :return: returns nothing
        """
        for provider in self.__custom_providers:
            self.__stop_provider(provider, stopped)

    def wait_for_init_complete(self):
        """
        Blocks until initialization is complete.
        :return: returns nothing
        """
        self.__init_complete_event.wait()

    def add_command_handler(self, command_handler):
        """
        Adds the command handler to the commands executor. Upon receiving of the command with corresponding
        command name, the action will be executed. If handler is already added, it is replaced.
        :param command_handler: command handler to add
        :return: returns nothing
        """
        self.__commands_executor.add_command_handler(command_handler)

    def remove_command_handler(self, command_handler):
        """
        Removes the command handler. If command handler was not added previously, nothing is changed.
        :param command_handler: command handler to remove
        :return: return command handler or None, if command handler was not bound previously
        """
        return self.__commands_executor.remove_command_handler(command_handler)

    def execute_command(self, command_name, command_id, data, request=False, response=None):
        """
        If command is bound executes the action, otherwise the default_action is executed.
        :param command_name: command which should be executed, must be set
        :param command_id: id of the command, must be set
        :param data: additional data for the command, must be set
        :param request: flag, whether the command is a request and should be responded to
        :param response: response object, containing additional information about the request execution, can be None
        :return: returns nothing
        """
        try:
            if command_name is None:
                raise CommandExecutionError(ValueError("command_name not set"))
            if data is None:
                raise CommandExecutionError(ValueError("data not set"))
            if command_id is None:
                raise CommandExecutionError(ValueError("command id not set"))
            self.__commands_executor.execute_command(command_name, data, command_id, request, response)
        except CommandExecutionError:
            if request and command_id:
                self.__commands_executor.notify_command_failed(command_name, data, command_id, response)

    def send_command(self, command):
        """
        Sends the command via.
        :param command: command to be sent
        :return: returns nothing
        """
        self.__commands_executor.send_command(command)

    def named_provider(self, provider_name):
        """
        If provider with given name is available, then it is returned. Otherwise None is returned.
        :param provider_name: name of the desired provider
        :return: provider with given name or None
        """
        for provider in self.__custom_providers:
            if provider.name == provider_name:
                return provider
        return None

    @property
    def websocket_provider(self):
        return self.__websockets_provider

    @property
    def orientation_provider(self):
        return self.__orientation_provider

    @property
    def commands_executor(self):
        return self.__commands_executor

    @property
    def gps_provider(self):
        return self.__gps_provider

    @property
    def rx_provider(self):
        return self.__rx_provider

    @property
    def alarmist(self):
        return self.__alarmist

    @property
    def notifier(self):
        return self.__notifier


class RaspilotBuilder:
    """
    Builder for the Raspilot.
    """

    def __init__(self):
        """
        Constructs a new 'RaspilotBuilder' with all providers set as None.
        :return: returns nothing
        """
        self.__alarmist = None
        self.__websockets_provider = WebsocketsProvider
        self.__rx_provider = None
        self.__orientation_provider = OrientationProvider
        self.__gps_provider = None
        self.__servo_controller = None
        self.__commands_executor = None
        self.__custom_providers = []
        self.__notifier = None
        self.__flight_controller = None
        self.__black_box_controller = None
        self.__starter = Starter()

    def add_custom_provider(self, provider):
        """
        Adds a custom provider. Provider should extend raspilot.providers.BaseProvider.
        :param provider: provider which extends raspilot.providers.BaseProvider.
        :return: returns nothing.
        """
        self.__custom_providers.append(provider)

    @property
    def websockets_provider(self):
        return self.__websockets_provider

    @websockets_provider.setter
    def websockets_provider(self, value):
        self.__websockets_provider = value

    @property
    def rx_provider(self):
        return self.__rx_provider

    @rx_provider.setter
    def rx_provider(self, value):
        self.__rx_provider = value

    @property
    def orientation_provider(self):
        return self.__orientation_provider

    @orientation_provider.setter
    def orientation_provider(self, value):
        self.__orientation_provider = value

    @property
    def gps_provider(self):
        return self.__gps_provider

    @gps_provider.setter
    def gps_provider(self, value):
        self.__gps_provider = value

    @property
    def servo_controller(self):
        return self.__servo_controller

    @servo_controller.setter
    def servo_controller(self, value):
        self.__servo_controller = value

    @property
    def commands_executor(self):
        return self.__commands_executor

    @commands_executor.setter
    def commands_executor(self, value):
        self.__commands_executor = value

    @property
    def custom_providers(self):
        return self.__custom_providers

    @property
    def notifier(self):
        return self.__notifier

    @notifier.setter
    def notifier(self, value):
        self.__notifier = value

    @property
    def flight_controller(self):
        return self.__flight_controller

    @flight_controller.setter
    def flight_controller(self, value):
        self.__flight_controller = value

    @property
    def black_box_controller(self):
        return self.__black_box_controller

    @black_box_controller.setter
    def black_box_controller(self, value):
        self.__black_box_controller = value

    @property
    def alarmist(self):
        return self.__alarmist

    @alarmist.setter
    def alarmist(self, value):
        self.__alarmist = value

    @property
    def starter(self):
        return self.__starter

    @starter.setter
    def starter(self, value):
        self.__starter = value

    def build(self):
        """
        Builds Raspilot from previously set information.
        :return: a new Raspilot instance created from data in this builder
        """
        return Raspilot(self)
