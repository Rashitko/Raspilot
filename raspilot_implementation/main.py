import configparser
import datetime
import logging
from threading import Thread

from raspilot.raspilot import RaspilotBuilder
from raspilot_implementation.commands.commands_executor import RaspilotCommandsExecutor
from raspilot_implementation.notifier.RaspilotNotifier import RaspilotNotifier
from raspilot_implementation.providers.android_provider import AndroidProvider, AndroidProviderConfig
from raspilot_implementation.providers.gps_provider import RaspilotGPSProvider, RaspilotGPSProviderConfig
from raspilot_implementation.providers.orientation_provider import (RaspilotOrientationProvider,
                                                                    RaspilotOrientationProviderConfig)
from raspilot_implementation.providers.rx_provider import RaspilotRXProvider, RaspilotRXConfig
from raspilot_implementation.providers.websocket_provider import RaspilotWebsocketsProvider, RaspilotWebsocketsConfig
from raspilot_implementation.servo.servo_controller import RaspilotServoController, RaspilotServoControllerConfig

TRANSMISSION_LEVEL_NUM = 9
FILE_LOGGER = 'raspilot.log'


class RaspilotConfig:
    """
    Reads the config file.
    """

    def __init__(self):
        """
        Constructs a new 'RaspilotConfig' and reads the config file and initializes self with the config file
        information.
        :return: returns nothing
        """
        cfg = configparser.ConfigParser()
        cfg.read('config.cfg')

        self.__username = cfg['AUTHENTICATION']['Username']
        self.__password = cfg['AUTHENTICATION']['Password']
        self.__device_identifier = cfg['AUTHENTICATION']['Device identifier']

        self.__default_protocol = cfg['DEFAULT']['Protocol']
        self.__server_address = cfg['DEFAULT']['Address']
        self.__default_port = cfg['DEFAULT']['Protocol']
        self.__base_url = "{}://{}:{}".format(self.__default_protocol, self.__server_address, self.__default_protocol)

        self.__websockets_port = cfg['WEBSOCKETS']['Port']
        self.__websockets_path = cfg['WEBSOCKETS']['Address']
        self.__websockets_protocol = cfg['WEBSOCKETS']['Protocol']
        self.__websockets_url = "{}://{}:{}/{}".format(self.__websockets_protocol, self.__server_address,
                                                       self.__websockets_port, self.__websockets_path)
        self.__retry_count = cfg.getint('WEBSOCKETS', 'Retries')
        self.__retry_delay = cfg.getint('WEBSOCKETS', 'Retry delay')

        self.__orientation_port = cfg.getint('ANDROID', 'Port for orientation data')
        self.__general_port = cfg.getint('ANDROID', 'Port for general data')

        self.__updates_namespace = cfg['TELEMETRY']['Updates namespace']
        self.__updates_freq = cfg.getint('TELEMETRY', 'Updates frequency')
        self.__updates_error_limit = cfg.getint('TELEMETRY', 'Error limit')

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def default_protocol(self):
        return self.__default_protocol

    @property
    def server_address(self):
        return self.__server_address

    @property
    def base_url(self):
        return self.__base_url

    @property
    def websockets_port(self):
        return self.__websockets_port

    @property
    def websockets_path(self):
        return self.__websockets_path

    @property
    def websockets_protocol(self):
        return self.__websockets_protocol

    @property
    def websockets_url(self):
        return self.__websockets_url

    @property
    def retry_count(self):
        return self.__retry_count

    @property
    def retry_delay(self):
        return self.__retry_delay

    @property
    def device_identifier(self):
        return self.__device_identifier

    @property
    def orientation_port(self):
        return self.__orientation_port

    @property
    def general_port(self):
        return self.__general_port

    @property
    def updates_namespace(self):
        return self.__updates_namespace

    @property
    def updates_freq(self):
        return self.__updates_freq

    @property
    def updates_error_limit(self):
        return self.__updates_error_limit


def start_raspilot(rasp):
    rasp.start()


def init_logger():
    logging.addLevelName(TRANSMISSION_LEVEL_NUM, "TRANSMISSION")
    logger = logging.getLogger('raspilot.log')
    logger.setLevel(TRANSMISSION_LEVEL_NUM)
    fh = logging.FileHandler("raspilog-{}.log".format(datetime.datetime.now()))
    fh.setLevel(TRANSMISSION_LEVEL_NUM)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s\n\t'
                                  '%(message)s\n\t'
                                  '[FILE]%(pathname)s:%(lineno)s\n\t',
                                  "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.debug('Logging initialized')


if __name__ == "__main__":
    init_logger()
    builder = RaspilotBuilder()
    config = RaspilotConfig()

    # Websockets provider initialization
    websockets_config = RaspilotWebsocketsConfig(config)
    provider = RaspilotWebsocketsProvider(websockets_config)
    builder.websockets_provider = provider

    # RX provider initialization
    rx_config = RaspilotRXConfig()
    rx_provider = RaspilotRXProvider(rx_config)
    builder.rx_provider = rx_provider

    # Orientation provider initialization
    orientation_config = RaspilotOrientationProviderConfig(config.orientation_port)
    orientation_provider = RaspilotOrientationProvider(orientation_config)
    builder.orientation_provider = orientation_provider

    # GPS provider initialization
    gps_config = RaspilotGPSProviderConfig()
    gps_provider = RaspilotGPSProvider(gps_config)
    builder.gps_provider = gps_provider

    # Servo controller initialization
    servo_controller_config = RaspilotServoControllerConfig()
    servo_controller = RaspilotServoController(servo_controller_config)
    builder.servo_controller = servo_controller

    # Android provider initialization
    android_provider = AndroidProvider(AndroidProviderConfig(config.general_port))
    builder.add_custom_provider(android_provider)

    # Commands executor
    commands_executor = RaspilotCommandsExecutor(android_provider)
    builder.commands_executor = commands_executor

    # Notifier initialization
    builder.notifier = RaspilotNotifier(config.updates_namespace, config.updates_freq, config.updates_error_limit)

    raspilot = builder.build()
    raspilot_thread = Thread(None, start_raspilot, None, (raspilot,))
    raspilot_thread.start()
    raspilot.wait_for_init_complete()
    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        raspilot.stop()
