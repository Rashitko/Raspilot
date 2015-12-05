import unittest

from raspilot.tests.commands_executor_tests import CommandExecutorTests
from raspilot.tests.commands_tests import CommandsTests


class RaspilotTestSuite(unittest.TestSuite):
    def __init__(self):
        super().__init__([CommandExecutorTests, CommandsTests])
