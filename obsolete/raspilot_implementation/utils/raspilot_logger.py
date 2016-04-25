import datetime
import logging
import os
import sys

from colorlog import ColoredFormatter

TRANSMISSION_LEVEL_NUM = 9
date_format = "%Y-%m-%d %H:%M:%S"


class RaspilotLoggerFactory:
    @staticmethod
    def create(logger_name, level, path):
        logging.addLevelName(TRANSMISSION_LEVEL_NUM, "TRANSMISSION")
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        if not os.path.exists(path):
            os.makedirs(path)
        fh = logging.FileHandler("{}{}-{}.log".format(path, logger_name, datetime.datetime.now().strftime("%Y-%m-%d")))
        fh.setLevel(level)
        message_format = '%(log_color)s[%(levelname)s] %(asctime)s%(reset)s\n\t''%(message)s\n\t''[FILE]%(pathname)s:%(lineno)s\n\t''[THREAD]%(threadName)s'
        formatter = ColoredFormatter(message_format, date_format)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False
        return logger
