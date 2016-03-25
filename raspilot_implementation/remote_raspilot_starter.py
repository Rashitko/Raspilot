from raspilot.starter import Starter


class RemoteRaspilotStarter(Starter):
    """
    Custom Starter for the remote Raspilot. Disables the providers specified in the
    RemoteRaspilotStarter.DISABLED_PROVIDERS
    """

    DISABLED_PROVIDERS = ['RaspilotRXProvider', 'RaspilotFlightController', 'RaspilotServoController',
                          'RaspilotWebsocketsProvider']
    """
    Class names of the providers which are not started
    """

    def should_start(self, provider, raspilot):
        """
        For disabled providers specified in the RemoteRaspilotStarter.DISABLED_PROVIDERS returns False. Otherwise the
        result of the super is returned.
        :param provider: starting provider
        :param raspilot: raspilot instance
        :return: False for providers specified in the DISABLED_PROVIDERS, result of the super otherwise
        """
        provider_name = provider.__class__.__name__
        if provider_name in RemoteRaspilotStarter.DISABLED_PROVIDERS:
            return False
        return super().should_start(provider, raspilot)
