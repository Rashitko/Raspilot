import importlib
import inspect
import os

from new_raspilot.core.base_module import BaseModule
from new_raspilot.core.base_system_state_recorder import BaseSystemStateRecorder
from new_raspilot.core.flight_controller.base_flight_controller import BaseFlightController
from new_raspilot.core.raspilot import Raspilot
from new_raspilot.core.utils.raspilot_logger import RaspilotLogger


class RaspilotLoader:
    MODULES_PATH = '../../modules/'
    MODULES_MODULE_PREFIX = 'new_raspilot.modules.'

    RECORDERS_PATH = '../../recorders/'
    RECORDERS_MODULE_PREFIX = 'new_raspilot.recorders.'

    FLIGHT_CONTROLLER_PATH = '../../flight_controller/'
    FLIGHT_CONTROLLER_MODULE_PREFIX = 'new_raspilot.flight_controller.'

    def __init__(self):
        self.__logger = RaspilotLogger.get_logger()

    @staticmethod
    def __module_module_filter(name, klass):
        return not name.startswith('__') and issubclass(klass, BaseModule)

    @staticmethod
    def __recorders_filter(name, klass):
        return not name.startswith('__') and issubclass(klass, BaseSystemStateRecorder)

    @staticmethod
    def __flight_controller_filter(name, klass):
        return not name.startswith('__') and issubclass(klass, BaseFlightController)

    def create(self, raspilot_class=Raspilot):
        """
        Loads all Raspilot modules which are specified in the '{raspilot}/modules/' folder. The Raspilot module is
        loaded if it subclasses the BaseModule and has the load flag set.
        :param raspilot_class: Raspilot class, if custom Raspilot implementation is used. The class is instantiated via
        constructor with one parameter, the Raspilot modules array
        :return: newly created Raspilot instance
        :rtype: Raspilot
        """
        modules_folder = self.__get_modules_folder()
        if not modules_folder:
            return None
        raspilot_modules = []
        self.__load_modules(RaspilotLoader.MODULES_MODULE_PREFIX, modules_folder, raspilot_modules,
                            self.__module_module_filter)
        recorders_folder = self.__get_recorders_folder()
        if not recorders_folder:
            return None
        raspilot_recorders = []
        self.__load_modules(RaspilotLoader.RECORDERS_MODULE_PREFIX, recorders_folder, raspilot_recorders,
                            self.__recorders_filter)
        flight_controller_folder = self.__get_flight_controller_folder()
        flight_controllers = []
        self.__load_modules(RaspilotLoader.FLIGHT_CONTROLLER_MODULE_PREFIX, flight_controller_folder,
                            flight_controllers, self.__flight_controller_filter)
        if flight_controllers:
            if len(flight_controllers) > 1:
                self.__logger.warning(
                    "More than one FlightController specified. Using the {}".format(flight_controllers[0].class_name))
            return raspilot_class(raspilot_modules, raspilot_recorders, flight_controllers[0])
        else:
            self.__logger.warning("FlightController not found")
            return raspilot_class(raspilot_modules, raspilot_recorders)

    @staticmethod
    def __load_modules(module_prefix, folder, modules_list, module_filter):
        for module_file in os.listdir(folder):
            if not module_file.startswith('__') and module_file.endswith('.py'):
                file_name_limit = module_file.index('.')
                module_name = module_file[0:file_name_limit]
                modules_module = importlib.import_module(module_prefix + module_name)
                RaspilotLoader.__process_module(modules_module, modules_list, module_filter)

    @staticmethod
    def __process_module(modules_module, raspilot_modules, module_filter):
        """
        Processes the classes specified in the module. Only subclasses of the BaseModule are added to the
        raspilot_modules list
        :param modules_module: module to load classes from
        :param raspilot_modules: array of Raspilot modules, where instances of all relevant modules should be appended
        :return: None
        :rtype: None
        """
        # noinspection SpellCheckingInspection
        for name, klass in inspect.getmembers(modules_module):
            if module_filter(name, klass):
                RaspilotLoader.__process_raspilot_module(klass, name, raspilot_modules)

    # noinspection SpellCheckingInspection
    @staticmethod
    def __process_raspilot_module(klass, name, raspilot_modules):
        """
        Adds the klass to the globals() under the 'name' key. Instantiates the Raspilot module and adds the instance to
        the 'raspilot_modules' list if the load flag is set. Flag is checked via invocating the load() on the module
        instance.
        :param klass: class of the Raspilot module
        :param name: string name of the Raspilot module
        :param raspilot_modules: list of Raspilot module instances, which has the load flag set
        :return: None
        :rtype: None
        """
        globals()[name] = klass
        try:
            module = klass()
            if module.load():
                raspilot_modules.append(module)
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

    def __get_recorders_folder(self):
        """
        :return: string path to the modules folder, or None if the folder was newly created
        :rtype: str
        """
        modules_path = os.path.join(os.path.dirname(__file__), RaspilotLoader.RECORDERS_PATH)
        modules_path = os.path.abspath(modules_path)
        self.__logger.debug('Looking for recorders in {}'.format(modules_path))
        if not os.path.exists(modules_path):
            self.__logger.error(
                "Recorders dir not found. Dir was created, please place your modules there and start Raspilot again")
            os.makedirs(modules_path)
            return None
        return modules_path

    def __get_flight_controller_folder(self):
        """
        :return: string path to the modules folder, or None if the folder was newly created
        :rtype: str
        """
        modules_path = os.path.join(os.path.dirname(__file__), RaspilotLoader.FLIGHT_CONTROLLER_PATH)
        modules_path = os.path.abspath(modules_path)
        self.__logger.debug('Looking for flight controller in {}'.format(modules_path))
        if not os.path.exists(modules_path):
            self.__logger.error(
                "Flight Controller dir not found. Dir was created, please place your modules there and start Raspilot "
                "again")
            os.makedirs(modules_path)
            return None
        return modules_path


if __name__ == '__main__':
    loader = RaspilotLoader()
    loader.create()
