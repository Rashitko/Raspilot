import configparser
import os

import pid
from pid import PidFile
from up.utils.config_reader import ConfigReader
from up.utils.up_loader import UpLoader
from up.utils.up_logger import UpLogger

from raspilot.utils.raspilot_loader import RaspilotLoader

MODULES_PATH = 'modules'
MODULES_PREFIX = 'raspilot.modules'
RECORDERS_PATH = 'recorders'
RECORDERS_PREFIX = 'raspilot.recorders'
FLIGHT_CONTROLLER_PATH = 'flight_controller'
FLIGHT_CONTROLLER_PREFIX = 'raspilot.flight_controller'

if __name__ == "__main__":
    logger = UpLogger.get_logger()
    config = ConfigReader.instance().global_config
    pid_dir = None
    pid_name = None
    try:
        pid_dir = config.get('DEFAULT', 'PID DIR')
        pid_name = config.get('DEFAULT', 'PID NAME', fallback='raspilot')
    except configparser.NoOptionError as e:
        logger.critical("The option '%s' under [%s] is required. Please add it in the %s" % (
            e.args[0].upper(), e.args[1], ConfigReader.instance().global_config_path))
        exit(1)

    current_dir = os.path.dirname(__file__)
    modules_path = os.path.abspath(os.path.join(current_dir, MODULES_PATH))
    recorders_path = os.path.abspath(os.path.join(current_dir, RECORDERS_PATH))
    flight_controller_path = os.path.abspath(os.path.join(current_dir, FLIGHT_CONTROLLER_PATH))
    if '~' in pid_dir:
            pid_dir = os.path.join(os.path.expanduser(pid_dir[pid_dir.index('~'):]))
    try:
        with PidFile(piddir=pid_dir, pidname=pid_name):
            with (UpLoader(modules_path=modules_path, modules_prefix=MODULES_PREFIX, recorders_path=recorders_path,
                           recorders_prefix=RECORDERS_PREFIX, flight_controller_path=flight_controller_path,
                           flight_controller_prefix=FLIGHT_CONTROLLER_PREFIX).create(
                load_condition_class=RaspilotLoader)) as raspilot:
                raspilot.run()
    except pid.PidFileAlreadyLockedError:
        logger.critical("Another instance of Raspilot is already running. Check %s." % os.path.join(pid_dir, pid_name))
        exit(2)
    except KeyboardInterrupt:
        pass
    logger.info("Stopping Raspilot")
