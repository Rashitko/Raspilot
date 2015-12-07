import logging
from queue import Queue
from threading import RLock, Thread

from raspilot.commands.command import Command
from raspilot.commands.response import CommandResponse


class CommandsExecutor:
    """
    Executes commands if they have a callable associated with their name.
    """

    def __init__(self):
        """
        Creates a new 'CommandsExecutor' with empty dict of commands and associated actions.
        :return: returns nothing
        """
        self.__logger = logging.getLogger('raspilot.log')
        self.__commands = {}
        self.__execute_lock = RLock()
        self.__send_lock = RLock()
        self.__queue = Queue()
        self.__running = True
        self.__thread = Thread(target=self.__message_loop, name="COMMANDS_EXECUTOR_MESSAGE_THREAD")
        self.messages_thread.start()

    def stop(self):
        self.__logger.debug("Stopping the commands executor")
        self.__running = False
        self.__queue.put(None, False)

    def __message_loop(self):
        while self.__running:
            command = self.__queue.get()
            if command:
                self._transmit_message(command)
            self.__queue.task_done()

    def add_command_handler(self, command_handler):
        """
        Adds new command handler. Should be a subclass of the BaseCommandHandler
        :param command_handler: new command handler
        :return:
        """
        self.__commands[command_handler.name] = command_handler

    def remove_command_handler(self, command_name):
        """
        Removes the command handler. If command handler has not been added previously, nothing is changed.
        :param command_name: name of the command, which handler will be removed
        :return: returns command handler or None, if command is not bound
        """
        return self.__commands.pop(command_name, None)

    def execute_command(self, command_name, data, command_id, request, response):
        """
        If command is bound, executes the action.
        :param command_name: name of the command which should be executed
        :param data: additional data for the command
        :param command_id: id of the command
        :param request: flag whether the command is a request which should be responded to
        :param response: response object which contains additional information about the request execution, can be None
        :return: returns nothing
        :raises: raspilot.commands.base_command_handler.ActionExecutionError if any error occurs during the action
        execution
        """
        handler = self.__commands.get(command_name, None)
        if handler:
            with self.__execute_lock:
                handler.execute_action(data, command_id, request, response)

    def notify_command_failed(self, command_name, data, command_id, response):
        """
        :param command_name: name of the command which execution fails
        :param data: data provided for the command, might be None
        :param command_id: id of the command
        :param response: response object which contains additional information about the request execution,
                         might be None
        """
        self.send_message(command_name, None, False, CommandResponse(command_id, False, data))

    def send_message(self, command_name, data, request, response):
        """
        Constructs general message object from provided data and adds it to the send queue.
        :param command_name: name of the command which should be sent
        :param data: data for the command, might be None
        :param request: flag, whether the command is a request
        :param response: response object, contains additional information about the request execution, might be None
        :return: returns True if message was sent, False otherwise
        """
        self.__queue.put(Command(command_name, data, request, response))

    def _transmit_message(self, command):
        """
        Sends the command.
        :param command: command to be sent
        :return: returns True if transmission was successful False otherwise
        """
        return False

    @property
    def running(self):
        return self.__running

    @property
    def messages_thread(self):
        return self.__thread


class CommandExecutionError(Exception):
    """
    Error thrown when an Exception is risen during command execution.
    """

    def __init__(self, error):
        """
        Creates a new 'CommandExecutionError' with the specified exception.
        :param error: Exception which caused this error
        :return: returns nothing
        """
        self.__error = error

    @property
    def error(self):
        return self.__error


class MessageTransmitter:
    def __init__(self):
        self.__queue = Queue()
