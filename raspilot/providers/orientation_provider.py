from raspilot.providers.base_provider import BaseProvider, BaseProviderConfig


class OrientationProvider(BaseProvider):
    def current_orientation(self):
        """
        Returns the current orientation or None. The returned type depends on the implementation. Default implementation
        returns None
        :return: returns the current orientation. Default implementation returns None
        """
        return None


class OrientationProviderConfig(BaseProviderConfig):
    pass
