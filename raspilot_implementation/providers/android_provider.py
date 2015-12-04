import raspilot.providers.base_provider
import raspilot_implementation.providers.socket_provider
import json

RESPONSE_KEY = 'response'

DATA_KEY = 'data'
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
        The json should contain
        * the command name, which is used to identify the command
        * the data, which are passed to the action associated with the command
        * the id of the command, used to identify the commands
        * response object containing the success flag and id of received message which this message responds to
        :param data: received data
        :return: returns nothing
        """
        super()._on_data_received(data)
        deserialized_data = json.loads(data)
        command = deserialized_data[COMMAND_KEY]
        if command:
            command_data = deserialized_data[DATA_KEY]
            command_id = deserialized_data[ID_KEY]
            response = deserialized_data[RESPONSE_KEY]
            self.raspilot.execute_command(command, command_data, command_id, response)


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
