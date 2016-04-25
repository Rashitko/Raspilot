import logging

from obsolete.raspilot.providers import BaseProvider

MILLIS_IN_SECOND = 1000

DEFAULT_RETRY_DELAY = 500
DEFAULT_RECONNECT_COUNT = 120


class FlightControlProvider(BaseProvider):
    """
    Abstract WebsocketProvider which provides the basic methods for work with websockets
    """

    def __init__(self, websockets_config):
        """
        Constructs a new 'WebsocketProvider' which is initialized from data in the configuration
        :param websockets_config: configuration to read initialization data from
        :return: returns nothing
        """
        super().__init__(websockets_config)
        self.__logger = logging.getLogger('raspilot.log')

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
