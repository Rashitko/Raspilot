from threading import Thread
from websocket import WebSocketApp
import base64


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
        :return: returns nothing
        """
        if not self.__dispatcher.is_connected():
            self.__message_queue.append(event)
        else:
            self.__send_event(event)

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
        :return: returns nothing
        """
        data = event.to_json()
        print("----> SENDING: {}".format(event.event_name))
        self.__ws.send(data)

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
        print("<---- RECEIVED: {}".format(message))
        self.__dispatcher.on_new_message(message)

    @property
    def connection_id(self):
        return self.__connection_id

    @connection_id.setter
    def connection_id(self, value):
        self.__connection_id = value
