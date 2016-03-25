from threading import Event

from raspilot.providers.websockets_provider import WebsocketsProvider, WebsocketsConfig
from raspilot_implementation.websockets.websocket_dispatcher import WebsocketDispatcher

CHANNEL_NAME_FORMAT = "device:{}"


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
        self.__device_identifier = websockets_config.device_identifier
        self.__dispatcher = WebsocketDispatcher(self, self.__username, self.__password)
        self.__channel_connected = False
        self._wait_for_channel = Event()
        self.__channel = None

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

    def should_reconnect(self):
        """
        Asks the dispatcher whether should reconnect
        :return: result from dispatcher
        """
        return self.__dispatcher.should_reconnect()

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
        if not self.__dispatcher.is_connected():
            return False
        channel_name = CHANNEL_NAME_FORMAT.format(self.__device_identifier)
        self.__channel = self.__dispatcher.subscribe(channel_name, success=self.__on_channel_connection,
                                                     failure=self.__on_channel_connection)
        self._wait_for_channel.wait()
        return self.__dispatcher.connection_id and self.__channel_connected

    def send_telemetry_update_message(self, message, success=None, failure=None):
        """
        Sends a raw message via the websocket. If the transmission fails failure callback is executed (if set).
        If the transmission is successful the success callback is executed (if set). It is not verified that someone
        receives the message, only transmission success is reported. Callbacks should have one parameter - message.
        :param message: message to be sent
        :param success: success callback
        :param failure: failure callback
        :return: True if transmission is successful, False otherwise.
        """
        if self.__channel:
            trigger = self.__channel.trigger('telemetry.update', message)
            return trigger
        else:
            return False

    def send_message(self, message, success=None, failure=None):
        self.__dispatcher.trigger_event(message)

    def __on_channel_connection(self, success):
        self.__channel_connected = success
        self._wait_for_channel.set()

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
        self.__device_identifier = raspilot_config.device_identifier

    @property
    def server_address(self):
        return self.__server_address

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def device_identifier(self):
        return self.__device_identifier
