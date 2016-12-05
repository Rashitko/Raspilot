from up.commands.command import BaseCommand


class OrientationCommand(BaseCommand):
    NAME = 'arduino.orientation'

    def __init__(self, roll, pitch, yaw):
        super().__init__(self.NAME, {'roll': roll, 'pitch': pitch, 'yaw': yaw})

    @property
    def roll(self):
        return self.data['roll']

    @property
    def pitch(self):
        return self.data['pitch']

    @property
    def yaw(self):
        return self.data['yaw']
