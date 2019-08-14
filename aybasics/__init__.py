__author__ = "Jan Lukas Braje"
import sys
from loguru import logger

from aybasics.files.converting import *
from aybasics.files.load import *


class IntWithIndex(int):
    def __new__(cls, value, index):
        return super(IntWithIndex, cls).__new__(cls, value)

    def __init__(self, value, index):
        super().__init__()
        self.index = index

    def __iter__(self):
        return iter((self, self.index))


def basic_log(log_level=5):
    style = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | " \
            "<magenta>{name}</magenta>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logger.remove()
    logger.add(sys.stderr, level=log_level, format=style)
    return logger


log = basic_log()


# def my_max(array, return_arg=False):
#     maximum = np.max(array)
#     index = np.argmax(array)
#     return IntWithIndex(maximum, index)
