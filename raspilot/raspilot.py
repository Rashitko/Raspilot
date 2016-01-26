import logging
from threading import Event

from raspilot.commands.commands_executor import CommandsExecutor, CommandExecutionError
from raspilot.providers.orientation_provider import OrientationProvider
from raspilot.providers.websockets_provider import WebsocketsProvider
from raspilot_implementation.commands.speak_command import SpeakCommand


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
        self.__stop_self_event = Event()
        self.__init_complete_event = Event()
        self.__commands_executor = raspilot_builder.commands_executor
        if not self.__commands_executor:
            self.__commands_executor = CommandsExecutor()
        self.__commands_executor.raspilot = self
        self.__custom_providers = raspilot_builder.custom_providers
        self.__notifier = raspilot_builder.notifier

        self.__init_messages = []

        self.__init_rx_provider()
        self.__init_websockets_provider()
        self.__init_orientation_provider()
        self.__init_gps_provider()
        self.__init_servo_controller()
        self.__init_notifier()

        self.__init_custom_providers()

    def __init_websockets_provider(self):
        """
        Initializes the WebsocketsProvider if a provider is set
        :return: returns nothing
        """
        if self.__websockets_provider is not None:
            self.__websockets_provider.raspilot = self
            self.__websockets_provider.initialize()
        else:
            self.__logger.warning('Websockets not available')

    def __init_rx_provider(self):
        """
        Initializes the RXProvider if a provider is set
        :return: returns nothing
        """
        if self.__rx_provider is not None:
            self.__rx_provider.raspilot = self
            self.__rx_provider.initialize()
        else:
            self.__logger.warning('RX input not available')

    def __init_orientation_provider(self):
        """
        Initializes the OrientationProvider if a provider is set
        :return: returns nothing
        """
        if self.__orientation_provider is not None:
            self.__orientation_provider.raspilot = self
            self.__orientation_provider.initialize()
        else:
            self.__logger.warning('Orientation provider not available')

    def __init_gps_provider(self):
        """
        Initializes the GPSProvider if a provider is set
        :return: returns nothing
        """
        if self.__gps_provider is not None:
            self.__gps_provider.raspilot = self
            self.__gps_provider.initialize()
        else:
            self.__logger.warning('GPS provider not available')

    def __init_servo_controller(self):
        """
        Initializes the ServoController if a controller is set
        :return: returns nothing
        """
        if self.__servo_controller is not None:
            self.__servo_controller.raspilot = self
            self.__servo_controller.initialize()
        else:
            self.__logger.warning('Servo controller not available')

    def __init_custom_providers(self):
        """
        Initializes the custom providers if any.
        :return: returns nothing
        """
        for provider in self.__custom_providers:
            provider.raspilot = self
            provider.initialize()

    def __init_notifier(self):
        """
        Initializes the notifier if any.
        :return: returns nothing
        """
        if self.__notifier:
            self.__logger.info("Initializing notifier")
            self.__notifier.raspilot = self
            self.__notifier.initialize()

    def __start_rx_provider(self):
        """
        starts the RXProvider if a provider is set
        :return: returns True, if no provider is set, else return the result of provider start
        """
        if self.__rx_provider is not None:
            return self.__rx_provider.start()
        return True

    def __start_websockets_provider(self):
        """
        starts the WebsocketsProvider if a provider is set
        :return: returns True, if no provider is set, else return the result of provider start
        """
        if self.__websockets_provider is not None:
            return self.__websockets_provider.start()
        return True

    def __start_orientation_provider(self):
        """
        starts the OrientationProvider if a provider is set
        :return: returns True, if no provider is set, else return the result of provider start
        """
        if self.__orientation_provider is not None:
            return self.__orientation_provider.start()
        return True

    def __start_gps_provider(self):
        """
        Starts the GPSProvider if a provider is set.
        :return: returns True, if no provider is set, else return the result of provider start
        """
        if self.__gps_provider is not None:
            return self.__gps_provider.start()
        return True

    def start(self):
        """
        Starts the Raspilot with available providers and blocks till the Raspilot is running.
        :return: return nothing
        """
        init_messages = []
        self.__logger.info('Starting Raspilot...')
        if self.__start_rx_provider():
            self.__logger.info('RX provider started')
        else:
            self.__logger.warning('RX provider failed to start')
            init_messages.append('Warning! Receiver provider failed to start.')

        if self.__start_websockets_provider():
            self.__logger.info('Websockets provider started')
        else:
            self.__logger.warning('Websockets provider failed to start')
            init_messages.append('Warning! Websocket provider failed to start.')

        if self.__start_orientation_provider():
            self.__logger.info('Orientation provider started')
        else:
            self.__logger.warning('Orientation provider failed to start')
            init_messages.append('Warning! Orientation provider failed to start.')

        if self.__start_gps_provider():
            self.__logger.info('GPS provider started')
        else:
            self.__logger.warning('GPS provider failed to start')
            init_messages.append('Warning! GPS provider failed to start')

        self.__start_custom_providers(init_messages)

        # TODO: servo controller

        self.__init_complete_event.set()
        self.__logger.info('Initialization complete, Raspilot is now running!')
        init_messages.append('Initialization complete.')
        if init_messages != [] and self.commands_executor:
            self.commands_executor.send_command(SpeakCommand(init_messages))
        self.__start_notifier()
        self.__stop_self_event.wait()

    def __start_notifier(self):
        """
        Starts the notifier if any.
        :return: returns nothing
        """
        if self.__notifier:
            self.__notifier.start()

    def __start_custom_providers(self, init_messages):
        """
        Starts custom providers, if any.
        :return: returns nothing
        """
        for provider in self.__custom_providers:
            started = provider.start()
            name = provider.__class__.__name__
            if started:
                self.__logger.info("Custom provider '{}' started".format(name))
            else:
                self.__logger.warning("Custom provider '{}' failed to start".format(name))
                init_messages.append('Warning! Custom provider {} failed to start'.format(name))

    def stop(self):
        """
        Stops all available providers, notifier and then stops self.
        :return: return nothing
        """
        self.__logger.info('Stopping Raspilot')
        if self.__commands_executor:
            self.__commands_executor.stop()
        if self.__notifier:
            self.__notifier.stop()
        if self.__rx_provider:
            self.__rx_provider.stop()
        if self.__websockets_provider:
            self.__websockets_provider.stop()
        if self.__orientation_provider:
            self.__orientation_provider.stop()
        if self.__gps_provider:
            self.__gps_provider.stop()
        self.__stop_custom_providers()
        self.__stop_self_event.set()

    def __stop_custom_providers(self):
        """
        Stops custom providers, if any.
        :return: returns nothing
        """
        for provider in self.__custom_providers:
            provider.stop()

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

    @property
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


class RaspilotBuilder:
    """
    Builder for the Raspilot.
    """

    def __init__(self):
        """
        Constructs a new 'RaspilotBuilder' with all providers set as None.
        :return: returns nothing
        """
        self.__websockets_provider = WebsocketsProvider
        self.__rx_provider = None
        self.__orientation_provider = OrientationProvider
        self.__gps_provider = None
        self.__servo_controller = None
        self.__commands_executor = None
        self.__custom_providers = []
        self.__notifier = None

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

    def build(self):
        """
        Builds Raspilot from previously set information.
        :return: a new Raspilot instance created from data in this builder
        """
        return Raspilot(self)
