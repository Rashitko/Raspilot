import configparser
import os

from new_raspilot.core.utils.raspilot_logger import RaspilotLogger
from new_raspilot.utils.singleton import Singleton


class ConfigReader(metaclass=Singleton):
    DEFAULT_CONFIG_PATH = '../config/modules.cfg'

    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        current_path = os.path.dirname(__file__)
        config_path = config_path
        self.__modules_config_path = os.path.abspath(os.path.join(current_path, config_path))

        self.__modules_config = configparser.ConfigParser(allow_no_value=True)
        self.__modules_config.read(self.__modules_config_path)

    def module_enabled(self, module):
        module_name = module.__class__.__name__
        if module_name in self.__modules_config['DISABLED MODULES']:
            RaspilotLogger.get_logger().info("%s DISABLED in %s" % (module_name, self.__modules_config_path))
            return False
        return True

    @staticmethod
    def instance(config_path=DEFAULT_CONFIG_PATH):
        return ConfigReader(config_path)
