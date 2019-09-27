from .file_selection import *
from .._helper import _cast_main_key_name
import csv

__doc__ = "The csv_file module takes care of all I/O interactions concerning csv files"


__all__ = [
    "load",
    "load_single",
    "load_these",
    "load_all",
    "write",
    "write_from_rows",
    "write_from_dict",
]


def _register_csv_dialect(**kwargs):
    """
    Register a csv dialect from kwargs with differences to the main unix dialect

    Parameters
    ----------
    kwargs : optional
        all parameters for changing from unix basic dialect

    """
    csv_dialect_options = {i for i in set(dir(csv.Dialect)) if "__" not in i}
    if not all(key in csv_dialect_options for key in kwargs.keys()):
        raise KeyError(
            f"only these keys for csv dialect are allowed: {csv_dialect_options}\nGiven keys: {kwargs.keys()}"
        )
    csv.register_dialect("custom", **kwargs)


def load(path, **kwargs):
    """
    Load(s) csv file(s) and returns the rows
    Specifying a file_name: one file will be loaded.
    Specifying a directory: all `*.csv` files will be loaded.

    Parameters
    ----------
    path : str
        path to a file_name or directory
    kwargs : optional
        csv dialect options

    Returns
    -------
    list, dict
        list of lists if a single file_name was provided: ``[[row1.1, row1.2]]``
        dict of list of lists if multiple files provided: ``{file_name : [[row1.1, row1.2]]}``

    """
    files = return_file_list_if_path(path, file_ending=".csv", return_always_list=True)
    data = load_these(files, **kwargs)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_single(file_name, **kwargs):
    """
    Load a csv file and return the rows

    Parameters
    ----------
    file_name : str
       file_name to load from
    kwargs : optional
        csv dialect options

    Returns
    -------
    list
        list of lists representing the csv data
        ``[[row1.1, row1.2]]``
    """
    if kwargs and "dialect" in kwargs:
        dialect = kwargs["dialect"]
    elif kwargs:
        _register_csv_dialect(**kwargs)
        dialect = "custom"
    else:
        dialect = "unix"

    with open(file_name, "r") as f:
        data = list()
        rows = csv.reader(f, dialect=dialect)
        for row in rows:
            data.append(row)

    return data


def load_these(file_name_list, **kwargs):
    """
    Load specified csv files and return the rows in a dictionary with file_name as key

    Parameters
    ----------
    file_name_list : list
        list of file_names to load from
    kwargs : optional
        csv dialect options

    Returns
    -------
    dict(list)
        the rows from the files as values of file_name as key
        ``{file_name : [[row1.1, row1.2]]}``

    """
    if kwargs and "dialect" not in kwargs:
        _register_csv_dialect(**kwargs)

    if not isinstance(file_name_list, list):
        raise TypeError("Expected list, got {}".format(type(file_name_list)))

    data = dict()
    for file in file_name_list:
        data[file] = load_single(file, **kwargs)

    return data


def load_all(directory, **kwargs):
    """
    Load all csv files in the directory and return the rows in a dictionary with file_name as key

    Parameters
    ----------
    directory : str
        the directory containing the csv files
    kwargs : optional
     csv dialect options

    Returns
    -------
    dict(list)
        the rows from the files as values of file_name as key
        ``{file_name : [[row1.1, row1.2]]}``
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError

    files = get_file_list_from_directory(directory, file_ending=".csv")
    data = load_these(files, **kwargs)

    return data


def write_from_rows(file_name, rows, **kwargs):
    """
    Save row based document from rows to file

    Parameters
    ----------
    file_name : str
        the file_name to save the data under. if no ending is provided, saved as `file_name.csv`
    rows : list
        list of lists to write to file_name
    kwargs : optional
        csv dialect options

    """
    if "." not in file_name:
        file_name += ".csv"

    logging.info(f"saving to file_name: {file_name}")

    if kwargs and "dialect" in kwargs:
        dialect = kwargs["dialect"]
    elif kwargs:
        _register_csv_dialect(**kwargs)
        dialect = "custom"
    else:
        dialect = "unix"

    if not check_file_name_ending(file_name, ["csv", "tsv"]):
        logging.warning(
            "file_name ending {} different to standard ({})".format(
                file_name.split(".")[-1], ["csv", "tsv"]
            )
        )

    with open(file_name, "w") as fw:
        w = csv.writer(fw, dialect=dialect)
        for row in rows:
            w.writerow(row)


def write_from_dict(
    file_name,
    data,
    main_key_name=None,
    main_key_position=0,
    order=None,
    if_empty_value=None,
    **kwargs,
):
    """
    Save a row based document from dict to file

    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as `file_name.csv`
    data : dict
        the dictionary to be saved as csv
    main_key_name : str, optional
        if the json or dict does not have the main key as a single key present (``{main_element_name: dict}``), it needs to be specified
    order : dict {int: str}, list, optional
        for defining a specific order of the keys
        either a dictionary with the specified positions in a dictionary with positions as keys (integers) or in a list
    if_empty_value : any, optional
        the value to set when no handling is available
        default is "delete" leading to be an empty value
    main_key_position : int, optional
        the position in csv of the dictionary main key
    kwargs : optional
        csv dialect options

    """
    if not main_key_name:
        data, main_key_name = _cast_main_key_name(data)

    from ..convert import dict_to_rows

    rows = dict_to_rows(
        data=data,
        main_key_name=main_key_name,
        main_key_position=main_key_position,
        if_empty_value=if_empty_value,
        order=order,
    )
    write_from_rows(file_name, rows, **kwargs)


def write(
    file_name,
    data,
    main_key_name=None,
    main_key_position=0,
    order=None,
    if_empty_value=None,
    **kwargs,
):
    """
    Save a row based document from dict or list to file
    If presented a dictionary, converting to rows is done by the `dict_to_rows <https://datesy.readthedocs.io/en/latest/datesy.html#datesy.convert.rows_to_dict>`_ method of this package.

    Parameters
    ----------
    file_name : str
        the file_name to save under. if no ending is provided, saved as `file_name.csv`
    data : dict
        the dictionary to be saved as csv
    main_key_name : str, optional
        if the json or dict does not have the main key as a single key present (``{main_element_name: dict}``), it needs to be specified
    main_key_position : int, optional
        the position in csv of the dictionary main key
    order : dict {int: str}, list, optional
        for defining a specific order of the keys
        either a dictionary with the specified positions in a dictionary with positions as keys (integers) or in a list
    if_empty_value : any, optional
        the value to set when no handling is available
        default is "delete" leading to be an empty value
    kwargs : optional
        csv dialect options
    """
    if isinstance(data, list):
        if main_key_name or order or if_empty_value or main_key_position:
            raise ValueError(
                "if row of rows used, main_key_name, order, "
                "if_empty_value and main_key_position must not be set"
            )
        write_from_rows(file_name, data, **kwargs)
    elif isinstance(data, dict):
        write_from_dict(
            file_name,
            data,
            main_key_name,
            order,
            if_empty_value,
            main_key_position,
            **kwargs,
        )
    else:
        raise TypeError(
            "wrong type for `handling`. only list or dict are allowed, {} given".format(
                type(data)
            )
        )
