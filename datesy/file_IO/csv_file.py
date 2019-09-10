from .file_selection import *
from .._helper import _cast_main_key_name
import csv


__all__ = [
    "load",
    "load_all",
    "load_single",
    "load_these",
    "write_from_rows",
    "write_from_dict",
]


def _register_csv_dialect(**kwargs):
    """
    Register a csv dialect from kwargs with differences to main unix dialect

    Parameters
    ----------
    kwargs
        all parameters for changing from unix basic dialect

    """
    csv_dialect_options = {i for i in set(dir(csv.Dialect)) if "__" not in i}
    if not all(key in csv_dialect_options for key in kwargs.keys()):
        raise KeyError(
            "only these keys for csv dialect are allowed: {}\nGiven keys: {}".format(
                csv_dialect_options, kwargs.keys()
            )
        )
    csv.register_dialect("custom", **kwargs)


def load(path, **kwargs):
    """
    Load a csv file_name and returns the rows

    Parameters
    ----------
    path : str
        path to a file_name or directory
    kwargs
        csv dialect options

    Returns
    -------
    handling : list, dict
        if a single file_name was provided, the list of lists
        if multiple files provided, a dict of list of lists

    """
    files = return_file_list_if_path(path, file_ending=".csv", return_always_list=True)
    data = load_these(files, **kwargs)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_single(path, **kwargs):
    """
    Load a csv file_name and return the rows

    Parameters
    ----------
    path : str
       path to file_name
    kwargs
        csv dialect options
    """
    if kwargs and "dialect" in kwargs:
        dialect = kwargs["dialect"]
    elif kwargs:
        _register_csv_dialect(**kwargs)
        dialect = "custom"
    else:
        dialect = "unix"

    with open(path, "r") as f:
        data = list()
        rows = csv.reader(f, dialect=dialect)
        for row in rows:
            data.append(row)

    return data


def load_these(file_list, **kwargs):
    if kwargs and "dialect" not in kwargs:
        _register_csv_dialect(**kwargs)

    if not isinstance(file_list, list):
        raise TypeError("Expected list, got {}".format(type(file_list)))

    data = dict()
    for file in file_list:
        data[file] = load_single(file, **kwargs)

    return data


def load_all(directory, **kwargs):
    if not os.path.isdir(directory):
        raise NotADirectoryError

    files = get_file_list_from_directory(directory, file_ending=".csv")
    data = load_these(files, **kwargs)

    return data


def write_from_rows(file, rows, **kwargs):
    """
    Save a row based document from rows to file_name

    Parameters
    ----------
    file : str
        the file_name to save under. if no ending is provided, saved as .csv
    rows : list
        list of lists to write to file_name
    kwargs : optional
        csv dialect options

    """
    if "." not in file:
        file += ".csv"

    logging.info("saving to file_name: {}".format(file))

    if kwargs and "dialect" in kwargs:
        dialect = kwargs["dialect"]
    elif kwargs:
        _register_csv_dialect(**kwargs)
        dialect = "custom"
    else:
        dialect = "unix"

    if not check_file_name_ending(file, ["csv", "tsv"]):
        logging.warning(
            "file_name ending {} different to standard ({})".format(
                file.split(".")[-1], ["csv", "tsv"]
            )
        )

    with open(file, "w") as fw:
        w = csv.writer(fw, dialect=dialect)
        for row in rows:
            w.writerow(row)


def write_from_dict(
    file,
    data,
    main_key=None,
    order=None,
    if_empty_value=None,
    main_key_position=0,
    **kwargs
):
    """
    Save a row based document from dict to file_name

    Parameters
    ----------
    file : str
        the file_name to save under. if no ending is provided, saved as .csv
    data : dict
        the dictionary to be saved as json
    main_key : str
        if the json or dict does not have the main key as a single {main_element : dict} present, it needs to be specified
    order : dict {int: str}
        for defining a specific order of the keys
    if_empty_value
        the value to set when no handling is available
    main_key_position : int
        the position in csv of the json key
    kwargs
        csv dialect options

    """
    if not main_key:
        data, main_key = _cast_main_key_name(data)

    from ..convert import dict_to_rows

    rows = dict_to_rows(
        data=data,
        main_key=main_key,
        main_key_position=main_key_position,
        if_empty_value=if_empty_value,
        order=order,
    )
    write_from_rows(file, rows, **kwargs)


def write(
    file,
    data,
    main_key=None,
    order=None,
    if_empty_value=None,
    main_key_position=0,
    **kwargs
):
    if isinstance(data, list):
        if main_key or order or if_empty_value or main_key_position:
            raise ValueError(
                "if row of rows used, main_key, order, "
                "if_empty_value and main_key_position must not be set"
            )
        write_from_rows(file, data, **kwargs)
    elif isinstance(data, dict):
        write_from_dict(
            file, data, main_key, order, if_empty_value, main_key_position, **kwargs
        )
    else:
        raise TypeError(
            "wrong type for `handling`. only list or dict are allowed, {} given".format(
                type(data)
            )
        )
