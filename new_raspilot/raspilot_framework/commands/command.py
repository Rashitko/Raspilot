import json
from abc import abstractmethod

from new_raspilot.raspilot_framework.utils.raspilot_logger import RaspilotLogger


class Command:
    def __init__(self):
        super().__init__()
        self.__name = None
        self.__data = None
        self.__id = None

    def serialize(self):
        serialized_json = {'name': self.name, 'data': self.data, 'id': self.id}
        return bytes(json.dumps(serialized_json), 'utf-8')

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @classmethod
    def from_json(cls, parsed_data):
        c = Command()
        c.name = parsed_data.get('name', None)
        if not c.name:
            raise InvalidCommandJson('Command name must be set')
        c.data = parsed_data.get('data', None)
        c.id = parsed_data.get('id', None)
        return c


class InvalidCommandJson(ValueError):
    pass


class CommandHandler:
    def __init__(self):
        self.__logger = RaspilotLogger.get_logger()

    @abstractmethod
    def run_action(self, command):
        pass

    @property
    def logger(self):
        return self.__logger
