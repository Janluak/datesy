__doc__ = "All actions of inspecting data are to be found here"
__all__ = ["find_header_line", "find_key"]


def find_header_line(data, header_keys):
    """
    Find the header line in row_based data_structure
    NOT IMPLEMENTED YET: Version 0.9 feature

    Parameters
    ----------
    data : list, pandas.DataFrame
    header_keys : str, list, set
        some key(s) to find in a row

    Returns
    -------
    int
        the header_line
    """
    # patterns with regex if not word?
    raise NotImplemented


def find_key(data, key=None, regex_pattern=None):
    # ToDo separate to three functions: one handling key & regex, then separate functions for string or regex
    """
    Find a key in a complex dictionary

    Parameters
    ----------
    data : dict
        the data structure to find the key
    key : str, optional
        a string to be found
    regex_pattern : str, optional
        a regex match to be found

    Returns
    -------
    dict
        all matches and their path in the structure ``{found_key: path_to_key}``
    """
    # return "path in structure", "value"
    raise NotImplemented
