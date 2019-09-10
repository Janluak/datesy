from .file_selection import *

__all__ = ["load", "load_all", "load_single", "load_these"]


def load(path):
    """
    Load a xml file_name to a dictionary

    Parameters
    ----------
    path : str
        path to a file_name or directory

    Returns
    -------
    handling : dict
        if a single file_name provided, the dictionary.
        otherwise a dict of dicts with the loaded dicts

    """
    files = return_file_list_if_path(path, file_ending=".xml", return_always_list=True)
    data = load_these(files)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_single(path):
    """
    Load a single xml file_name

    Parameters
    ----------
    path : str
        path to file_name

    Returns
    -------
    handling : dict
        the loaded json as a dict

    """
    from xmltodict import parse

    with open(path, "r") as f:
        logging.info("loading file_name {}".format(path))
        f = str(f.read())
        return dict(parse(f))


def load_these(file_list):
    if not isinstance(file_list, list):
        raise TypeError("Expected list, got {}".format(type(file_list)))

    data = dict()
    for file in file_list:
        data[file] = load_single(file)

    return data


def load_all(directory):
    if not os.path.isdir(directory):
        raise NotADirectoryError

    files = get_file_list_from_directory(directory, file_ending=".xml")
    data = load_these(files)

    return data
