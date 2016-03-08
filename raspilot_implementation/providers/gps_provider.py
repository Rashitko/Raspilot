import logging

from raspilot.providers.gps_provider import GPSProvider, GPSProviderConfig
from raspilot_implementation.commands.gps_location_handler import GPSLocationHandler

PROVIDER_KEY = 'provider'

ACCURACY_KEY = 'accuracy'

ALTITUDE_KEY = 'altitude'

LONGITUDE_KEY = 'longitude'

LATITUDE_KEY = 'latitude'


class RaspilotGPSProvider(GPSProvider):
    """
    Custom implementation of the GPSProvider which is used in cooperation with the Android device.
    """

    def __init__(self, config):
        super().__init__(config)
        self.__logger = logging.getLogger('raspilot.log')

    def start(self):
        """
        Adds a command handler for gps messages passed via the AndroidProvider.
        :return: True, but situations when AndroidProvider fails to start may occur
        """
        self.raspilot.add_command_handler(GPSLocationHandler(self))
        return True

    def on_data_received(self, data):
        """
        Handler method, which creates a GPSLocation from provided data and if this data are valid, then sets
        the GPSLocation so it can be later retrieved.
        :param data: data which should contain the gps location
        :return: returns True if location was set, False otherwise
        """
        location = GPSLocation.create(data)
        self.__logger.debug('Received location: {}'.format(location))
        if location:
            self._location = location
            return True
        return False


class RaspilotGPSProviderConfig(GPSProviderConfig):
    pass


class GPSLocation:
    """
    Wrapper class for the GPS location provided by an Android device
    """

    def __init__(self):
        """
        Creates a new 'GPSLocation' with all attributes set as None. Use the class method create(data) to create
        GPSLocation with attributes initialized with the data provided by Android.
        :return:
        """
        self.__latitude = None
        self.__longitude = None
        self.__altitude = None
        self.__accuracy = None
        self.__provider = None

    def to_json(self):
        return {LATITUDE_KEY: self.latitude, LONGITUDE_KEY: self.longitude, ALTITUDE_KEY: self.altitude,
                ACCURACY_KEY: self.accuracy, PROVIDER_KEY: self.provider}

    @property
    def latitude(self):
        return self.__latitude

    @property
    def longitude(self):
        return self.__longitude

    @property
    def altitude(self):
        return self.__altitude

    @property
    def accuracy(self):
        return self.__accuracy

    @property
    def provider(self):
        return self.__provider

    @classmethod
    def create(cls, data):
        """
        Constructs new GPSLocation from provided data. If the data are not valid, None is returned. Otherwise a
        GPSLocation with specified data is returned.
        :param data: dict to construct GPSLocation from. Mandatory keys are 'lat', 'long', 'alt', 'acc', 'prov'.
        :return: if the data are not valid, None is returned, otherwise a GPSLocation with specified data is returned
        """
        if not data or not GPSLocation.__data_valid(data):
            return None
        gps_location = GPSLocation()
        gps_location.__latitude = data.get(LATITUDE_KEY, None)
        gps_location.__longitude = data.get(LONGITUDE_KEY, None)
        gps_location.__altitude = data.get(ALTITUDE_KEY, None)
        gps_location.__accuracy = data.get(ACCURACY_KEY, None)
        gps_location.__provider = data.get(PROVIDER_KEY, None)
        return gps_location

    @staticmethod
    def __data_valid(data):
        """
        Validates the provided dict whether it contains all the mandatory fields. Mandatory fields are
        'lat', 'long', 'alt', 'acc', 'prov'.
        :param data: dict to by validated.
        :return: True if data are valid, False otherwise
        """
        return data and LATITUDE_KEY in data and LONGITUDE_KEY in data and ALTITUDE_KEY in data and ACCURACY_KEY in data and PROVIDER_KEY in data
