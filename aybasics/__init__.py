__author__ = "Jan Lukas Braje"
import sys
from loguru import logger

from aybasics.files.converting import *
from aybasics.files._converting import _json_to_pandas_data_frame
from aybasics.files.load import *
from aybasics.files.write import *
from aybasics.files.converting import dict_to_csv, xlsx_to_json, xls_to_json, xlsx_to_dict, xls_to_dict




def basic_log(log_level=5):
    # ToDo add thread name to style
    # Todo create different styles (one with threading one without)
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
