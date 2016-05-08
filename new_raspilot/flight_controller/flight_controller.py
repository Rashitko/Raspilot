import time

from new_raspilot.core.flight_controller.base_flight_controller import BaseFlightController
from new_raspilot.utils.pid_ported import Pid
from new_raspilot.utils.value_mapper import ValueMapper


class RaspilotFlightController(BaseFlightController):
    MAX_ROLL_ANGLE = 45
    MAX_PITCH_ANGLE = 45
    MIN_PWM = 1000
    MAX_PWM = 2000
    MIN_ANGLE = 0
    MAX_ANGLE = 180
    STAB_CONSTRAINT = 250
    RATE_CONSTRAINT = 500

    def __init__(self):
        super().__init__()
        self.__ail_pid_rate = Pid(0.7, 0, 0, 50)
        self.__ail_pid_stab = Pid(4.5, 0, 0, 50)
        self.__ele_pid_rate = Pid(0.7, 0, 0, 50)
        self.__ele_pid_stab = Pid(4.5, 0, 0, 50)

    def _notify_loop(self):
        while self._run:
            raw_roll = self._rx_provider.ailerons
            rcroll = ValueMapper.map(raw_roll, self.MIN_PWM, self.MAX_PWM, -self.MAX_ROLL_ANGLE, self.MAX_ROLL_ANGLE)
            roll = 0
            roll_stab_output = self.__ail_pid_stab.get_pid(rcroll - roll, 1)
            roll_stab_output = self.__constraint(roll_stab_output, -self.STAB_CONSTRAINT, self.STAB_CONSTRAINT)
            gyro_roll = 0
            roll_output = self.__ail_pid_rate.get_pid(roll_stab_output - gyro_roll, 1)
            roll_output = self.__constraint(roll_output, -self.RATE_CONSTRAINT, self.RATE_CONSTRAINT)
            roll_angle = ValueMapper.map((raw_roll + roll_output), self.MIN_PWM, self.MAX_PWM, self.MIN_ANGLE,
                                         self.MAX_ANGLE)

            raw_pitch = self._rx_provider.elevator
            rcpitch = ValueMapper.map(raw_pitch, self.MIN_PWM, self.MAX_PWM, -self.MAX_PITCH_ANGLE,
                                      self.MAX_PITCH_ANGLE)
            pitch = 0
            pitch_stab_output = self.__ele_pid_stab.get_pid(rcpitch - pitch, 1)
            pitch_stab_output = self.__constraint(pitch_stab_output, -self.STAB_CONSTRAINT, self.STAB_CONSTRAINT)
            gyro_pitch = 0
            pitch_output = self.__ele_pid_rate.get_pid(pitch_stab_output - gyro_pitch, 1)
            pitch_output = self.__constraint(pitch_output, -self.RATE_CONSTRAINT, self.RATE_CONSTRAINT)
            pitch_angle = ValueMapper.map((raw_pitch + pitch_output), self.MIN_PWM, self.MAX_PWM, self.MIN_ANGLE,
                                          self.MAX_ANGLE)
            time.sleep(0.02)

    @staticmethod
    def __constraint(roll_stab_output, min_value, max_value):
        if roll_stab_output > max_value:
            return max_value
        if roll_stab_output < min_value:
            return min_value
        return roll_stab_output
