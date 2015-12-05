import logging

from raspilot.commands.commands_executor import CommandsExecutor


class RaspilotCommandsExecutor(CommandsExecutor):

    def __init__(self, android_provider):
        """
        Creates a new 'RaspilotCommandsExecutor' with specified android provider. Used to communicate with Android
        device.
        :param android_provider: AndroidProvider which will be used to transmit messages. Must be set
        :return: returns nothing
        """
        if android_provider is None:
            ValueError("Android provider must be set")
        super().__init__()
        self.__logger = logging.getLogger('raspilot.log')

    def _transmit_message(self, command):
        """
        Current implementation only logs the message.
        :param command: command to be sent
        :return: returns True if transmission was successful, False otherwise
        """
        self.__logger.debug(command.serialize())
        return True
