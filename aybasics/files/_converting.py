from aybasics.logger import logger


def _dictionize(sub_dict):
    """
    creates normal dictionaries from a sub_dictionary containing orderedDicts

    Parameters
    ----------
    sub_dict : dict
        a dictionary with unlimited data structure depth and types

    Returns
    -------
    normalized_dict : dict
        the same data structure as `sub_dict` just without orderedDicts


    """
    from collections import OrderedDict
    normalized_dict = dict()
    for key in sub_dict:
        if isinstance(sub_dict[key], OrderedDict):
            normalized_dict[key] = _dictionize(sub_dict[key])
        elif isinstance(sub_dict[key], list):
            normalized_dict[key] = list()
            for element in sub_dict[key]:
                if isinstance(element, (list, dict, set)):
                    normalized_dict[key].append(_dictionize(element))
                else:
                    normalized_dict[key] = sub_dict[key]

        else:
            normalized_dict[key] = sub_dict[key]

    return normalized_dict


def _reduce_lists(sub_dict, list_for_reduction, manual_selection, depth_in_list=0):
    raise NotImplemented


def _cast_main_key_name(data):
    """
    casts the main_key_name in a dictionary `{main_key_name: {main_key_1 : {…}, maine_key_2 : {…}}}`

    a main_key_name is the name for all the main_keys

    Parameters
    ----------
    data : dict
        the dictionary to cast the main_key_name from

    Returns
    -------
    data : dict
        the input data with the main_keys as new top_level keys of dict `{main_key_1 : {…}, maine_key_2 : {…}}`
    main_key_name : str
        the name of the main_keys
    """
    if isinstance(data, dict):
        if len(data.keys()) == 1:
            [main_key_name] = data.keys()
            [data] = data.values()
            return data, main_key_name
        raise ValueError("Dict has more than one key. "
                         "Please provide either the main_key for dicts with more than one entry or "
                         "provide dict with only one key")
    raise TypeError("Expected type dict, got {}".format(type(data)))


def _csv_to_json(file, memory, save_to_file, main_key_position, null_value, dialect, header_line):
    """
    Converts a single file from csv to json

    Parameters
    ----------
    file : str
    memory : dict
    main_key_position : int
    dialect : str, None
    null_value
    header_line : int

    Returns
    -------
    data : dict
        dictionary containing the information from csv

    """
    rows_no = 0
    data = dict()
    from .load import load_csv
    rows = load_csv(file, dialect=dialect if dialect else "unix")
    header = rows[header_line]
    for row in rows[header_line + 1:]:
        if null_value == "delete":
            data[row[main_key_position]] = {header[i]: row[i] for i in range(len(header)) if
                                            row[i] and i != main_key_position}
        else:
            data[row[main_key_position]] = {header[i]: row[i] if row[i] else null_value for i in range(len(header))
                                            if i != main_key_position}
        rows_no += 1
    data = {header[main_key_position]: data}
    if memory:
        memory[file] = data
    if save_to_file:
        from .write import write_json
        write_json(file.split(".")[0] + ".json", data)
    logger.info("{} rows: {}".format(file.split("/")[-1], rows_no))
    return data


def _json_to_csv(file, memory, save_to_file, dialect, main_key_position, if_empty_value, order, main_key=None,
                 data=False):
    """
    Converts a single file from json to csv

    Parameters
    ----------
    file : str
    memory : dict
    main_key : str
    dialect : str, None
    main_key_position : int
    if_empty_value
    order : dict, None
    data : object

    Returns
    -------
    rows : list(lists)
        list of rows representing the csv based on the `main_key_position`

    """
    if not data:
        from .load import load_json
        data = load_json(file)
        logger.info("current file: {}".format(file.split("/")[-1]))
    if not main_key:
        data, main_key = _cast_main_key_name(data)

    header_keys = set()
    try:
        for element in data:
            for key in data[element].keys():
                header_keys.add(key)
    except AttributeError:
        raise ValueError("JSON/dictionary is not formatted suitable for neat csv conversion. "
                         "{main_key: {key: {value_key: value}}} expected")

    if not order:
        header = list(header_keys)
        header.insert(main_key_position, main_key)  # put the json_key to position in csv
    else:
        # order keys need to be int
        if not all(isinstance(order_no, int) for order_no in order.keys()):
            raise ValueError("all keys of order dictionary need to be of type int")

        #
        if main_key_position in order.keys() and main_key != order[main_key_position]:
            raise KeyError(
                "The main_key_position '{}' is used by another key ('{}') "
                "in the order dict!".format(main_key_position, order[main_key_position]))
        if main_key not in order.values():
            order[main_key_position] = main_key
        placed_keys = set(order.values())
        placed_keys.add(main_key)
        order[main_key_position] = main_key
        header = list(header_keys - placed_keys)
        for order_no in sorted(list(order.keys())):
            header.insert(order_no, order[order_no])

    header_without_ordered_keys = header.copy()
    header_without_ordered_keys.remove(main_key)
    rows = [header]

    for element in data:
        row = [data[element][key] if key in data[element] else if_empty_value for key in header_without_ordered_keys]
        row.insert(main_key_position, element)
        rows.append(row)
    if memory:
        memory[file] = rows
    if save_to_file:
        from .write import write_csv_from_rows
        write_csv_from_rows(file.split(".")[0] + ".csv", rows, dialect=dialect)
    return rows


