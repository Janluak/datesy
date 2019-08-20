import os
import threading
from aybasics import logger

__all__ = ["csv_to_json", "xml_to_json", "xls_to_json", "xlsx_to_json", "json_to_csv", "dict_to_csv", "json_to_xlsx"]


class _ConvertThread(threading.Thread):
    def __init__(self, memory, file, save_to_file, function, **kwargs):
        threading.Thread.__init__(self)
        self.file = file
        self.function = function
        self.setName(file)
        self.memory = memory
        self.save_to_file = save_to_file
        self.kwargs = kwargs
        logger.info(self.kwargs)
        self.start()

    def run(self):
        self.function(self.file, self.memory if self.memory else False, self.save_to_file, **self.kwargs)


class _FileConversion:
    def __init__(self, path, file_type, function, save_to_file, **kwargs):
        self.path = path
        self._get_files(file_type)
        self.threads = dict()
        self.lock = threading.Lock()
        self.lock.acquire()
        self.__data = dict()
        for file in self.files:
            self.__data[file] = None
            self.threads[file] = _ConvertThread(memory=self.__data, save_to_file=save_to_file, file=file,
                                                function=function, **kwargs)
        for thread in self.threads:
            self.threads[thread].join()
        self.lock.release()

    def _get_files(self, file_type):
        """
        Returns all files for concerting as a list.
        If a single file is provided as path, returns single file in list
         Parameters
        ----------
        file_type : str
            the filename ending specifying the file type
        Returns
        -------
        files : list
            a list of all relative file directories
        """
        # ToDo get files in a class for direct allocation of results and opt for
        self._absolute_path = os.path.abspath(self.path)
        if os.path.isdir(self.path):
            self._absolute_path += "/"
            self.files = [self.absolute_path + file for file in os.listdir(self.path) if
                          file_type in file.split(".")[-1]]
            if not self.files:
                raise ValueError("No files with this Ending")
            logger.info("Number of files: {}".format(len(self.files)))
        else:
            if file_type not in self.path.split(".")[-1]:
                raise IOError("Wrong file_type! Expected {}, given {}".format(file_type, self.path.split(".")[-1]))
            self.files = [self._absolute_path]
        logger.info("Files for converting: {}".format([file.split("/")[-1] for file in self.files]))

    @property
    def data(self):
        self.lock.acquire()
        self.lock.release()
        if len(self.__data.keys()) == 1:
            return list(self.__data.values())[0]
        return {key[len(key) - len(self.path):]: value for key, value in self.__data.items()}

    @property
    def file_names(self):
        return self.files

    @property
    def absolute_path(self):
        return self._absolute_path


def _register_csv_dialect(**kwargs):
    import csv
    csv_dialect_options = {i for i in set(dir(csv.Dialect)) if "__" not in i}
    if not all(key in csv_dialect_options for key in kwargs.keys()):
        raise KeyError("only these keys for csv dialect are allowed: {}\nGiven keys: {}".format(csv_dialect_options,
                                                                                                kwargs.keys()))
    csv.register_dialect("custom", **kwargs)


def csv_to_json(path, save_to_file=False, null_value="delete", main_key_position=0, header_line=0, **kwargs):
    # ToDo add support for finding header row automatically
    # ToDo add support for inverse csv writing
    """
    Converts files from csv to json

    Parameters
    ----------
    path : str
        path of files or file
    save_to_file : bool
        if data is supposed to be saved to file
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
    conversion = _FileConversion(path, "csv", _csv_to_json, null_value=null_value, main_key_position=main_key_position,
                                 dialect="custom" if kwargs else None, header_line=header_line,
                                 save_to_file=save_to_file)

    return conversion.data


def xml_to_json(path, save_to_file=False, list_reduction=False, manual_selection=False):
    """

    Parameters
    ----------
    path : str
        path of files or file
    save_to_file : bool
        if data is supposed to be saved to file
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

    conversion = _FileConversion(path, "xml", _xml_to_json, list_reduction=list_reduction,
                                 manual_selection=manual_selection, save_to_file=save_to_file)

    return conversion.data


def xls_to_json(path, save_to_file):
    """
    Converts Microsoft Excel xls or xlsx files to json

    Parameters
    ----------
     path : str
        path to json file or directory with json files
    save_to_file : bool
        if data is supposed to be saved to file
    Returns
    -------

    """
    from ._converting import _xlsx_to_json
    conversion = _FileConversion(path=path, file_type="xls", function=_xlsx_to_json, save_to_file=save_to_file)

    return conversion.data


xlsx_to_json = xls_to_json


def json_to_csv(path, key_name, order=None, save_to_file=False, if_empty_value=None, key_position=0, **kwargs):
    # ToDo add support for inverse csv writing
    """
    Converts a dictionary or json to csv. The dictionary converts as dict[line_key][header_key]
    Parameters
    ----------
    path : str
        path to json file or directory with json files
    key_name : str
        the name of the json keys
    order : dict {int: [str, int, float]}
        for defining a specific order of the
    save_to_file : bool
        if data is supposed to be saved to file
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
    conversion = _FileConversion(path=path, file_type="json", function=_json_to_csv,
                                 key_name=key_name, dialect="custom" if kwargs else None,
                                 key_position=key_position, if_empty_value=if_empty_value if if_empty_value else "",
                                 order=order, save_to_file=save_to_file)
    return conversion.data


dict_to_csv = json_to_csv


def json_to_xlsx(path, save_to_file):
    """

    Parameters
    ----------
     path : str
        path to json file or directory with json files
    save_to_file : bool
        if data is supposed to be saved to file

    Returns
    -------

    """
    from ._converting import _json_to_xlsx
    conversion = _FileConversion(path=path, file_type="json", function=_json_to_xlsx, save_to_file=save_to_file)

    return conversion.data
