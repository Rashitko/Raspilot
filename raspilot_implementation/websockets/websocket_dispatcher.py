import json
from threading import Event, RLock

from raspilot_implementation.websockets.websocket_channel import WebsocketChannel
from raspilot_implementation.websockets.websocket_connection import WebsocketConnection
from raspilot_implementation.websockets.websocket_event import WebsocketEvent, nop

STATE_DISCONNECTED = 'disconnected'
STATE_CONNECTED = 'connected'


class WebsocketDispatcher:
    """
    Dispatcher for the websockets. Main class for work with websockets.
    """

    def __init__(self, provider, username, password):
        """
        Constructs new 'WebsocketDispatcher'.
        :param provider: provider which should be notified of important events
        :return: returns nothing
        """
        self.__url = provider.server_address
        self.__provider = provider
        self.__state = STATE_DISCONNECTED
        self.__channels_map = {}
        self.__connection_id = None
        self.__queue = {}
        self.__callbacks = {}
        self.__connection = WebsocketConnection(self.__url, self, username, password)
        self.__connection_wait_event = Event()
        self.__was_connected = False
        self.__recv_lock = RLock()

    def on_new_message(self, message):
        """
        Called when new message arrived. Creates a WebsocketEvent from the message and dispatch this event. In case of
        'ping', events, 'pong' is automatically send. In case of 'client_connected' event, the connection id is saved.
         In case of 'channel' event, the message is dispatched to the channel.
        :param message: received message
        :return: returns nothing.
        """
        with self.__recv_lock:
            data = json.loads(message)
            for entry in data:
                event = WebsocketEvent(entry)
                if event.is_result():
                    queued_event = self.__queue.pop(event.id, None)
                    if queued_event:
                        queued_event.success = event.success
                        queued_event.run_callbacks()
                elif event.is_channel():
                    self.__dispatch_channel(event)
                elif event.is_ping():
                    self.__pong()
                elif event.is_client_connected():
                    self.__client_connected(event)
                else:
                    self.__dispatch(event)

    def on_error(self, error):
        """
        Called when an error occur. Notifies the provider.
        :param error: error occurred
        :return: returns nothing
        """
        self.state = STATE_DISCONNECTED
        self.__connection.disconnect()
        self.__provider.on_error(error)

    def on_close(self):
        """
        Called when connection is closed because of an error, or because of normal disconnect. Notifies the provider.
        :return: returns nothing
        """
        self.state = STATE_DISCONNECTED
        self.__connection_wait_event.set()
        self.__provider.on_close()

    def on_open(self):
        """
        Called when connection is opened. Notifies the provider.
        :return: returns nothing
        """
        pass

    def connect(self):
        """
        Connects to the server.
        :return: returns nothing
        """
        self.__connection.connect()

    def disconnect(self):
        """
        Disconnects the websocket.
        :return: returns nothing
        """
        self.__connection.disconnect()

    def reconnect(self):
        """
        Reconnects.
        :return: returns nothing
        """
        self.__connection.reconnect()

    def should_reconnect(self):

        """
        Returns True, if should reconnect, False, otherwise
        :return: True, if should reconnect, False, otherwise
        """
        return self.__was_connected

    def __pong(self):
        """
        Creates and send the 'pong' event.
        :return: returns nothing
        """
        pong_event = WebsocketEvent.create_pong(self.__connection_id)
        self.__connection.trigger(pong_event)

    def __client_connected(self, event):
        """
        Handles the 'client_connected' event. Saves the connection_id from the message.
        :param event: 'client_connected' event received
        :return: returns nothing
        """
        data = event.data
        self.__connection_id = data.get('connection_id')
        print("connection id is {0}".format(self.connection_id))
        self.state = STATE_CONNECTED
        self.__was_connected = True
        self.__connection_wait_event.set()

    def bind(self, event_name, callback):
        """
        Binds a callback for a event name.
        :param event_name: event name to bind
        :param callback: callback which will be called
        :return: returns nothing
        """
        if not self.__callbacks.get(event_name):
            self.__callbacks[event_name] = []
        self.__callbacks[event_name].append(callback)

    def trigger(self, event_name, data, success_callback=nop, failure_callback=nop):
        """
        Creates event with given name and data sends it and executes the callback if set.
        :param event_name: name for the event
        :param data: data sent in the event
        :param success_callback: callback for success
        :param failure_callback: callback for failure
        :return: returns nothing
        """
        frame = [event_name, data, self.__connection_id]
        event = WebsocketEvent(frame, success_callback, failure_callback)
        self.__queue[event.id] = event
        self.__connection.trigger(event)

    def trigger_event(self, event):
        """
        Sends event, which was previously created.
        :param event: event which should be sent
        :return: returns nothing
        """
        if not self.__queue.get(event.id) or not self.__queue[event.id] == event.id:
            self.__queue[event.id] = event
            self.__connection.trigger(event)

    def __dispatch(self, event):
        """
        Executes callbacks for the received event
        :param event: received event
        :return: returns nothing
        """
        callbacks = self.__callbacks.get(event.event_name, None)
        if callbacks:
            for callback in callbacks:
                callback.on_data_available(event.data)

    def is_subscribed(self, channel_name):
        """
        Returns True, if given channel name is subscribed, False otherwise.
        :param channel_name: name of the channel
        :return: True, if given channel name is subscribed, False otherwise
        """
        return self.__channels_map.get(channel_name) is not None

    def subscribe(self, channel_name, success=nop, failure=nop):
        """
        Subscribes the public channel.
        :param channel_name: name of the channel
        :param success: success callback
        :param failure: failure callback
        :return: returns nothing
        """
        if self.is_subscribed(channel_name):
            return self.__channels_map[channel_name]
        channel = WebsocketChannel(channel_name, self, success=success, failure=failure)
        self.__channels_map[channel_name] = channel
        return channel

    def subscribe_private(self, channel_name):
        """
        Subscribes the private channel.
        :param channel_name: name of the channel
        :return: returns nothing
        """
        if self.is_subscribed(channel_name):
            return self.__channels_map[channel_name]
        channel = WebsocketChannel(channel_name, self, True)
        self.__channels_map[channel_name] = channel
        return channel

    def unsubscribe(self, channel_name):
        """
        Unsubscribes the channel.
        :param channel_name: name of the channel
        :return: returns nothing
        """
        if self.is_subscribed(channel_name):
            self.__channels_map[channel_name].destroy()
            self.__channels_map.pop(channel_name, None)

    def __dispatch_channel(self, event):
        """
        If channel is subscribed, dispatches the event to the channel
        :param event: received event
        :return: returns nothing
        """
        channel_name = None if not event.channel else event.channel
        if self.is_subscribed(channel_name):
            self.__channels_map[channel_name].dispatch(event.event_name, event.data)

    def wait_for_connection(self):
        """
        Blocks until connection is successfully created, or till the connection fails.
        :return: returns nothing
        """
        self.__connection_wait_event.wait()

    def is_connected(self):
        """
        Returns True if connected, false otherwise
        :return: True if connected, false otherwise
        """
        return self.state == STATE_CONNECTED

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value

    @property
    def url(self):
        return self.__url

    @property
    def connection_id(self):
        return self.__connection_id
