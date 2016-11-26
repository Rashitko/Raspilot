import configparser
import os

from new_raspilot.utils.singleton import Singleton


class ConfigReader(metaclass=Singleton):
    MODULES_CONFIG_PATH = '../config/modules.cfg'
    GLOBAL_CONFIG_PATH = '../config/config.cfg'

    def __init__(self):
        current_path = os.path.dirname(__file__)

        self.__modules_config_path = os.path.abspath(os.path.join(current_path, self.MODULES_CONFIG_PATH))
        self.__modules_config = configparser.ConfigParser(allow_no_value=True)
        self.__modules_config.read(self.__modules_config_path)

        self.__global_config_path = os.path.abspath(os.path.join(current_path, self.GLOBAL_CONFIG_PATH))
        self.__global_config = configparser.ConfigParser(allow_no_value=True)
        self.__global_config.read(self.__global_config_path)

    def module_enabled(self, module):
        module_name = module.__class__.__name__
        if module_name in self.__modules_config['DISABLED MODULES']:
            return False
        return True

    @property
    def global_config(self):
        return self.__global_config

    @staticmethod
    def instance():
        return ConfigReader()
