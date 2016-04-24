import importlib
import inspect
import os

from new_raspilot.raspilot_framework.base_module import BaseModule
from new_raspilot.raspilot_framework.base_started_module import BaseStartedModule
from new_raspilot.raspilot_framework.raspilot import Raspilot
from new_raspilot.raspilot_framework.utils.raspilot_logger import RaspilotLogger


class RaspilotLoader:
    LOG_MESSAGE_END_LIMIT = -2
    """
    Removes the \n\t from the last log message
    """
    MODULES_PATH = '../../modules/'
    """
    Path to folder, where Raspilot modules are stored
    """

    def __init__(self):
        self.__logger = RaspilotLogger.get_logger()

    def load(self, raspilot_class=Raspilot):
        """
        Loads all Raspilot modules which are specified in the '{raspilot}/modules/' folder. The Raspilot module is
        loaded if it subclasses the BaseModule and has the load flag set.
        :param raspilot_class: Raspilot class, if custom Raspilot implementation is used. The class is instantiated via
        constructor with one parameter, the Raspilot modules array
        :return: newly created Raspilot instance
        :rtype: Raspilot
        """
        modules_folder = self.__get_modules_folder()
        raspilot_modules = []
        messages = []
        for module_file in os.listdir(modules_folder):
            if not module_file.startswith('__') and module_file.endswith('.py'):
                file_name_limit = module_file.index('.')
                module_name = module_file[0:file_name_limit]
                modules_module = importlib.import_module('new_raspilot.modules.' + module_name)
                RaspilotLoader.__process_module(messages, modules_module, raspilot_modules)
        log_message = ''
        for message in messages:
            log_message += message
        self.__logger.info(log_message[:RaspilotLoader.LOG_MESSAGE_END_LIMIT])
        return raspilot_class(raspilot_modules)

    @staticmethod
    def __process_module(messages, modules_module, raspilot_modules):
        """
        Processes the classes specified in the module. Only subclasses of the BaseModule are added to the
        raspilot_modules list
        :param messages: array of string which are logged after the load of all modules
        :param modules_module: module to load classes from
        :param raspilot_modules: array of Raspilot modules, where instances of all relevant modules should be appended
        :return: None
        :rtype: None
        """
        # noinspection SpellCheckingInspection
        for name, klass in inspect.getmembers(modules_module):
            if not name.startswith('__') and issubclass(klass, BaseModule):
                RaspilotLoader.__process_raspilot_module(klass, messages, name, raspilot_modules)

    # noinspection SpellCheckingInspection
    @staticmethod
    def __process_raspilot_module(klass, messages, name, raspilot_modules):
        """
        Adds the klass to the globals() under the 'name' key. Instantiates the Raspilot module and adds the instance to
        the 'raspilot_modules' list if the load flag is set. Flag is checked via invocating the load() on the module
        instance.
        :param klass: class of the Raspilot module
        :param messages: array of string which are logged after the load of all modules
        :param name: string name of the Raspilot module
        :param raspilot_modules: list of Raspilot module instances, which has the load flag set
        :return: None
        :rtype: None
        """
        globals()[name] = klass
        try:
            module = klass()
            if module.load():
                if issubclass(klass, BaseStartedModule):
                    messages.append("Started module {} found\n\t".format(name))
                else:
                    messages.append("Module {} found\n\t".format(name))
                raspilot_modules.append(module)
            else:
                messages.append(
                    "Skipping module {} because it does not have the load flag set\n\t".format(name))
        except TypeError:
            pass

    def __get_modules_folder(self):
        """
        :return: string path to the modules folder, or None if the folder was newly created
        :rtype: str
        """
        modules_path = os.path.join(os.path.dirname(__file__), RaspilotLoader.MODULES_PATH)
        modules_path = os.path.abspath(modules_path)
        self.__logger.debug('Looking for modules in {}'.format(modules_path))
        if not os.path.exists(modules_path):
            self.__logger.error(
                "Modules dir not found. Dir was created, please place your modules there and start Raspilot again")
            os.makedirs(modules_path)
            return None
        return modules_path


if __name__ == '__main__':
    loader = RaspilotLoader()
    loader.load()
