import unittest

from raspilot.commands.base_command_handler import BaseCommandHandler, ActionExecutionError
from raspilot.commands.command import Command
from raspilot_implementation.commands.commands_executor import RaspilotCommandsExecutor
from raspilot_implementation.commands.ahi_command import SetNeutralAhiHandler


class CommandExecutorTests(unittest.TestCase):
    def setUp(self):
        self.commands_executor = RaspilotCommandsExecutor(False)
        self.dummy_handler = BaseCommandHandler("dummy")
        self.ahi_handler = SetNeutralAhiHandler(None)

    def test_none_android_provider(self):
        with self.assertRaises(ValueError):
            RaspilotCommandsExecutor(None)

    def test_executor_stopped(self):
        executor = RaspilotCommandsExecutor(False)
        executor.stop()
        executor.messages_thread.join()
        self.assertFalse(executor.running, "Commands executor should be stopped")

    def test_execute_nonbound(self):
        self.assertIsNone(self.commands_executor.execute_command('dummy', None, None, None, None))

    def test_remove_handler(self):
        self.commands_executor.add_command_handler(self.dummy_handler)
        self.assertEqual(self.dummy_handler, self.commands_executor.remove_command_handler('dummy'))

    def test_dummy_execution(self):
        self.commands_executor.add_command_handler(self.dummy_handler)
        with self.assertRaises(ActionExecutionError):
            self.commands_executor.execute_command("dummy", None, None, None, None)
        self.commands_executor.remove_command_handler(self.dummy_handler)

    def test_adding_handler(self):
        self.assertIsNone(self.commands_executor.add_command_handler(self.dummy_handler), "Adding dummy handler")

    def test_executor_running(self):
        self.assertTrue(self.commands_executor.running, "Commands executor running")

    def test_notify_command_failed(self):
        self.commands_executor.notify_command_failed('dummy', None, None, None)

    def test_transmit_message(self):
        self.assertTrue(self.commands_executor._transmit_message(Command('dummy', {'customInt': 123}, True, None)))

    def test_neutral_ahi_provider(self):
        self.commands_executor.add_command_handler(self.ahi_handler)
        with self.assertRaises(ActionExecutionError):
            self.commands_executor.execute_command('ahi.set_neutral', None, None, None, None)

    def tearDown(self):
        self.commands_executor.stop()
