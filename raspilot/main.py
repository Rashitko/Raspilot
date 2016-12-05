import os

from up.utils.up_loader import UpLoader
from up.utils.up_logger import UpLogger

from raspilot.utils.raspilot_loader import RaspilotLoader

MODULES_PATH = 'modules'
MODULES_PREFIX = 'raspilot.modules.'
RECORDERS_PATH = 'recorders'
RECORDERS_PREFIX = 'raspilot.recorders.'
FLIGHT_CONTROLLER_PATH = 'flight_controller'
FLIGHT_CONTROLLER_PREFIX = 'raspilot.flight_controller.'


if __name__ == "__main__":
    logger = UpLogger.get_logger()
    current_dir = os.path.dirname(__file__)
    modules_path = os.path.abspath(os.path.join(current_dir, MODULES_PATH))
    recorders_path = os.path.abspath(os.path.join(current_dir, RECORDERS_PATH))
    flight_controller_path = os.path.abspath(os.path.join(current_dir, FLIGHT_CONTROLLER_PATH))
    try:
        with (UpLoader(modules_path=modules_path, modules_prefix=MODULES_PREFIX, recorders_path=recorders_path,
                       recorders_prefix=RECORDERS_PREFIX, flight_controller_path=flight_controller_path,
                       flight_controller_prefix=FLIGHT_CONTROLLER_PREFIX)
                      .create(load_condition_class=RaspilotLoader)) as raspilot:
            raspilot.run()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Stopping Raspilot")
