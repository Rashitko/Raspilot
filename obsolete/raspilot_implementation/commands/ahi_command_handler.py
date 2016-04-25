from raspilot_implementation.commands.execution_response import RaspilotExecutionResponse

from obsolete.raspilot.commands import BaseCommandHandler

AHI_SET_NEUTRAL_COMMAND_NAME = "ahi.set_neutral"


class SetNeutralAhiHandler(BaseCommandHandler):
    """
    Handler for setting the neutral AHI.
    """

    def __init__(self, orientation_provider):
        """
        Creates a new 'SetNeutralAhiHandler'. This handler is associated with the name 'ahi.set_neutral'
        :return: returns nothing
        """
        super().__init__(AHI_SET_NEUTRAL_COMMAND_NAME)
        self.__orientation_provider = orientation_provider

    def _run_action(self, data, command_id, request, response, raspilot):
        """
        Sets the current orientation as the neutral position of the plane, when both roll and pitch will be equal to 0
        :param data: currently not processed
        :return: returns response object containing the information whether the operation was successful or None,
        if the response should not be send
        """
        return RaspilotExecutionResponse(self.__orientation_provider.set_neutral(), command_id,
                                         RaspilotExecutionResponse.ANDROID_CHANNEL)
