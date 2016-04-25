import unittest

from obsolete.raspilot.commands import Command, NAME_KEY, DATA_KEY, REQUEST_KEY, RESPONSE_KEY
from obsolete.raspilot.commands import CommandResponse


class CommandsTests(unittest.TestCase):
    def test_serialization(self):
        name = 'cmd_name'
        data = {'customInt': 123}
        request = True
        response = CommandResponse(123, False)
        cmd = Command(name, data, request, response)
        self.assertEqual(cmd.serialize(),
                         {NAME_KEY: name, DATA_KEY: data, RESPONSE_KEY: response.serialize(), REQUEST_KEY: request})

    def test_deserialization(self):
        name = 'cmd_name'
        data = {'customInt': 123}
        request = True
        response = CommandResponse(123, False, {'asd': 123})
        cmd = Command(name, data, request, response)
        loaded_cmd = Command.from_json(cmd.serialize())
        self.assertEqual(loaded_cmd.name, name)
        self.assertEqual(loaded_cmd.data, data)
        self.assertEqual(loaded_cmd.response.serialize(), CommandResponse(123, False, {'asd': 123}).serialize())
        self.assertEqual(loaded_cmd.request, request)