def _xml_to_json(file, memory, save_to_file, list_reduction, manual_selection):
    """
    Converts a single file from xml to json

    Parameters
    ----------
    file : str
    memory : dict
    save_to_file : bool
    list_reduction : bool
    manual_selection : bool

    Returns
    -------


    """

    from collections import OrderedDict

    from xmltodict import parse
    with open(file, "r") as f:
        f = str(f.read())
        basic_dict = dict(parse(f))
    data = dict()
    for key in basic_dict:
        if isinstance(basic_dict[key], OrderedDict):
            data[key] = _dictionize(basic_dict[key])
        else:
            data[key] = basic_dict[key]

    if list_reduction:
        data = _reduce_lists(data, list_reduction, manual_selection)

    if memory:
        memory[file] = data

    if save_to_file:
        from .write import write_json
        write_json(file.split(".")[0] + ".json", data)


def _json_to_xlsx(file, memory, save_to_file, main_key, sheets, order=None, data=False):
    """
    Converts a single file from json to xlsx
    
    Parameters
    ----------
    file : str
    memory : dict
    save_to_file : bool
    main_key : str
    sheets : 
    order
    data

    Returns
    -------

    """
    raise DeprecationWarning("Function not working: see issue #21")
    if not data:
        from .load import load_json
        data = load_json(file)
        logger.info("current file: {}".format(file.split("/")[-1]))

    data_frame = _json_to_pandas_data_frame(data, main_key, order)

    if memory:
        memory[file] = data_frame

    if save_to_file:
        from aybasics import write_xlsx
        write_xlsx(file.split(".")[0] + ".xlsx", data_frame, sheets)


def _json_to_pandas_data_frame(data, main_key=None, order=None, inverse=False):
    """
    Converts a single file from dict to pandas.DataFrame

    Parameters
    ----------
    data : dict
    main_key : str
    order : list
    inverse : bool

    Returns
    -------
    data_frame : pandas.DataFrame

    """
    from pandas import DataFrame
    if not main_key:
        data, main_key = _cast_main_key_name(data)

    if not order:
        if not inverse:
            data_frame = DataFrame.from_dict(data, orient="index")
        else:
            data_frame = DataFrame.from_dict(data)
    else:
        if not inverse:
            data_frame = DataFrame.from_dict(data, orient="index", columns=order)
        else:
            data_frame = DataFrame.from_dict(data, columns=order)

        if not isinstance(order, list):
            raise TypeError("expected list type for order, received type {}. received order: {}".
                            format(type(order), order))
        data_frame[main_key] = data_frame.index
        data_frame.set_index(order[0], inplace=True)

    data_frame.index.name = main_key

    return data_frame


def _xlsx_to_csv(file, memory, save_to_file, main_key_position, null_value, header_line, sheets):
    raise NotImplemented


def _xlsx_to_json(file, memory, save_to_file, main_key_position, null_value, header_line, sheets):
    """
    Converts a single file from xlsx to json

    Parameters
    ----------
    file : str
    memory : dict
    save_to_file : bool
    main_key_position : int
    null_value
    header_line : int
    sheets : list

    Returns
    -------
    data : dict
        the dictionary representing the xlsx based on `main_key_position`
    """
    from .load import load_xls
    from pandas import notnull
    data_frame = load_xls(file, sheets, ret_single=True)
    if header_line == 0:
        header = list(data_frame.keys())
    else:
        raise NotImplemented

    # set null_values
    if null_value == "delete":
        exchange_key = None
    else:
        exchange_key = null_value
    data_frame = data_frame.where((notnull(data_frame)), exchange_key)

    # delete null_values if null_value == "delete"
    data = data_frame.set_index(header[main_key_position]).T.to_dict()
    for key in data.copy():
        for key2 in data[key].copy():
            if not data[key][key2] and null_value == "delete":
                del data[key][key2]
    data = {header[0]: data}

    if memory:
        memory[file] = data

    if save_to_file:
        from .write import write_json
        write_json(file.split(".")[0] + ".json", data)
    logger.info("{} rows: {}".format(file.split("/")[-1], data_frame[header[0]].count() + 1))
    return data
