import datetime
import logging
import os
import sys

from colorlog import ColoredFormatter


class RaspilotLogger:
    LOGGER_NAME = 'raspilot.log'
    TRANSMISSION_LEVEL_NUM = 9
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LEVEL = 'INFO'
    PATH = '../../../logs/'

    initialized = False

    @staticmethod
    def __initialize():
        logging.addLevelName(RaspilotLogger.TRANSMISSION_LEVEL_NUM, "TRANSMISSION")
        logger = logging.getLogger(RaspilotLogger.LOGGER_NAME)
        logger.setLevel(RaspilotLogger.LEVEL)
        dir = os.path.dirname(__file__)
        path = os.path.join(dir, RaspilotLogger.PATH)
        if not os.path.exists(path):
            os.makedirs(path)
        fh = logging.FileHandler("{}{}-{}.log".format(path, RaspilotLogger.LOGGER_NAME,
                                                      datetime.datetime.now().strftime("%Y-%m-%d")))
        fh.setLevel(RaspilotLogger.LEVEL)
        message_format = '--------------------------->\n%(log_color)s[%(levelname)s] %(asctime)s%(reset)s\n\t''%(message)s\n\t''[FILE]%(pathname)s:%(lineno)s\n\t''[THREAD]%(threadName)s\n<---------------------------\n\n'
        formatter = ColoredFormatter(message_format, RaspilotLogger.DATE_FORMAT)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False
        RaspilotLogger.initialized = True

    @staticmethod
    def get_logger():
        if not RaspilotLogger.initialized:
            RaspilotLogger.__initialize()
        return logging.getLogger(RaspilotLogger.LOGGER_NAME)
