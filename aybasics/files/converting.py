import os
import threading
from aybasics import logger
__all__ = ["csv_to_json", "xml_to_json", "xls_to_json", "json_to_csv", "json_to_xlsx"]


class _Convert(threading.Thread):
    def __init__(self, file, function, **kwargs):
        threading.Thread.__init__(self)
        self.file = file
        self.function = function
        self.setName(file)
        self.kwargs = kwargs
        logger.info(self.kwargs)
        self.start()

    def run(self):
        self.function(self.file, **self.kwargs)


def _get_files(path, file_type):
    """
    Returns all files for concerting as a list.
    If a single file is provided as path, returns single file in list
     Parameters
    ----------
    path : str
        a path containing the files for conversion
    file_type : str
        the filename ending specifying the file type
    Returns
    -------
    files : list
        a list of all relative file directories
    """

    absolute_path = os.path.abspath(path)
    if os.path.isdir(path):
        absolute_path += "/"
        files = [absolute_path + file for file in os.listdir(path) if file_type in file.split(".")[-1]]
        if not files:
            raise ValueError("No files with this Ending")
        logger.info("Number of files: {}".format(len(files)))
    else:
        if file_type not in path.split(".")[-1]:
            raise IOError("Wrong file_type! Expected {}, given {}".format(file_type, path.split(".")[-1]))
        files = [absolute_path]
    logger.info("Files for converting: {}".format([file.split("/")[-1] for file in files]))
    return files, absolute_path


def _start_threads(path, file_type, function, **kwargs):
    files, absolute_path = _get_files(path, file_type)
    threads = dict()
    for file in files:
        # threads[file] = _Convert(file, inspect.stack()[1].function)
        threads[file] = _Convert(file, function, **kwargs)
    for thread in threads:
        threads[thread].join()
    return files, absolute_path


def _register_csv_dialect(**kwargs):
    import csv
    from . import csv_dialect_options
    if not all(key in csv_dialect_options for key in kwargs.keys()):
        raise KeyError("only these keys for csv dialect are allowed: {}".format(csv_dialect_options))
    csv.register_dialect("custom", **kwargs)


def csv_to_json(path, direct_data_use=False, null_value="delete", main_key_position=0, header_line=0, **kwargs):
    # ToDo add support for header in other row than 0: if int: use this row, if str: search for this word
    """
    Converts files from csv to json

    Parameters
    ----------
    path : str
        path of files or file
    direct_data_use : bool
        if data is supposed to be used directly after converting, the data is returned as a dictionary
    null_value
        the value to fill the key if no value in csv file. If "delete", key in json not being present
    main_key_position : int
        the position in csv file for the main key for this row
    header_line : int
        if the header is not in the first row, select row here. WARNING: all data above this line will not be parsed
    Returns
    -------
    data : dict
        dictionary containing the jsons
    """
    from ._converting import _csv_to_json
    if kwargs:
        _register_csv_dialect(**kwargs)
        # ToDo add support for builtin dialects

    # converting
    files, path = _start_threads(path, "csv", _csv_to_json, null_value=null_value, main_key_position=main_key_position,
                                 dialect="custom" if kwargs else None, header_line=header_line)

    # loading converted files
    if direct_data_use:
        from .load import load_json
        data = load_json([file.replace(".csv", ".json") for file in files])
        if len(data.keys()) == 1:
            return list(data.values())[0]
        return {key.replace(path, ""): value for key, value in data.items()}


def xml_to_json(path, direct_data_use=False, list_reduction=False, manual_selection=False):
    """

    Parameters
    ----------
    path : str
        path of files or file
    direct_data_use : bool
        if data is supposed to be used directly after converting, the data is returned as a dictionary
    list_reduction : {bool, list}
        if multiple keys on same hierarchy level the function tries to reduce the lists by creating a virtual dictionary
        key with unique values: key_of_list-unique_key_in_dicts_in_list
        if a list is provided, this list is used for selecting the keys in the dictionaries. the list is level based,
        so top-level keys need to be first, lowest level keys need to be last.
    manual_selection : bool
        if the selection of the leading keys for list reduction shall be picked by hand
        no effect if list_reduction : False


    Returns
    -------
    data : dict
        dictionary containing the jsons


    """
    from ._converting import _xml_to_json

    files, path = _start_threads(path, "xml", _xml_to_json, list_reduction=list_reduction, manual_selection=manual_selection)

    # loading converted files
    if direct_data_use:
        from .load import load_json
        data = load_json([file.replace("xml", "json") for file in files])
        if len(data.keys()) == 1:
            return list(data.values())[0]
        return {key.replace(path, ""): value for key, value in data.items()}


def xls_to_json(path):
    """
    Converts Microsoft Excel xls or xlsx files to json

    Parameters
    ----------
    path

    Returns
    -------

    """
    files = _get_files(path, "xls")

    return dict()


def json_to_csv(path, key_name, order=None, direct_data_use=False, if_empty_value=None, key_position=0, **kwargs):
    """

    Parameters
    ----------
    path : str
        path to json file or directory with json files
    key_name : str
        the name of the json keys
    order : dict {int: [str, int, float]}
        for defining a specific order of the
    direct_data_use : bool
        if the csv rows are wanted for immediate further use
    if_empty_value
        the value to set when no data is available
    key_position : int
        the position in csv of the json key

    Returns
    -------

    rows : [list, dict]
        a list of rows representing the csv file (if multiple files in a dictionary with filename as key)

    """
    from ._converting import _json_to_csv

    if kwargs:
        _register_csv_dialect(**kwargs)
        # ToDo add support for builtin dialects

    # converting
    files, path = _start_threads(path, "json", _json_to_csv,
                                 key_name=key_name, dialect="custom" if kwargs else None,
                                 key_position=key_position, if_empty_value=if_empty_value, order=order)

    # loading converted files
    if direct_data_use:
        from .load import load_csv
        data = load_csv([file.replace("json", "csv") for file in files], dialect="custom" if kwargs else None)
        if isinstance(data, list):
            return list(data)
        return {key.replace(path, ""): value for key, value in data.items()}


def json_to_xlsx(path):
    """

    Parameters
    ----------
    path

    Returns
    -------

    """
    files = _get_files(path, "json")

    return
