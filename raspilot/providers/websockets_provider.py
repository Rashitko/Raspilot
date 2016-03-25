import logging
import time

from raspilot.providers.base_provider import BaseProvider, BaseProviderConfig

MILLIS_IN_SECOND = 1000

DEFAULT_RETRY_DELAY = 500
DEFAULT_RECONNECT_COUNT = 120


class WebsocketsProvider(BaseProvider):
    """
    Abstract WebsocketProvider which provides the basic methods for work with websockets
    """

    def __init__(self, websockets_config):
        """
        Constructs a new 'WebsocketProvider' which is initialized from data in the configuration
        :param websockets_config: configuration to read initialization data from
        :return: returns nothing
        """
        if websockets_config is None:
            raise ValueError("Config cannot be None")
        self.__logger = logging.getLogger('raspilot.log')
        super().__init__(websockets_config)
        self.__retry_count = websockets_config.retry_count
        self.__reconnect_delay = websockets_config.reconnect_delay
        self.__retries = 0
        self.__raspilot = None

    def start(self):
        BaseProvider.start(self)

    def stop(self):
        self.disconnect()
        self.__logger.info('Stopping websocket provider')
        BaseProvider.stop(self)

    def connect(self):
        """
        Connects the websocket.
        :return: returns nothing
        """
        pass

    def reconnect(self):
        """
        Reconnects the websocket. Called after connection drop.
        :return: returns nothing
        """
        pass

    def disconnect(self):
        """
        Disconnect the websocket.
        :return: returns nothing
        """
        pass

    def should_reconnect(self):
        """
        Returns True if should try to reconnect, False otherwise
        :return: True if should try to reconnect, False otherwise
        """
        return False

    def on_error(self, error):
        """
        Called when an error occurred. Tries to reconnect if reconnection limit is not reached
        :param error: occurred error
        :return: returns nothing
        """
        self.__logger.error("Error occurred: {}".format(error))
        self.__retries += 1

        if self.should_reconnect():
            if self.__retry_count > self.__retries:
                self.__logger.warning("Trying to reconnect. {}/{}".format(self.__retries, self.__retry_count))
                time.sleep(self.__reconnect_delay / MILLIS_IN_SECOND)
                self.reconnect()
            else:
                self.__logger.error("Connection failed, retries limit reached.")
        else:
            self.__logger.error("Connection fails, but not trying to reconnect")

    def send_telemetry_update_message(self, message, success=None, failure=None):
        """
        Sends the message. The default implementation fails to send the message. Callbacks should have one
        parameter - message.
        :param message: message to be sent
        :param success: success callback, run if transmission was successful
        :param failure: failure callback, run if transmission failed
        :return: returns nothing
        """
        if failure:
            failure(message)

    def send_message(self, message, success=None, failure=None):
        """
        Sends the message. The default implementation fails to send the message. Callbacks should have one
        parameter - message.
        :param message: message to be sent
        :param success: success callback, run if transmission was successful
        :param failure: failure callback, run if transmission failed
        :return: returns nothing
        """
        if failure:
            failure(message)

    def on_close(self):
        """
        Called when connection is closed. This can happen after an error, or when the connection was closed in normal
        way.
        :return: returns nothing
        """
        self.__logger.info("Websocket closed")

    @property
    def retry_count(self):
        return self.__retry_count

    @property
    def reconnect_delay(self):
        return self.__reconnect_delay


class WebsocketsConfig(BaseProviderConfig):
    """
    Used to initialize the WebsocketsProvider. All subclasses of the WebsocketProvider which has their own config,
    should extend this class.
    """

    def __init__(self, retry_count=DEFAULT_RECONNECT_COUNT, retry_delay=DEFAULT_RETRY_DELAY):
        """
        Constructs a new 'WebsocketsConfig' which is used to initialize the WebsocketsProvider.
        :param retry_count: number of retries to reconnect
        :param retry_delay: delay in ms to wait between reconnects
        :return: returns nothing
        """
        BaseProviderConfig.__init__(self)
        self.__retry_count = retry_count
        self.__reconnect_delay = retry_delay

    @property
    def retry_count(self):
        return self.__retry_count

    @retry_count.setter
    def retry_count(self, value):
        self.__retry_count = value

    @property
    def reconnect_delay(self):
        return self.__reconnect_delay

    @reconnect_delay.setter
    def reconnect_delay(self, value):
        self.__reconnect_delay = value
