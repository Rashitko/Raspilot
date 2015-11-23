from threading import Event


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

        self.__init_rx_provider()
        self.__init_websockets_provider()
        self.__init_orientation_provider()
        self.__init_gps_provider()
        self.__init_servo_controller()

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

        # TODO: gps, servo controller

        self.__init_complete_event.set()
        print('Initialization complete, Raspilot is now running!')
        self.__stop_self_event.wait()

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
        self.__stop_self_event.set()

    def wait_for_init_complete(self):
        """
        Blocks until initialization is complete.
        :return: returns nothing
        """
        self.__init_complete_event.wait()

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

    def build(self):
        """
        Builds Raspilot from previously set information.
        :return: a new Raspilot instance created from data in this builder
        """
        return Raspilot(self)
