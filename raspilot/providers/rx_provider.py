from raspilot.providers.base_provider import BaseProvider, BaseProviderConfig


class RXProvider(BaseProvider):

    def __init__(self, config):
        if config is None:
            raise ValueError("Config must be set")
        super().__init__(config)


class RXConfig(BaseProviderConfig):

    def __init__(self):
        BaseProviderConfig.__init__(self)

