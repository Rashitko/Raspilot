from new_raspilot.core.utils.raspilot_loader import RaspilotLoader
from new_raspilot.core.utils.raspilot_logger import RaspilotLogger
from new_raspilot.utils.my_loader import MyLoader

if __name__ == "__main__":
    logger = RaspilotLogger.get_logger()
    try:
        with (RaspilotLoader().create(load_condition_class=MyLoader)) as raspilot:
            raspilot.run()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Stopping Raspilot")
