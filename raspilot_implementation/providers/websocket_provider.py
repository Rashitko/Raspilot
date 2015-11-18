from raspilot.providers.websockets_provider import WebsocketsProvider, WebsocketsConfig
from raspilot_implementation.websockets.websocket_dispatcher import WebsocketDispatcher


class RaspilotWebsocketsProvider(WebsocketsProvider):

    """
    Implementation of the abstract WebsocketsProvider.
    """

    def __init__(self, websockets_config):
        """
        Constructs a new 'RaspilotWebsocketsProvider' which is initialized from data in the configuration.
        :param websockets_config: configuration to read initialization data from
        :return: returns nothing
        """
        WebsocketsProvider.__init__(self, websockets_config)
        self.__server_address = websockets_config.server_address
        self.__username = websockets_config.username
        self.__password = websockets_config.password
        self.__dispatcher = WebsocketDispatcher(self)

    def connect(self):
        """
        Connects the dispatcher.
        :return: return nothing
        """
        WebsocketsProvider.connect(self)
        self.__dispatcher.connect()

    def disconnect(self):
        """
        Disconnects the dispatcher.
        :return: return nothing
        """
        WebsocketsProvider.disconnect(self)
        self.__dispatcher.disconnect()

    def reconnect(self):
        """
        Reconnects the dispatcher.
        :return: return nothing
        """
        WebsocketsProvider.reconnect(self)
        self.__dispatcher.reconnect()

    def start(self):
        """
        Connects and waits for the success of failure.
        :return: True, if connection is successful, False otherwise
        """
        WebsocketsProvider.start(self)
        self.connect()
        self.__dispatcher.wait_for_connection()
        return self.__dispatcher.connection_id

    def subscribe(self, channel_name):
        """
        Subscribes the given channel name
        :param channel_name: channel name to subscribe
        :return: returns nothing
        """
        self.__dispatcher.subscribe(channel_name)

    @property
    def server_address(self):
        return self.__server_address


class RaspilotWebsocketsConfig(WebsocketsConfig):
    """
    Used to initialize the RaspilotWebsocketsProvider. All subclasses of the RaspilotWebsocketsProvider which has their
    own config should extend this class.
    """

    def __init__(self, raspilot_config):
        """
        Constructs a new 'RaspilotWebsocketsConfig' which is used to initialize the RaspilotWebsocketsProvider.
        :param raspilot_config: configuration used to read data from
        :return: returns nothing
        """
        if raspilot_config is None:
            raise ValueError("Raspilot config must be set")
        WebsocketsConfig.__init__(self, raspilot_config.retry_count, raspilot_config.retry_delay)
        self.__server_address = raspilot_config.websockets_url
        self.__username = raspilot_config.username
        self.__password = raspilot_config.password

    @property
    def server_address(self):
        return self.__server_address

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password
