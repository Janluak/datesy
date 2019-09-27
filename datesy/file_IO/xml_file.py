from .file_selection import *

__doc__ = "The xml_file module takes care of all I/O interactions concerning xml files"

__all__ = ["load", "load_single", "load_these", "load_all"]


def load(path):
    """
    Load(s) json file(s) and returns the dictionary/-ies
    Specifying a file_name: one file will be loaded.
    Specifying a directory: all `*.json` files will be loaded.

    Parameters
    ----------
    path : str
        path to a file_name or directory

    Returns
    -------
    dict
        dictionary representing the json ``{file_name: {data}}``

    """
    files = return_file_list_if_path(path, file_ending=".xml", return_always_list=True)
    data = load_these(files)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_single(file_name):
    """
    Load a single xml file

    Parameters
    ----------
    file_name : str
        file_name to load from

    Returns
    -------
    dict
        the xml as ordered dict ``{collections.OrderedDict}``

    """
    from xmltodict import parse

    with open(file_name, "r") as f:
        logging.info("loading file_name {}".format(file_name))
        f = str(f.read())
        return dict(parse(f))


def load_these(file_name_list):
    """
    Load specified xml files and return the data in a dictionary with file_name as key

    Parameters
    ----------
    file_name_list : list
        list of file_names to load from

    Returns
    -------
    dict(collections.OrderedDict)
        the dictionaries from the files as values of file_name as key
        ``{file_name: {collections.OrderedDict}``

    """
    if not isinstance(file_name_list, list):
        raise TypeError("Expected list, got {}".format(type(file_name_list)))

    data = dict()
    for file in file_name_list:
        data[file] = load_single(file)

    return data


def load_all(directory):
    """
    Load all xml files in the directory and return the data in a dictionary with file_name as key

    Parameters
    ----------
    directory : str
        the directory containing the xml files

    Returns
    -------
    dict(collections.OrderedDict)
        the dictionaries from the files as values of file_name as key
        ``{file_name: {collections.OrderedDict}}``
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError

    files = get_file_list_from_directory(directory, file_ending=".xml")
    data = load_these(files)

    return data
