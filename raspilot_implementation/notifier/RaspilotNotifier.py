import logging

from raspilot.notifier.base_notifier import BaseNotifier


class RaspilotNotifier(BaseNotifier):
    """
    An extension to the BaseNotifier which uses the websocket_rails events.
    """

    def __init__(self, namespace, update_freq, error_limit=100):
        """
        Creates a new 'RaspilotNotifier' which will send updates as websocket_rails events. These events will have the
        specified namespace
        :param namespace: namespace of the events
        :param update_freq: how often the updates will be send, in milliseconds
        :param error_limit: how many sequential errors can occur when sending updates before stopping updates
        :return: returns nothing
        """
        super().__init__(update_freq, error_limit)
        self.__logger = logging.getLogger('raspilot.log')
        self.__namespace = namespace

    def _prepare_message(self):
        """
        Creates an update message which contains orientation data
        :return: created event
        """
        orientation = self.raspilot.orientation_provider.current_orientation()
        location = self.raspilot.gps_provider.location
        if orientation:
            orientation_data = orientation.to_json()
        else:
            orientation_data = {'error': {'message': 'current orientation was null'}}
        if location:
            location_data = location.to_json()
        else:
            location_data = {'error': {'message': 'current location was null'}}
        data = {'orientation': orientation_data, 'location': location_data}
        self.__logger.info("Sending telemetry update: {}".format(data))
        return data

    def _serialize_message(self, message):
        """
        Message serialization is not needed, it will be serialized later in the websockets module
        :param message message which should be sent
        :return: message
        """
        return message
