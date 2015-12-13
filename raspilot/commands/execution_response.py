DATA_KEY = 'data'
SOURCE_ID_KEY = 'sourceID'
SUCCESS_KEY = 'success'


class ExecutionResponse:
    """
    Wrapper for the commands responses.
    """

    def __init__(self, success, source_id, data):
        """
        Creates a new 'ExecutionResponse' with the specified attributes. Instance must be serialized using the serialize
        method in order to be sent as a JSON message.
        :param success: boolean flag, if the operation was successfully executed
        :param source_id: command id to which this message responds
        :param data: additional data
        :return: returns nothing
        """
        self.__success = success
        self.__source_id = source_id
        self.__data = data

    def serialize(self):
        """
        Serializes the ExecutionResponse to a dict.
        :return: dict representation of the ExecutionResponse
        """
        return {SUCCESS_KEY: self.__success,
                SOURCE_ID_KEY: self.__source_id,
                DATA_KEY: self.__data}
