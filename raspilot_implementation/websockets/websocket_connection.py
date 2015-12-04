import base64
import logging
from threading import Thread

from websocket import WebSocketApp

NAME_NOT_PROVIDED = "Name not provided"


class WebsocketConnection:
    """
    Websocket connection. Used to send, receive messages.
    """

    def __init__(self, url, dispatcher, username, password):
        """
        Constructs a new 'WebsocketConnection'. Does not connect, until WebsocketConnection.connect() is called.
        :param url: address where to connect
        :param dispatcher: dispatcher used for communication
        :return: returns nothing
        """
        self.__logger = logging.getLogger('raspilot.log')
        self.__dispatcher = dispatcher
        self.__url = url
        self.__message_queue = []
        self.__connection_id = None
        self.__username = username
        self.__password = password
        self.__websocket_app = self.__create_websocket_app()

    def __create_websocket_app(self):
        auth_data = "{}:{}".format(self.__username, self.__password).encode('utf-8')
        auth_encoded = "Basic {}".format(base64.b64encode(auth_data).decode('ascii'))
        auth_header = "Authorization:{}".format(auth_encoded)
        return WebSocketApp(self.__url, on_open=self.__on_open, on_message=self.__on_message,
                            on_close=self.__on_close, on_error=self.__on_error, header={auth_header})

    def connect(self):
        """
        Connects to the server.
        :return: returns nothing
        """
        Thread(target=self.__websocket_app.run_forever).start()

    def disconnect(self):
        """
        Disconnects the socket.
        :return: returns nothing
        """
        self.__websocket_app.close()

    def reconnect(self):
        """
        Reconnects to the server. WebsocketApp is closed, newly created and WebsocketConnection.connect() is called
        :return: returns nothing
        """
        self.__websocket_app.close()
        self.__websocket_app = self.__create_websocket_app()
        self.connect()

    def trigger(self, event):
        """
        Sends event to the server. If not connected, event is added to the queue.
        :param event: event to send
        :return: returns True if message was transmitted, False otherwise
        """
        if not self.__dispatcher.is_connected():
            self.__message_queue.append(event)
            return False
        else:
            return self.__send_event(event)

    def __flush_queue(self):
        """
        Sends all events from the queue.
        :return: returns nothing
        """
        for event in self.__message_queue:
            self.trigger(event)
        self.__message_queue = []

    def __send_event(self, event):
        """
        Sends event.
        :param event: event to send
        :return: returns True if event was transmitted, False otherwise
        """
        data = event.to_json()
        return self.__send(data, event.event_name)

    def __send(self, data, event_name=NAME_NOT_PROVIDED):
        """
        Sends the data via the websocket.
        :param data: data to be sent
        :param event_name: name of the event, or other identification for logging purposes
        :return:
        """
        self.__logger.log(9, ("----> SENDING: {}".format(event_name)))
        return self.__ws.send(data) is None

    def __on_open(self, ws):
        """
        Called when connection is opened
        :param ws: websocket
        :return: returns nothing
        """
        self.__ws = ws
        self.__dispatcher.on_open()

    def __on_close(self, ws):
        """
        Called when connection is closed, might be because of an error, or because of the normal disconnect.
        :param ws: websocket
        :return: returns nothing
        """
        self.__ws = ws
        self.__dispatcher.on_close()

    def __on_error(self, ws, error):
        """
        Called when an error occurred.
        :param ws: websocket
        :param error: error occurred
        :return: returns nothing
        """
        self.__ws = ws
        self.__dispatcher.on_error(error)

    def __on_message(self, ws, message):
        """
        Called when new message is received.
        :param ws: websocket
        :param message: message received
        :return: returns nothing
        """
        self.__ws = ws
        self.__logger.log(9, ("<---- RECEIVED: {}".format(message)))
        self.__dispatcher.on_new_message(message)

    @property
    def connection_id(self):
        return self.__connection_id

    @connection_id.setter
    def connection_id(self, value):
        self.__connection_id = value

    def raw_send(self, message, success, failure):
        """
        Sends a raw message via the websocket. If the transmission fails failure callback is executed (if set).
        If the transmission is successful the success callback is executed (if set). It is not verified that someone
        receives the message, only transmission success is reported. Callbacks should have one parameter - message.
        :param message: message to be sent
        :param success: success callback
        :param failure: failure callback
        :return: True if transmission is successful, False otherwise.
        """
        result = False
        if self.__ws:
            error = self.__send(message, message)
            if not error:
                result = True
                if success:
                    success()
            else:
                if failure:
                    failure()
        else:
            if failure:
                failure()
        return result
