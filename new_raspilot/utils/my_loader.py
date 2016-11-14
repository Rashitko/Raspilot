from new_raspilot.core.utils.base_module_load_strategy import BaseModuleLoadStrategy
from new_raspilot.utils.config_reader import ConfigReader


class MyLoader(BaseModuleLoadStrategy):
    @staticmethod
    def load(module):
        return ConfigReader.instance().module_enabled(module) and module.load()
