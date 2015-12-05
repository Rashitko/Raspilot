import json

import raspilot.providers.base_provider
import raspilot_implementation.providers.socket_provider

DATA_KEY = 'data'
RESPONSE_KEY = 'response'
REQUEST_KEY = 'request'
COMMAND_KEY = 'command'
ID_KEY = 'id'

RECV_SIZE = 1024


class AndroidProvider(raspilot_implementation.providers.socket_provider.SocketProvider):
    """
    Provider of communication with the Android device
    """

    def __init__(self, config):
        """
        Creates a new 'AndroidProvider' from the specified config
        :param config: configuration to load from
        :return: returns nothing
        """
        super().__init__(config.port, RECV_SIZE)

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
        deserialized_data = json.loads(data)
        valid_command = self._validate_command(deserialized_data)
        if valid_command:
            command_name = deserialized_data[COMMAND_KEY]
            command_id = deserialized_data[ID_KEY]
            command_data = deserialized_data[DATA_KEY]
            request = deserialized_data[REQUEST_KEY]
            response = None
            if RESPONSE_KEY in deserialized_data:
                response = deserialized_data[RESPONSE_KEY]
            self.raspilot.execute_command(command_name, command_id, command_data, request, response)

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
