DATA_KEY = 'data'

SUCCESS_KEY = 'success'

ID_KEY = 'requestID'


class CommandResponse:
    """
    Response object. Sent in Android and websocket commands. Used when responding to commands which has requests flag
    set.
    """

    def __init__(self, request_id, success, data=None):
        """
        Creates a new 'CommandResponse' which wraps additional information about executing the request. Used when
        replying to the CommandRequests.
        :param request_id: id of request command, which this command responds to
        :param success: True if request was successfully executed, False otherwise
        :param data: additional data, must be serializable via json.dumps(data)
        :return: returns nothing
        """
        self.__request = request_id
        self.__success = success
        self.__data = data

    def serialize(self):
        """
        Serializes the object as a JSON object.
        :return:
        """
        result = {ID_KEY: self.__request, SUCCESS_KEY: self.__success}
        if self.__data:
            result[DATA_KEY] = self.__data
        return result

    @classmethod
    def from_json(cls, json_data):
        """
        Deserializes the CommandResponse from the provided json
        :param json_data: json object to load from
        :return: returns deserialized CommandResponse
        """
        data = json_data.get(DATA_KEY, None)
        return cls(json_data[ID_KEY], json_data[SUCCESS_KEY], data)
