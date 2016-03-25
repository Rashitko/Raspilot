from raspilot.providers.base_provider import BaseProvider, BaseProviderConfig


class RXProvider(BaseProvider):
    def __init__(self, config):
        if config is None:
            raise ValueError("Config must be set")
        super().__init__(config)

    def get_channels(self):
        """
        Returns tuple of all channel values.
        :return: tuple of all channel values, might be empty
        """
        return []

    def get_channel_value(self, channel):
        """
        Returns value of particular channel or None, if no such channel is available
        :param channel: channel to get value of
        :return: value of the channel or None if no such channel is available
        """
        return None

    def get_channels_count(self):
        """
        Returns the channel count which are read with this RXProvider.
        :return: number of channels read by this RXProvider
        """
        return 0


class RXConfig(BaseProviderConfig):
    def __init__(self):
        BaseProviderConfig.__init__(self)
