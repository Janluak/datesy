from aybasics.logger import logger


def load_json(files):
    """
    loads a json file to a dictionary
    Parameters
    ----------
    files : [str, list]
        either a list of file names or a file_name

    Returns
    -------
    data : dict
        if a single file provided, the dictionary.
        otherwise a dict of dicts with the loaded dicts

    """
    from json import load
    data = dict()
    if not isinstance(files, list):
        files = [files]
    for file in files:
        with open(file, "r") as f:
            data[file] = load(f)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_csv(files, **kwargs):
    """
    loads a csv file and returns the rows
    Parameters
    ----------
    files : [str, list]
        either a list of file names or a file_name
    kwargs
        csv dialect options

    Returns
    -------
    data : [list, dict]
        if a single file was provided, the list of lists
        if multiple files provided, a dict of list of lists

    """
    from csv import reader
    data = dict()
    if kwargs and "dialect" not in kwargs:
        from .converting import _register_csv_dialect
        _register_csv_dialect(**kwargs)
    if not isinstance(files, list):
        files = [files]
    for file in files:
        with open(file, "r") as f:
            data[file] = list()
            rows = reader(f, dialect="custom" if kwargs and "dialect" not in kwargs else "unix")
            for row in rows:
                data[file].append(row)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_xls(files, sheets=None, ret_single=False):
    """
    loading a xls or xlsx file to a pandas.DataFrame
    Parameters
    ----------
    files : [str, list]
        either a list of file names or a file_name
    sheets : [str, list]
        either a sheet_name or list of sheet_names to extract
    ret_single : bool
        if only single data_frame shall be returned. Only due to bug implemented! To be removed!

    Returns
    -------
    data : [list, dict]
            if a single file was provided, the pandas.DataFrame
            if multiple files provided, a dict of pandas.DataFrame
    """
    from pandas import read_excel, ExcelFile
    data = dict()
    if not isinstance(files, list):
        files = [files]
    for file in files:
        data[file] = dict()
        excel_file = ExcelFile(file)
        if not sheets:
            for sheet in excel_file.sheet_names:
                data[file][sheet] = read_excel(file, sheet_name=sheet)
        else:
            if not isinstance(sheets, list):
                sheets = [sheets]
            for sheet in sheets:
                data[file][sheet] = read_excel(file, sheet_name=sheet)
        if ret_single:  # ToDo get rid after supporting multiple sheets in _converting.py
            data[file] = read_excel(file)

    try:
        [value] = data.values()
        return value
    except ValueError:
        return data
