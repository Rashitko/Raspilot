import configparser
import logging
import os
import socket
from threading import Thread

from twisted.internet import reactor

from raspilot.black_box import BlackBoxController, BlackBoxControllerConfig
from raspilot_implementation.black_box.black_box import RaspilotBlackBox
from raspilot_implementation.commands.ahi_command_handler import SetNeutralAhiHandler
from raspilot_implementation.commands.commands_executor import RaspilotCommandsExecutor
from raspilot_implementation.commands.exit_command_handler import ExitCommandHandler
from raspilot_implementation.notifier.RaspilotNotifier import RaspilotNotifier
from raspilot_implementation.providers.android_provider import AndroidProvider, AndroidProviderConfig
from raspilot_implementation.providers.flight_control_provider import RaspilotFlightControlProvider, \
    RaspilotFlightControlConfig
from raspilot_implementation.providers.gps_provider import RaspilotGPSProvider, RaspilotGPSProviderConfig
from raspilot_implementation.providers.orientation_provider import (RaspilotOrientationProvider,
                                                                    RaspilotOrientationProviderConfig)
from raspilot_implementation.providers.rx_provider import RaspilotRXProvider, RaspilotRXConfig
from raspilot_implementation.raspilot_alarmist import RaspilotAlarmist, RaspilotAlarmistConfig
from raspilot_implementation.raspilot_flight_controller import RaspilotFlightController
from raspilot_implementation.raspilot_impl import RaspilotImplBuilder
from raspilot_implementation.remote_raspilot_starter import RemoteRaspilotStarter
from raspilot_implementation.utils.raspilot_logger import RaspilotLoggerFactory

LOGS_DIR_PATH = '../logs/'

date_format = "%Y-%m-%d %H:%M:%S"

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
        dir = os.path.dirname(__file__)
        config_file = os.path.join(dir, './config.cfg')
        print('Loading config from {}'.format(os.path.abspath(config_file)))
        cfg.read(config_file)

        self.__username = cfg['AUTHENTICATION']['Username']
        self.__password = cfg['AUTHENTICATION']['Password']
        self.__device_identifier = cfg['AUTHENTICATION']['Device identifier']

        self.__default_protocol = cfg['DEFAULT']['Protocol']
        self.__server_address = cfg['DEFAULT']['Address']
        self.__default_port = cfg['DEFAULT']['Protocol']
        self.__base_url = "{}://{}:{}".format(self.__default_protocol, self.__server_address, self.__default_protocol)
        self.__logging_level = cfg['DEFAULT']['Logging level']
        self.__logs_path = cfg['DEFAULT']['Logs Path']
        self.__discovery_port = cfg.getint('DEFAULT', 'Discovery port')
        self.__discovery_reply_port = cfg.getint('DEFAULT', 'Discovery reply port')

        self.__websockets_port = cfg.getint('WEBSOCKETS', 'Port')
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

        self.__baud_rate = cfg.getint('ARDUINO', 'Baud rate')

        self.__black_box_delay = cfg.getint('BLACK BOX', 'Recording delay') / 1000

        self.__panic_threshold = cfg.getint('UTILIZATION', 'Panic Threshold')
        self.__calm_down_threshold = cfg.getint('UTILIZATION', 'Calm Down Threshold')
        self.__utilization_delay = cfg.getint('UTILIZATION', 'Check Delay') / 1000
        self.__panic_delay = cfg.getint('UTILIZATION', 'Panic Delay') / 1000
        self.__calm_down_delay = cfg.getint('UTILIZATION', 'Calm Down Delay') / 1000

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

    @property
    def logging_level(self):
        return self.__logging_level

    @property
    def logs_path(self):
        return self.__logs_path

    @property
    def discovery_port(self):
        return self.__discovery_port

    @property
    def discovery_reply_port(self):
        return self.__discovery_reply_port

    @property
    def baud_rate(self):
        return self.__baud_rate

    @property
    def black_box_delay(self):
        return self.__black_box_delay

    @property
    def panic_threshold(self):
        return self.__panic_threshold

    @property
    def calm_down_threshold(self):
        return self.__calm_down_threshold

    @property
    def utilization_delay(self):
        return self.__utilization_delay

    @property
    def panic_delay(self):
        return self.__panic_delay

    @property
    def calm_down_delay(self):
        return self.__calm_down_delay


