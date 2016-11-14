from new_raspilot.core.commands.command import BaseCommand


class RXUpdateCommand(BaseCommand):
    NAME = 'arduino.rx'

    def __init__(self, ail, ele, thr, rud):
        super().__init__(self.NAME, {'ail': ail, 'ele': ele, 'thr': thr, 'rud': rud})

    @property
    def ailerons(self):
        return self.data['ail']

    @property
    def elevator(self):
        return self.data['ele']

    @property
    def throttle(self):
        return self.data['thr']

    @property
    def rudder(self):
        return self.data['rud']
