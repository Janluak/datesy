from pandas import read_excel, ExcelFile
from .file_selection import *

__doc__ = (
    "The xls_file module takes care of all I/O interactions concerning xls(x) files"
)

__all__ = [
    "load_single_sheet",
    "load_these_sheets",
    "load_all_sheets",
    "load_these_files",
    "load_all_files",
    "write_single_sheet_from_DataFrame",
    "write_multi_sheet_from_DataFrames",
    "write_single_sheet_from_dict",
    "write_multi_sheet_from_dict_of_dicts",
]


def load(path):
    """
    Load all xls(x) files in the directory with all their sheets to a pandas.DataFrame as values to sheet_names as keys in a dictionary
    Specifying a file_name: one file will be loaded.
    Specifying a directory: all `*.xls(x)` files will be loaded.

    Parameters
    ----------
    path : str
        path to a file_name or directory

    Returns
    -------
    dict
        dictionary containing the sheets as `panda.DataFrames`: ``{file_name: {sheet_name: pandas.DataFrame}}``

    """
    files = return_file_list_if_path(path, pattern="*.xls*", return_always_list=True)
    data = load_these_files(files)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_single_sheet(file_name, sheet=None):
    """
    Load a xls(x) file's (first) sheet to a pandas.DataFrame

    Parameters
    ----------
    file_name : str
       file_name to load from
    sheet : str, optional
        a specified sheet_name to extract. default is first sheet

    Returns
    -------
    pandas.DataFrame
        pandas.DataFrame representing the xls(x) file
    """
    if not os.path.isfile(file_name):
        raise TypeError("given path doesn't point to a file_name")

    if not sheet:
        data = read_excel(file_name)
    else:
        data = read_excel(file_name, sheet_name=sheet)

    return data


def load_all_sheets(file_name):
    """
    Load from a xls(x) file all its sheets to a pandas.DataFrame as values to sheet_names as keys in a dictionary

    Parameters
    ----------
    file_name : str
       file_name to load from

    Returns
    -------
    dict
        dictionary containing the sheet_names as keys and pandas.DataFrame representing the xls(x) sheets
        ``{sheet_name: pandas.DataFrame}``
    """

    excel_file = ExcelFile(file_name)
    return load_these_sheets(file_name, list(excel_file.sheet_names))


def load_these_sheets(file_name, sheets):
    """
    Load from a xls(x) file_name the specified sheets to a pandas.DataFrame as values to sheet_names as keys in a dictionary

    Parameters
    ----------
    file_name : str
       file_name to load from
    sheets : list
        sheet_names to load

    Returns
    -------
    dict(pandas.DataFrame)
        dictionary containing the sheet_names as keys and pandas.DataFrame representing the xls(x) sheets
        ``{sheet_name: pandas.DataFrame}``
    """

    data = dict()
    for sheet in sheets:
        data[sheet] = load_single_sheet(file_name, sheet)

    return data


def load_these_files(file_name_list):
    """
    Load the specified xls(x) files with all their sheets to a pandas.DataFrame as values to sheet_names as keys in a dictionary

    Parameters
    ----------
    file_name_list : list
        list of file_names to load from

    Returns
    -------
    dict
        the data from the sheets in a dictionary with sheet_name as key within again a dictionary with file_name as key
        ``{file_name: {sheet_name: pandas.DataFrame}}``
    """
    if not isinstance(file_name_list, list):
        raise TypeError(f"Expected list, got {type(file_name_list)}")

    data = dict()
    for file in file_name_list:
        data[file] = load_all_sheets(file)

    return data


def load_all_files(directory):
    """
    Load all xls(x) files in the directory with all their sheets to a pandas.DataFrame as values to sheet_names as keys in a dictionary

    Parameters
    ----------
    directory : str
        the directory containing the xlsx files

    Returns
    -------
    dict
        the data from the sheets in a dictionary with sheet_name as key within again a dictionary with file_name as key
        ``{file_name: {sheet_name: pandas.DataFrame}}``

    """
    if not os.path.isdir(directory):
        raise NotADirectoryError

    files = get_file_list_from_directory(directory, pattern="*.xls*")
    data = load_these_files(files)

    return data


