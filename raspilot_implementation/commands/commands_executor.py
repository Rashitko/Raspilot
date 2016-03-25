import logging

from raspilot.commands.commands_executor import CommandsExecutor
from raspilot_implementation.commands.command import RaspilotCommand
from raspilot_implementation.providers.android_provider import AndroidProvider
from raspilot_implementation.websockets.websocket_event import WebsocketEvent


class RaspilotCommandsExecutor(CommandsExecutor):
    def __init__(self, android_provider):
        """
        Creates a new 'RaspilotCommandsExecutor' with specified android provider. Used to communicate with Android
        device.
        :param android_provider: AndroidProvider which will be used to transmit messages. Must be set
        :return: returns nothing
        """
        if android_provider is None:
            raise ValueError("Android provider must be set")
        super().__init__()
        self.__logger = logging.getLogger('raspilot.log')

    def _transmit_message(self, command):
        """
        Current implementation only logs the message.
        :param command: command to be sent
        :return: returns True if transmission was successful, False otherwise
        """
        if command.data.get('target', None) == RaspilotCommand.TARGET_ANDROID:
            self.__transmit_to_android(command)
        elif command.data.get('target', None) == RaspilotCommand.TARGET_WEBSOCKET:
            if self.raspilot.websocket_provider:
                self.raspilot.websocket_provider.send_message(WebsocketEvent(command))
        else:
            self.__transmit_to_android(command)

        return True

    def __transmit_to_android(self, command):
        android_provider = self.raspilot.named_provider(AndroidProvider.NAME)
        if android_provider:
            android_provider.send_command(command)