def logging_level_name_to_value(level_name):
    """
    For the specified logging level name returns the logging level int value. If an unspecified or invalid level is
    provided, logging.DEBUG is returned
    :param level_name: string representation of the level name
    :return: int value of the level name
    """
    level_name = level_name.upper()
    if level_name == 'DEBUG':
        return logging.DEBUG
    elif level_name == 'INFO':
        return logging.INFO
    elif level_name == 'ERROR':
        return logging.ERROR
    elif level_name == 'TRANSMISSION':
        return TRANSMISSION_LEVEL_NUM
    else:
        return logging.DEBUG


def start_raspilot(rasp):
    """
    Starts the Raspilot.
    :param rasp: Raspilot instance
    :return: returns nothing
    """
    rasp.start()


def init_logger(level, logs_path):
    """
    Initializes the Raspilot logger.
    :param level: logging level of the created logger
    :return: returns nothing
    """
    RaspilotLoggerFactory.create('raspilot.log', level, logs_path)
    # logging.addLevelName(TRANSMISSION_LEVEL_NUM, "TRANSMISSION")
    # logger = logging.getLogger('raspilot.log')
    # logger.setLevel(level)
    # if not os.path.exists(logs_path):
    #     os.makedirs(logs_path)
    # fh = logging.FileHandler("{}raspilog-{}.log".format(logs_path, datetime.datetime.now().strftime("%Y-%m-%d")))
    # fh.setLevel(level)
    # message_format = '%(log_color)s[%(levelname)s] %(asctime)s%(reset)s\n\t''%(message)s\n\t''[FILE]%(pathname)s:%(lineno)s\n\t''[THREAD]%(threadName)s'
    # formatter = ColoredFormatter(message_format, date_format)
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # ch = logging.StreamHandler(sys.stdout)
    # ch.setLevel(logging.DEBUG)
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)
    # logger.propagate = False


def create_raspilot():
    global raspilot
    config = RaspilotConfig()
    dir = os.path.dirname(__file__)
    log_dir = os.path.join(dir, config.logs_path)
    init_logger(config.logging_level, log_dir)
    builder = RaspilotImplBuilder(config.discovery_port, config.discovery_reply_port)
    builder.starter = RemoteRaspilotStarter()
    # Websockets provider initialization
    websockets_config = RaspilotFlightControlConfig(config.server_address, config.websockets_port)
    provider = RaspilotFlightControlProvider(websockets_config)
    builder.websockets_provider = provider
    # RX provider initialization
    rx_config = RaspilotRXConfig(config.baud_rate)
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
    # Android provider initialization
    android_provider = AndroidProvider(AndroidProviderConfig(config.general_port))
    builder.add_custom_provider(android_provider)
    # Commands executor
    commands_executor = RaspilotCommandsExecutor(android_provider)
    commands_executor.add_command_handler(SetNeutralAhiHandler(orientation_provider))
    builder.commands_executor = commands_executor
    # Notifier initialization
    builder.notifier = RaspilotNotifier(config.updates_namespace, config.updates_freq, config.updates_error_limit)
    # Flight controller initialization
    builder.flight_controller = RaspilotFlightController()
    # BlackBox controller initialization
    black_box_controller_config = BlackBoxControllerConfig()
    black_box_controller_config.delay = config.black_box_delay
    black_box_controller_config.black_box = RaspilotBlackBox()
    builder.black_box_controller = BlackBoxController(black_box_controller_config)
    # Alarmist initialization
    alarmist_config = RaspilotAlarmistConfig()
    alarmist_config.panic_threshold = config.panic_threshold
    alarmist_config.calm_down_threshold = config.calm_down_threshold
    alarmist_config.delay = config.utilization_delay
    alarmist_config.panic_delay = config.panic_delay
    alarmist_config.calm_down_delay = config.calm_down_delay
    builder.alarmist = RaspilotAlarmist(alarmist_config)
    raspilot = builder.build()
    return raspilot




def run_raspilot(runner=None):
    Thread(target=reactor.run, args=(False,)).start()
    raspilot = create_raspilot()
    raspilot.add_command_handler(ExitCommandHandler('system.exit'))
    raspilot_thread = Thread(target=start_raspilot, args=(raspilot,), name="RASPILOT_THREAD")
    raspilot_thread.start()
    try:
        raspilot.wait_for_init_complete()
        if runner:
            runner.raspilot_ready()
        raspilot_thread.join()
    except KeyboardInterrupt:
        if runner:
            runner.exit()
    finally:
        raspilot.stop()
        notify_runner()


if __name__ == "__main__":
    run_raspilot()
