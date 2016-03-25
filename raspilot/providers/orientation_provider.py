import logging

from raspilot.providers.base_provider import BaseProvider, BaseProviderConfig


class OrientationProvider(BaseProvider):
    """
    Base Orientation Provider. This provider is used to get the device orientation. Usually and roll, pitch and yaw
    angles are obtain from the current_orientation method, but the custom implementation could return other values with
    different meaning.
    """

    def __init__(self, config):
        """
        Creates a new 'OrientationProvider' with specified config.
        :param config: config used to modify this provider
        :return: returns nothing
        """
        super().__init__(config)
        self.__logger = logging.getLogger('raspilot.log')

    def current_orientation(self):
        """
        Returns the current orientation or None. The returned type depends on the implementation. Default implementation
        returns None
        :return: returns the current orientation. Default implementation returns None
        """
        return None

    def set_neutral(self):
        """
        Current orientation will be saved as if the device roll and pitch will be equal to 0.
        :return: returns True if operation was successful, False otherwise
        """
        return False


class OrientationProviderConfig(BaseProviderConfig):
    pass
