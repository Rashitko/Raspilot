import uuid

from raspilot.commands.response import CommandResponse

RESPONSE_KEY = 'response'

REQUEST_KEY = 'request'

DATA_KEY = 'data'

NAME_KEY = 'name'


class Command:
    """
    General command used in control the Raspilot
    """

    def __init__(self, name, data, request, response):
        """
        Creates a new 'Command' with provided name, data, request flag and respons object.
        :param name: name of the command
        :param data: data associated with this command
        :param request: request flag
        :param response: response object
        :return: returns nothing
        """
        self.__name = name
        self.__data = data
        self.__request = request
        self.__response = response
        self.__id = uuid.uuid4()

    def serialize(self):
        """
        Serializes the command as a dict.
        :return: returns serialized command
        """
        serialized_response = None
        if self.response:
            serialized_response = self.response.serialize()
        return {NAME_KEY: self.name, DATA_KEY: self.data, REQUEST_KEY: self.request, RESPONSE_KEY: serialized_response}

    @classmethod
    def from_json(cls, data):
        """
        Constructs new command from provided dict.
        :param data: dict to load data from
        :return: returns newly created command
        """
        response = None
        if RESPONSE_KEY in data:
            response = CommandResponse.from_json(data[RESPONSE_KEY])
        return cls(data[NAME_KEY], data[DATA_KEY], data[REQUEST_KEY], response)

    @property
    def name(self):
        return self.__name

    @property
    def data(self):
        return self.__data

    @property
    def request(self):
        return self.__request

    @property
    def response(self):
        return self.__response
