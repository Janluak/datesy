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


def cast_main_key(data):
    """
    Cast the main_key_name in a dictionary ``{main_key_name: {main_key_1 : {…}, maine_key_2 : {…}}}``

    a main_key_name is the name for all the main_keys

    Parameters
    ----------
    data : dict
        the dictionary to cast the main_key_name from

    Returns
    -------
    data : dict
        the input data with the main_keys as new top_level keys of dictionary `{main_key_1 : {…}, maine_key_2 : {…}}`
    main_key_name : str
        the name of the main_keys that got casted
    """
    if not isinstance(data, dict):
        raise TypeError("Expected type dict, got {}".format(type(data)))
    if len(data.keys()) != 1:
        received_top_level_keys = set()
        i = 0
        for key in data:
            received_top_level_keys.add(key)
            i += 1
            if i == 3:
                break
        raise ValueError(
            f"Dict has more than one key, received e.g. '{received_top_level_keys}'. "
            "Please provide either the main_element for dicts with more than one entry or "
            "provide dict with only one key"
        )

    [main_key_name] = data.keys()
    [data] = data.values()
    return data, main_key_name
