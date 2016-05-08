import time


class Pid:
    def __init__(self, kp, kd, ki, imax):
        self.__last_time = None
        self.__kp = kp
        self.__kd = kd
        self.__ki = ki
        self.__imax = imax
        self.__last_derivative = None
        self.__last_time = None
        self.__last_error = 0
        self.__integrator = 0

    def get_pid(self, error, scaler):
        now = time.time() * 1000
        if self.__last_time:
            dt = now - self.__last_time
        output = 0
        delta_time = None
        # FIXME dt migh be referenced before assignment
        if self.__last_time is None or dt > 1000:
            # if this PID hasn't been used for a full second then zero
            # the intergator term. This prevents I buildup from a
            # previous fight mode from causing a massive return before
            # the integrator gets a chance to correct itself
            dt = 0
            self.__reset_i()
        self.__last_time = now
        delta_time = dt / 1000.0
        output += error * self.__kp

        # Compute derivative component if time has elapsed
        if abs(self.__kd) > 0 and dt > 0:
            derivative = 0

            if self.__last_derivative is None:
                # we've just done a reset, suppress the first derivative
                # term as we don't want a sudden change in input to cause
                # a large D output change
                derivative = 0
                self.__last_derivative = 0
            else:
                derivative = (error - self.__last_error) / delta_time

            # discrete low pass filter, cuts out the
            # high frequency noise that can drive the controller crazy
            # float RC = 1/(2*M_PI*_fCut);
            # derivative = _last_derivative +
            #              ((delta_time / (RC + delta_time)) *
            #               (derivative - _last_derivative));

            # update state
            self.__last_error = error
            self.__last_derivative = derivative

            # add in derivative component
            output += self.__kd * derivative

        # scale the P and D components
        output *= scaler

        # Compute integral component if time has elapsed
        if (abs(self.__ki) > 0) and (dt > 0):
            self.__integrator += (error * self.__ki) * scaler * delta_time
            if self.__integrator < -self.__imax:
                self.__integrator = -self.__imax
            elif self.__integrator > self.__imax:
                self.__integrator = self.__imax
            output += self.__integrator
        return output

    def __reset_i(self):
        self.__integrator = 0
        self.__last_derivative = 0
