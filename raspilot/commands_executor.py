class CommandsExecutor:
    """
    Executes commands if they have a callable associated with their name.
    """

    def __init__(self):
        """
        Creates a new 'CommandsExecutor' with empty dict of commands and associated actions.
        :return: returns nothing
        """
        self.__commands = {}

    def bind_command(self, command, action):
        """
        Associates the command and the callable action. Upon receiving of the command, the action will be called.
        If command is already bound, the action is replaced.
        :param command: command to bind to
        :param action: action to execute, should be callable
        :return: returns nothing
        """
        self.__commands[command] = action

    def unbind_command(self, command):
        """
        Unbinds the command. If command is not bound, nothing is changed.
        :param command: command to unbind from
        :return: return command or None, if command is not bound
        """
        return self.__commands.pop(command, None)

    def execute_command(self, command, data):
        """
        If command is bound, then executes the action. If any Exception is thrown during the execution, its caught and
        CommandExecutionError is risen.
        :param command: command which should be executed
        :param data: additional data for the command
        """
        try:
            action = self.__commands.get(command, None)
            if action:
                # noinspection PyCallingNonCallable
                action()
        except Exception as e:
            raise CommandExecutionError(e)


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