def __write_xlsx(file_name, data):
    """
    Write xlsx sheets from list of tuples ``[(sheet_name, DataFrame)]``

    Parameters
    ----------
    file_name : str
        the file_name to save the data under. if no ending is provided, saved as `file_name.xlsx`
    data : list
        list of tuples containing the sheet_name (pos.1) and panda.DataFrames (pos.2)
        ``[(sheet_name1, pandas.DataFrame1), sheet_name2, pandas.DataFrame2]``

    """
    from pandas import ExcelWriter, DataFrame

    if not isinstance(file_name, str):
        raise TypeError(f"file_name needs to be a string. {type(file_name)} given")
    if not all(isinstance(element[1], DataFrame) for element in data):
        raise TypeError("all handling elements[1] need to be a pandas.DataFrame")

    if "." not in file_name:
        file_name += ".xlsx"

    with ExcelWriter(file_name) as writer:
        logging.info(f"saving to file_name: {file_name}")
        for element in data:
            element[1].to_excel(writer, sheet_name=element[0])
        writer.save()


def write_single_sheet_from_DataFrame(file_name, data_frame, sheet_name=None):
    """
    Save a pandas.DataFrame to file

    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as .xlsx
    data_frame : pandas.DataFrame
        pandas.DataFrame to write to file_name
    sheet_name : str, optional
        a sheet_name containing the data

    """
    if not sheet_name:
        sheet_name = "Sheet1"

    __write_xlsx(file_name, [(sheet_name, data_frame)])


def write_multi_sheet_from_DataFrames(file_name, data_frames, sheet_order=None):
    """
    Save multiple pandas.DataFrames to one file

    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as .xlsx
    data_frames : dict {sheet_name: DataFrame}
        dict of data_frames
    sheet_order : dict {int: str}, list, optional
        either a dictionary with the specified positions in a dictionary with positions as keys (integers) or in a list

    """
    if sheet_order:
        from .._helper import _create_sorted_list_from_order

        order = _create_sorted_list_from_order(
            sheet_order, all_elements=data_frames.keys()
        )
        __write_xlsx(file_name, [(key, data_frames[key]) for key in order])
    else:
        __write_xlsx(file_name, [(key, data_frames[key]) for key in data_frames])


def write_single_sheet_from_dict(
    file_name, data, main_key_name=None, sheet=None, order=None, inverse=False
):
    """
    Save a dictionary (``{main_key_name: {data}}``) as xlsx document to file
    Uses the `dict_to_pandas_data_frame <https://datesy.readthedocs.io/en/latest/datesy.html#datesy.convert.dict_to_pandas_data_frame>`_ method of this package for converting the dictionary to pandas.DataFrame.

    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as .xlsx
    data : dict
        the dictionary to be saved as xlsx ``{main_key_name: {data}}``
    main_key_name : str, optional
        if the json or dict does not have the main key as a single `{main_element : dict}` present, it needs to be specified
    sheet : str, optional
        a sheet name for the handling
    order : dict, list, optional
        either a dictionary with the specified positions in a dictionary with positions as keys (integers) or in a list
    inverse : bool, optional
        if columns and rows shall be switched

    """
    from ..convert import dict_to_pandas_data_frame

    data_frame = dict_to_pandas_data_frame(data, False, main_key_name, order, inverse)
    write_single_sheet_from_DataFrame(
        file_name=file_name, data_frame=data_frame, sheet_name=sheet
    )


def write_multi_sheet_from_dict_of_dicts(file_name, data, order=None):
    """
    Save dictionaries (``{sheet_name: {main_key_name: {data}}}``) as xlsx document to file
    Uses the `dict_to_pandas_data_frame <https://datesy.readthedocs.io/en/latest/datesy.html#datesy.convert.dict_to_pandas_data_frame>`_ method of this package for converting the dictionary to pandas.DataFrame.


    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as .xlsx
    data : dict
        the dictionary to be saved as xlsx ``{sheet_name: {main_key_name: {data}}}``
    order : dict, list, optional
        either a dictionary with the specified positions in a dictionary with positions as keys (integers) or in a list

    """

    from ..convert import dict_to_pandas_data_frame

    data_frames = {key: dict_to_pandas_data_frame(data[key], False) for key in data}

    write_multi_sheet_from_DataFrames(file_name, data_frames, order)
