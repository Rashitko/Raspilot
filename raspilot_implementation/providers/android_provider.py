import raspilot.providers.base_provider
import raspilot_implementation.providers.socket_provider


class AndroidProvider(raspilot_implementation.providers.socket_provider.SocketProvider):
    """
    Provider of communication with the Android device
    """

    def __init__(self, config):
        """
        Creates a new 'AndroidProvider' from the specified config
        :param config: configuration to load from
        :return: returns nothing
        """
        super().__init__(config.port)


class AndroidProviderConfig(raspilot.providers.base_provider.BaseProviderConfig):
    """
    Configuration class for the Android provider.
    """

    def __init__(self, port):
        """
        Creates a new 'AndroidProviderConfig' which is used to configure the AndroidProvider.
        :param port: port to listen on
        :return: returns nothing
        """
        super().__init__()
        self.__port = port

    @property
    def port(self):
        return self.__port
