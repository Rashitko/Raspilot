from raspilot_implementation.websockets.websocket_event import WebsocketEvent


class WebsocketChannel:
    """
    Websocket channel used for communication between subscribers.
    """

    def __init__(self, channel_name, dispatcher, private=False):
        """
        Constructs a new 'WebsocketChannel' with given channel name and subscribes this channel
        :param channel_name: desired channel name
        :param dispatcher: dispatcher used for communication
        :param private: True if channel should be private
        :return: returns nothing
        """
        self.__callbacks = {}
        self.__channel_name = channel_name
        self.__token = None
        self.__dispatcher = dispatcher

        event_name = 'websocket_rails.subscribe_private' if private else 'websocket_rails.subscribe'
        info = {'channel': channel_name}
        data = {'data': info}
        frame = [event_name, data, dispatcher.connection_id]
        event = WebsocketEvent(frame)
        dispatcher.trigger_event(event)

    def bind(self, event_name, callback):
        """
        Binds and callback for the given event name.
        :param event_name: event name to bind to
        :param callback: callback which should be run
        :return: returns nothing
        """
        if not self.__callbacks.get(event_name):
            self.__callbacks[event_name] = []
        self.__callbacks[event_name].append(callback)

    def trigger(self, event_name, message):
        """
        Publishes the event to the channel.
        :param event_name: event name of the event
        :param message: message which should be in the event
        :return: return nothing
        """
        info = {'channel': self.__channel_name, 'data': message, 'token': self.__token}
        frame = [event_name, info, self.__dispatcher.connection_id]
        event = WebsocketEvent(frame)
        self.__dispatcher.trigger_event(event)

    def dispatch(self, event_name, message):
        """
        Run callbacks for the received event.
        :param event_name: event name of the received event
        :param message: message which will be dispatched
        :return: returns nothing
        """
        if 'websocket_rails.channel_token' == event_name:
            self.__token = message['token']
            print("Channel token is {}".format(self.__token))
        for callback in self.__callbacks[event_name]:
                callback.on_data_available(message)

    def destroy(self):
        """
        Unsubscribes from the channel.
        :return: returns nothing
        """
        event_name = 'websocket_rails.unsubscribe'
        data = {
            'data': {
                'channel': self.__channel_name
            }
        }
        frame = [event_name, data, self.__dispatcher.connection_id]
        event = WebsocketEvent(frame)
        self.__dispatcher.trigger_event(event)
        self.__callbacks = {}
