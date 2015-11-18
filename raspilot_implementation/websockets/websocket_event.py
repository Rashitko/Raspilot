import json

EVENT_TYPE_CLIENT_CONNECTED = 'client_connected'
EVENT_TYPE_PING = 'websocket_rails.ping'


def nop():
    pass


class WebsocketEvent:
    """
    Event representation used in the websocket.
    """

    def __init__(self, message, success_callback=nop, failure_callback=nop):
        """
        Creates a new 'WebsocketEvent' with given message and callbacks.
        :param message: message in format [event_name, payload]
        :param success_callback: called when event is successful
        :param failure_callback: called when event fails
        :return: returns nothing
        """
        self.__event_name = message[0]
        payload = message[1]
        self.__id = payload.get('id')
        self.__channel = payload.get('channel')
        self.__data = payload.get('data')
        self.__token = payload.get('token')
        self.__success = payload.get('success')
        self.__success_callback = success_callback
        self.__failure_callback = failure_callback

    def is_success(self):
        """
        Returns True if is successful.
        :return: True if is successful, False otherwise
        """
        return self.__success is not None

    def is_ping(self):
        """
        Returns True if is ping.
        :return: True if is ping, False otherwise
        """
        return self.__event_name == EVENT_TYPE_PING

    def is_result(self):
        """
        Returns True if is result.
        :return: True if is result, False otherwise
        """
        return self.__success is not None

    def is_channel(self):
        """
        Returns True if is send in channel.
        :return: True if is send in channel, False otherwise
        """
        return self.__channel is not None

    def run_callbacks(self):
        """
        Runs the successful callback if is successful and the callback is set, otherwise runs failure callback if the
        callback is set.
        :return: returns nothing
        """
        if self.is_success() and self.__success_callback is not None:
            self.__success_callback()
        elif self.__failure_callback is not None:
            self.__failure_callback()

    def is_client_connected(self):
        """
        Returns True if is 'client_connected' event.
        :return: True if is 'client_connected' event, False otherwise
        """
        return self.__event_name == EVENT_TYPE_CLIENT_CONNECTED

    def to_json(self):
        """
        Serializes the event into JSON
        :return: JSON representation of the event
        """
        serialized = [self.__event_name, {'channel': self.__channel, 'data': self.data, 'id': self.id}]
        return json.dumps(serialized, indent=4)

    @property
    def id(self):
        return self.__id

    @property
    def data(self):
        return self.__data

    @property
    def channel(self):
        return self.__channel

    @property
    def event_name(self):
        return self.__event_name

    @classmethod
    def create_pong(cls, connection_id):
        message = ['websocket_rails.pong', {'data': {'connection_id': connection_id}}]
        pong_event = cls(message)
        return pong_event
