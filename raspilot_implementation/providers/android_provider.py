import json
import logging

import raspilot.providers.base_provider
from raspilot_implementation.providers.stream_socket_provider import StreamSocketProvider

DATA_KEY = 'data'
RESPONSE_KEY = 'response'
REQUEST_KEY = 'request'
COMMAND_KEY = 'command'
ID_KEY = 'id'

RECV_SIZE = 1024


class AndroidProvider(StreamSocketProvider):
    """
    Provider of communication with the Android device
    """
    NAME = "Android Provider"

    def __init__(self, config):
        """
        Creates a new 'AndroidProvider' from the specified config
        :param config: configuration to load from
        :return: returns nothing
        """
        super().__init__(config.port, RECV_SIZE, AndroidProvider.NAME)
        self.__logger = logging.getLogger('raspilot.log')

    def _on_data_received(self, data):
        """
        Reads json from the received data and executes command present in this json. For json format see the docs.
        The json must contain
        * the command name, which is used to identify the command
        * the id of the command, used to identify the commands
        * the data, which are passed to the action associated with the command, might be None
        * the response flag, which determines whether and response should be sent after the execution
        * response object, containing additional information about the request execution, might be None
        :param data: received data
        :return: returns nothing
        """
        super()._on_data_received(data)
        deserialized_data = json.loads(data.decode('utf-8'))
        valid_command = self._validate_command(deserialized_data)
        if valid_command:
            command_name = deserialized_data.get(COMMAND_KEY, None)
            command_id = deserialized_data.get(ID_KEY, None)
            command_data = deserialized_data.get(DATA_KEY, None)
            request = deserialized_data.get(REQUEST_KEY, None)
            response = None
            if RESPONSE_KEY in deserialized_data:
                response = deserialized_data.get(RESPONSE_KEY, None)
            self.raspilot.execute_command(command_name, command_id, command_data, request, response)

    def send_command(self, command):
        """
        Serializes the command as JSON string and adds it to the send queue.
        :param command: command to be sent
        :return: returns nothing
        """
        self.send(json.dumps(command.serialize()) + '\n')

    @staticmethod
    def _validate_command(received_data):
        """
        Validates the command. Valid command contains all required keys.
        :param received_data: data which should be validated
        :return: returns True if command is valid, False otherwise
        """
        return COMMAND_KEY in received_data and DATA_KEY in received_data and ID_KEY in received_data and REQUEST_KEY in received_data


class AndroidProviderConfig(raspilot.providers.base_provider.BaseProviderConfig):
    """
    Configuration class for the Android provider.
    """

    def __init__(self, port):
        """
        Creates a new 'AndroidProviderConfig' which is used to configure the AndroidProvider.
        :param port: port to listen on
        :return: returns nothing
        """
        super().__init__()
        self.__port = port

    @property
    def port(self):
        return self.__port
