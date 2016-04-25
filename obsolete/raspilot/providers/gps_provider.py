from obsolete.raspilot.providers import BaseProvider, BaseProviderConfig


class GPSProvider(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        self.__location = None

    @property
    def location(self):
        return self._location

    @property
    def _location(self):
        return self.__location

    @_location.setter
    def _location(self, value):
        self.__location = value


class GPSProviderConfig(BaseProviderConfig):
    pass
