from pandas import read_excel, ExcelFile
from .file_selection import *

__all__ = [
    "load_single_sheet",
    "load_all_sheets",
    "load_these_sheets",
    "load_these",
    "load_all",
    "write_single_sheet_from_DataFrame",
    "write_multi_sheet_from_DataFrame",
    "write_xlsx_single_sheet_from_dict",
    "write_xlsx_multi_sheet_from_dict_of_dicts",
]


def load_single_sheet(file, sheet=None):
    """
    Load a xls(x) file_name to a pandas.DataFrame

    Parameters
    ----------
    file : str
        path to file_name
    sheet : str, optional
        a sheet_name to extract. default is first sheet

    Returns
    -------
    handling : pandas.DataFrame
        pandas.DataFrame representing the xls(x) file_name
    """
    if not os.path.isfile(file):
        raise TypeError("given path doesn't point to a file_name")

    if not sheet:
        data = read_excel(file)
    else:
        data = read_excel(file, sheet_name=sheet)

    return data


def load_all_sheets(file):
    """
    Load from a xls(x) file_name to a pandas.DataFrame all its sheets

    Parameters
    ----------
    file : str
        path to file_name

    Returns
    -------
    handling : dict {sheet_name: pandas.DataFrame}
        dictionary containing the sheet_names as keys and pandas.DataFrame representing the xls(x) sheets
    """

    excel_file = ExcelFile(file)
    return load_these_sheets(file, list(excel_file.sheet_names))


def load_these_sheets(file, sheets):
    """
    Load from a xls(x) file_name to a pandas.DataFrame the specified sheets

    Parameters
    ----------
    file : str
        path to file_name
    sheets : list
        sheet_names to extract

    Returns
    -------
    handling : dict(pandas.DataFrame)
        dictionary containing the sheet_names as keys and pandas.DataFrame representing the xls(x) sheets
    """

    data = dict()
    for sheet in sheets:
        data[sheet] = load_single_sheet(file, sheet)

    return data


def load_these(file_list):
    """
    Load the xls(x) files to a pandas.DataFrame all their sheets

    Parameters
    ----------
    file_list : list
        paths to files

    Returns
    -------
    handling : dict
        {file_name: {sheet_name: pandas.DataFrame}}
    """
    if not isinstance(file_list, list):
        raise TypeError("Expected list, got {}".format(type(file_list)))

    data = dict()
    for file in file_list:
        data[file] = load_all_sheets(file)

    return data


def load_all(directory):
    if not os.path.isdir(directory):
        raise NotADirectoryError

    files = get_file_list_from_directory(directory, pattern="*.xls*")
    data = load_these(files)

    return data


def __write_xlsx(file_name, data):
    """
    Write xlsx sheets from list of tuples (sheet_name, DataFrame)

    Parameters
    ----------
    file_name : str
    data : list
        list of tuples containing the sheet_name (pos.1) and panda.DataFrames (pos.2)

    """
    from pandas import ExcelWriter, DataFrame

    if not isinstance(file_name, str):
        raise TypeError(
            "file_name needs to be a string. {} given".format(type(file_name))
        )
    if not all(isinstance(element[1], DataFrame) for element in data):
        raise TypeError("all handling elements[1] need to be a pandas.DataFrame")

    if "." not in file_name:
        file_name += ".xlsx"

    with ExcelWriter(file_name) as writer:
        logging.info("saving to file_name: {}".format(file_name))
        for element in data:
            if not isinstance(element[1], DataFrame):
                raise ValueError("wrong handling type, expected pandas.DataFrame")
            element[1].to_excel(writer, sheet_name=element[0])
        writer.save()


def write_single_sheet_from_DataFrame(file_name, data_frame, sheet_name=None):
    """
    saves a pandas data_frame to file_name

    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as .xlsx
    data_frame : pandas.DataFrame
        either a data_frame or a dict of data_frames
    sheet_name : str, optional
        a sheet_name for the handling

    """
    if not sheet_name:
        sheet_name = "Sheet1"

    __write_xlsx(file_name, [(sheet_name, data_frame)])


def write_multi_sheet_from_DataFrame(file_name, data_frames, sheet_order=None):
    """
    saves a pandas data_frame to file_name

    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as .xlsx
    data_frames : dict {sheet_name: DataFrame}
        dict of data_frames
    sheet_order : dict {int: str}, optional
        for defining a specific order of the keys

    """
    if sheet_order:
        from .._helper import _create_sorted_list_from_order

        order = _create_sorted_list_from_order(
            sheet_order, all_elements=data_frames.keys()
        )
        __write_xlsx(file_name, [(key, data_frames[key]) for key in order])
    else:
        __write_xlsx(file_name, [(key, data_frames[key]) for key in data_frames])


def write_xlsx_single_sheet_from_dict(
    file_name, data, main_key=None, sheet=None, order=None, inverse=False
):
    """
    Save a pandas data_frame to file_name

    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as .xlsx
    data : dict
        dictionary of handling. `{main_element: {handling}}`
        if more than one main_element is provided the main_element is treated as sheet name
    main_key : str, optional
        if the json or dict does not have the main key as a single `{main_element : dict}` present, it needs to be specified
    sheet : str, optional
        a sheet name for the handling
    order : dict, list, optional
        list with the column names in order or dict with specified key positions
    inverse : bool, optional
        if columns and rows shall be switched

    """
    from ..convert import dict_to_pandas_data_frame

    data_frame = dict_to_pandas_data_frame(data, False, main_key, order, inverse)
    write_single_sheet_from_DataFrame(
        file_name=file_name, data_frame=data_frame, sheet_name=sheet
    )


def write_xlsx_multi_sheet_from_dict_of_dicts(file_name, data, order=None):
    """
    saves a pandas data_frame to file_name

    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as .xlsx
    data : dict
        dictionary of handling. `{sheet: {main_element: {handling}}}`
        if more than one main_element is provided the main_element is treated as sheet name
    order : dict, optional
        dict with sheet_name as key for order

    """

    from ..convert import dict_to_pandas_data_frame

    data_frames = {key: dict_to_pandas_data_frame(data[key], False) for key in data}

    write_multi_sheet_from_DataFrame(file_name, data_frames, order)
