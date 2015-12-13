from raspilot.commands.execution_response import ExecutionResponse


class RaspilotExecutionResponse(ExecutionResponse):
    ANDROID_CHANNEL = 'android'
    WEBSOCKET_CHANNEL = 'websocket'

    def __init__(self, success, source_id, data, response_channel=ANDROID_CHANNEL):
        """
        Creates a new 'ExecutionResponse' with the specified attributes. Instance must be serialized using the serialize
        method in order to be sent as a JSON message.
        :param success: boolean flag, if the operation was successfully executed
        :param source_id: command id to which this message responds
        :param data: additional data
        :param response_channel: will be used later to decide which communication channel use whether the Android socket
        or the Websocket
        :return: returns nothing
        """
        super().__init__(success, source_id, data)
        self.__response_channel = response_channel

    @property
    def response_channel(self):
        return self.__response_channel
