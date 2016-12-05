from up.utils.config_reader import ConfigReader
from up.utils.base_module_load_strategy import BaseModuleLoadStrategy


class RaspilotLoader(BaseModuleLoadStrategy):
    @staticmethod
    def load(module):
        return ConfigReader.instance().module_enabled(module) and module.load()
