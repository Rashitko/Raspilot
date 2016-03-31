import logging


def nop(data, request):
    pass


class BaseCommandHandler:
    """
    Class used in CommandsExecutor. Wraps command name and desired action.
    """

    def __init__(self, name):
        """
        Creates a new 'BaseCommandHandler'. This class must be subclassed.
        :param name: name of the command
        :return: returns nothing
        """
        self.__logger = logging.getLogger('raspilot.log')
        if name is None:
            ValueError('Name must be set')
        self.__name = name

    def execute_action(self, data, command_id, request, response, raspilot):
        """
        Runs the action. If any error is thrown, it is caught and an ActionExecution error is thrown instead.
        :param data: additional data for the command
        :param command_id: id of the command
        :param request: request flag
        :param response: response object which contains additional information about the request execution, can be None
        @param raspilot Raspilot instance
        @type raspilot Raspilot
        :return: returns an ActionResult object
        """
        try:
            return self._run_action(data, command_id, request, response, raspilot)
        except Exception as e:
            self.__logger.error(
                "An error during action execution occurred. Command name was {}, data were {}, command_id was {},"
                " request was {}, error was {}".format(self.name, data, command_id, request, e))
            raise ActionExecutionError(e)

    def _run_action(self, data, command_id, request, response, raspilot):
        """
        Runs the action. The default implementation rises the NotImplementedError. All subclasses should override
        this method.
        :param data: additional data
        :param command_id: id of the command
        :param request: request flag
        :param response: response object which contains additional information about the request execution, can be None
        :return: returns an ActionResult object
        """
        raise NotImplementedError()

    @property
    def name(self):
        return self.__name


class ActionExecutionError(Exception):
    """
    Exception is thrown if an error during action execution occurs.
    """

    def __init__(self, exception):
        """
        Creates new 'ActionExecutionError' with given exception.
        :param exception: exception which causes this ActionExecutionError
        :return: returns nothing
        """
        self.__exception = exception

    @property
    def exception(self):
        return self.__exception
