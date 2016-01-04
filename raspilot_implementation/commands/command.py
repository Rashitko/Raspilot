from raspilot.commands.command import Command


class RaspilotCommand(Command):
    TARGET_ANDROID = 'android'
    TARGET_WEBSOCKET = 'websocket'

    def __init__(self, name, data, request, response, target=TARGET_ANDROID):
        data['target'] = target
        super().__init__(name, data, request, response)