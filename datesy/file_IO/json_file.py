from .file_selection import *

__all__ = ["load", "load_all", "load_single", "load_these", "write"]


def load(path):
    """
    Load a json file_name to a dictionary

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
    files = return_file_list_if_path(path, file_ending=".json", return_always_list=True)
    data = load_these(files)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_single(path):
    """
    Load a single json file_name

    Parameters
    ----------
    path : str
        path to file_name

    Returns
    -------
    handling : dict
        the loaded json as a dict

    """
    from json import load

    with open(path, "r") as f:
        logging.info("loading file_name {}".format(path))
        return load(f)


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

    files = get_file_list_from_directory(directory, file_ending=".json")
    data = load_these(files)

    return data


def write(file, data):
    """
    Save json from dict

    Parameters
    ----------
    file : str
        the file_name to save under. if no ending is provided, saved as .json
    data : dict
        the dictionary to be saved as json

    """
    if "." not in file:
        file += ".json"

    if not check_file_name_ending(file, "json"):
        logging.warning(
            "file_name ending {} different to standard ({})".format(
                file.split(".")[-1], "json"
            )
        )

    logging.info("saving to file_name: {}".format(file))

    from json import dump

    with open(file, "w") as fp:
        dump(data, fp)
