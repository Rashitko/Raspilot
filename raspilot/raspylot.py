from threading import Event

from raspilot.commands_executor import CommandsExecutor, CommandExecutionError


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
        self.__rx_provider = raspilot_builder.rx_provider
        self.__websockets_provider = raspilot_builder.websockets_provider
        self.__orientation_provider = raspilot_builder.orientation_provider
        self.__gps_provider = raspilot_builder.gps_provider
        self.__servo_controller = raspilot_builder.servo_controller
        self.__stop_self_event = Event()
        self.__init_complete_event = Event()
        self.__commands_executor = raspilot_builder.commands_executor
        self.__custom_providers = raspilot_builder.custom_providers

        self.__init_rx_provider()
        self.__init_websockets_provider()
        self.__init_orientation_provider()
        self.__init_gps_provider()
        self.__init_servo_controller()

        self.__init_custom_providers()

    def __init_websockets_provider(self):
        """
        Initializes the WebsocketsProvider if a provider is set
        :return: returns nothing
        """
        if self.__websockets_provider is not None:
            self.__websockets_provider.__raspilot = self
            self.__websockets_provider.initialize()
        else:
            print('Websockets not available')

    def __init_rx_provider(self):
        """
        Initializes the RXProvider if a provider is set
        :return: returns nothing
        """
        if self.__rx_provider is not None:
            self.__rx_provider.__raspilot = self
            self.__rx_provider.initialize()
        else:
            print('RX input not available')

    def __init_orientation_provider(self):
        """
        Initializes the OrientationProvider if a provider is set
        :return: returns nothing
        """
        if self.__orientation_provider is not None:
            self.__orientation_provider.__raspilot = self
            self.__orientation_provider.initialize()
        else:
            print('Orientation provider not available')

    def __init_gps_provider(self):
        """
        Initializes the GPSProvider if a provider is set
        :return: returns nothing
        """
        if self.__gps_provider is not None:
            self.__gps_provider.__raspilot = self
            self.__gps_provider.initialize()
        else:
            print('GPS provider not available')

    def __init_servo_controller(self):
        """
        Initializes the ServoController if a controller is set
        :return: returns nothing
        """
        if self.__servo_controller is not None:
            self.__servo_controller.__raspilot = self
            self.__servo_controller.initialize()
        else:
            print('Servo controller not available')

    def __init_custom_providers(self):
        """
        Initializes the custom providers if any.
        :return: returns nothing
        """
        for provider in self.__custom_providers:
            provider.__raspilot = self
            provider.initialize()

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

    def start(self):
        """
        Starts the Raspilot with available providers and blocks till the Raspilot is running.
        :return: return nothing
        """
        print('Starting Raspilot...')
        if self.__start_rx_provider():
            print('RX provider started')
        else:
            print('RX provider failed to start')

        if self.__start_websockets_provider():
            print('Websockets provider started')
        else:
            print('Websockets provider failed to start')

        if self.__start_orientation_provider():
            print('Orientation provider started')
        else:
            print('Orientation provider failed to start')

        self.__start_custom_providers()

        # TODO: gps, servo controller

        self.__init_complete_event.set()
        print('Initialization complete, Raspilot is now running!')
        self.__stop_self_event.wait()

    def __start_custom_providers(self):
        """
        Starts custom providers, if any.
        :return: returns nothing
        """
        for provider in self.__custom_providers:
            started = provider.start()
            name = provider.__class__.__name__
            if started:
                print("Custom provider '{}' started".format(name))
            else:
                print("Custom provider '{}' failed to start".format(name))

    def stop(self):
        """
        Stops all available providers and the stops self.
        :return: return nothing
        """
        print('Stopping Raspilot\n')
        if self.__rx_provider is not None:
            self.__rx_provider.stop()
        if self.__websockets_provider is not None:
            self.__websockets_provider.stop()
        if self.__orientation_provider is not None:
            self.__orientation_provider.stop()
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

    def bind_command(self, command, action):
        """
        Associates the command and the callable action. Upon receiving of the command, the action will be called.
        If command is already bound, the action is replaced.
        :param command: command to bind to
        :param action: action to execute, should be callable
        :return: returns nothing
        """
        self.__commands_executor.bind_command(command, action)

    def unbind_command(self, command):
        """
        Unbinds the command. If command is not bound, nothing is changed.
        :param command: command to unbind from
        :return: return command or None, if command is not bound
        """
        return self.__commands_executor.unbind_command(command)

    def execute_command(self, command, default_action=nop, on_error=nop):
        """
        If command is bound executes the action, otherwise the default_action is executed.
        :param command: command which should be executed
        :param default_action: callable action which is executed when command is not bound
        :param on_error: callable action which is executed when CommandExecutionError is risen, usually when command
        fails to execute
        """
        try:
            if not self.__commands_executor.execute_command(command):
                default_action()
        except CommandExecutionError:
            on_error()

    @property
    def websocket_provider(self):
        return self.__websockets_provider


class RaspilotBuilder:
    """
    Builder for the Raspilot.
    """

    def __init__(self):
        """
        Constructs a new 'RaspilotBuilder' with all providers set as None.
        :return: returns nothing
        """
        self.__websockets_provider = None
        self.__rx_provider = None
        self.__orientation_provider = None
        self.__gps_provider = None
        self.__servo_controller = None
        self.__commands_executor = CommandsExecutor()
        self.__custom_providers = []

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

    def build(self):
        """
        Builds Raspilot from previously set information.
        :return: a new Raspilot instance created from data in this builder
        """
        return Raspilot(self)
