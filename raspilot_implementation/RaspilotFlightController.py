import logging
import time
from threading import Thread

from raspilot.flight_controller import FlightController

ERRORS_LIMIT = 10
SECONDS_TO_MILLIS = 1000


class RaspilotFlightController(FlightController):
    FLIGHT_MODES = {'FULL_RX': 0, 'STABILISATION': 1, 'RTH': 2, 'WAYPOINTS': 3}

    def __init__(self, control_loop_sleep=20):
        super().__init__()
        self.__control_loop_sleep = control_loop_sleep / SECONDS_TO_MILLIS
        self.__run = False
        self.__logger = logging.getLogger('raspilot.log')
        self.__flight_mode = self.FLIGHT_MODES['FULL_RX']
        self.__errors = 0
        self.__control_dropped = False

    def start(self):
        self.__run = True
        Thread(target=self.__control_loop, name="FLIGHT_CONTROLLER_THREAD").start()
        return True

    def stop(self):
        self.__run = False

    def __control_loop(self):
        total_errors_count = 0
        while self.__run:
            try:
                channels = self.__read_rx()
                if self.__flight_mode > self.FLIGHT_MODES['FULL_RX']:
                    orientation = self.__read_orientation()
                if self.__flight_mode > self.FLIGHT_MODES['STABILISATION']:
                    gps = self.__read_gps()

            except ProviderError as provider_error:
                total_errors_count += 1
                self.__logger.error("{} cannot be None".format(provider_error.provider.__class__.__name__))
            except ProviderValuesError as provider_value_error:
                total_errors_count += 1
                self.__logger.error(
                        "{} gives invalid data. The data were {}".format(
                            provider_value_error.provider.__class__.__name__,
                            provider_value_error.values))
            except Exception as e:
                total_errors_count += 1
                self.__logger.error(e)
            finally:
                if not self.__control_dropped and total_errors_count >= ERRORS_LIMIT:
                    self.__flight_mode = self.FLIGHT_MODES['FULL_RX']
                    self.__control_dropped = True
                    self.__logger.fatal(
                            "Too many errors if flight controller, dropping to full RX CONTROL mode. Future errors "
                            "will be ignored")
                time.sleep(self.__control_loop_sleep)

    def __read_rx(self):
        """
        Tries to read orientation from the RXProvider. If RXProvider is not available or returns invalid value,
        an Exception is risen.
        :return: valid RX channels values
        """
        rx_provider = self.raspilot.rx_provider
        self.__validate_provider(rx_provider)
        channels = rx_provider.get_channels()
        self.__validate_values(rx_provider, channels)
        return channels

    def __read_orientation(self):
        """
        Tries to read orientation from the OrientationProvider. If OrientationProvider is not available or returns
        invalid value, an Exception is risen.
        :return: valid orientation data
        """
        orientation_provider = self.raspilot.orientation_provider
        self.__validate_provider(orientation_provider)
        orientation = orientation_provider.current_orientation()
        self.__validate_values(orientation_provider, orientation)
        return orientation

    def __read_gps(self):
        """
        Tries to read orientation from the GPSProvider. If GPSProvider is not available or returns invalid value, an
        Exception is risen.
        :return: valid GPS data
        """
        gps_provider = self.raspilot.gps_provider
        self.__validate_provider(gps_provider)
        gps = gps_provider.location
        self.__validate_values(gps)
        return gps

    def __validate_provider(self, provider):
        """
        Returns true if provider is not None or if the control has been previously dropped.
        :param provider: provider to be tested
        :raises: ProviderException if provider is None and control hasn't been previously dropped
        :return: True if provider is not None or the control has been previously dropped
        """
        if not provider and not self.__control_dropped:
            raise ProviderError(provider)
        return provider or self.__control_dropped

    def __validate_values(self, provider, values):
        """
        Returns true if values are not None or if the control has been previously dropped.
        :param provider: provider which are the data read from
        :param values: values to be tested
        :raises: ProviderValuesError if provider is None and control hasn't been previously dropped
        :return: True if provider is not None or the control has been previously dropped
        """
        if not values and not self.__control_dropped:
            raise ProviderValuesError(provider, values)
        return values or self.__control_dropped


class ProviderError(Exception):
    def __init__(self, provider):
        self.__provider = provider

    @property
    def provider(self):
        return self.__provider


class ProviderValuesError(Exception):
    def __init__(self, provider, values):
        self.__values = values
        self.__provider = provider

    @property
    def values(self):
        return self.__values

    @property
    def provider(self):
        return self.__provider
