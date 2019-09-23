def rows_to_dict(rows, main_key_position=0, null_value="delete", header_line=0):
    """
    Convert a row of rows (e.g. csv) to dictionary

    Parameters
    ----------
    rows : list(lists)
    main_key_position : int, optional
    null_value : any, optional
    header_line : int, optional

    Returns
    -------
    handling : dict
        dictionary containing the information from csv

    """
    rows_no = 0
    data = dict()
    header = rows[header_line]

    for row in rows[header_line + 1:]:

        if null_value == "delete":
            try:
                data[row[main_key_position]] = {
                    header[i]: row[i]
                    for i in range(len(header))
                    if row[i] and i != main_key_position
                }
            except IndexError:
                raise IndexError("not all elements are the same length")

        else:
            data[row[main_key_position]] = {
                header[i]: row[i] if row[i] else null_value
                for i in range(len(header))
                if i != main_key_position
            }
        rows_no += 1

    data = {header[main_key_position]: data}

    return data


def dict_to_rows(
    data, main_key=None, main_key_position=0, if_empty_value=None, order=None
):
    """
    Convert a dictionary to rows

    Parameters
    ----------
    data : dict
    main_key : str, optional
    main_key_position : int, optional
    if_empty_value : any, optional
    order : dict, None, optional

    Returns
    -------
    list(lists)
        list of rows representing the csv based on the `main_element_position`

    """
    if not main_key:
        from ._helper import _cast_main_key_name

        data, main_key = _cast_main_key_name(data)

    header_keys = set()
    try:
        for main_key in data:
            for key in data[main_key].keys():
                header_keys.add(key)
    except AttributeError:
        raise ValueError(
            "JSON/dictionary is not formatted suitable for neat csv conversion. "
            "{main_element: {key: {value_key: value}}} expected"
        )

    if not order:
        header = list(header_keys)
        header.insert(
            main_key_position, main_key
        )  # put the json_key to position in csv
    else:
        from ._helper import _create_sorted_list_from_order

        header = _create_sorted_list_from_order(
            all_elements=header_keys,
            order=order,
            main_element=main_key,
            main_element_position=main_key_position,
        )

    header_without_ordered_keys = header.copy()
    header_without_ordered_keys.remove(main_key)
    rows = [header]

    for element in data:
        row = [
            data[element][key] if key in data[element] else if_empty_value
            for key in header_without_ordered_keys
        ]
        row.insert(main_key_position, element)
        rows.append(row)

    return rows


def dict_to_pandas_data_frame(
    data, data_as_index=False, main_key=None, order=None, inverse=False
):
    """
    Convert a dictionary to pandas.DataFrame

    Parameters
    ----------
    data : dict
        dictionary of handling
    data_as_index : bool, optional
        if the first column shall be used as index column
    main_key : str, optional
        if the json or dict does not have the main key as a single `{main_element : dict}` present, it needs to be specified
    order : dict, list, optional
        list with the column names in order or dict with specified key positions
    inverse : bool, optional
        if columns and rows shall be switched

    Returns
    -------
    pandas.DataFrame
        DataFrame representing the dictionary

    """
    if not isinstance(data, dict):
        raise TypeError
    if not isinstance(data_as_index, bool):
        raise TypeError
    if main_key and not isinstance(main_key, str):
        raise TypeError
    if not isinstance(inverse, bool):
        raise TypeError

    from ._helper import _create_sorted_list_from_order, _cast_main_key_name
    from pandas import DataFrame

    if not main_key:
        data, main_key = _cast_main_key_name(data)

    if not order:
        if not inverse:
            data_frame = DataFrame.from_dict(data, orient="index")
        else:
            data_frame = DataFrame.from_dict(data)
        order = list(data_frame)

    else:
        order = _create_sorted_list_from_order(order)
        if not inverse:
            data_frame = DataFrame.from_dict(data, orient="index", columns=order)
        else:
            data_frame = DataFrame.from_dict(data, columns=order)

    if data_as_index:
        data_frame[main_key] = data_frame.index
        data_frame.set_index(order[0], inplace=True)

    data_frame.index.name = main_key

    return data_frame


def pandas_data_frame_to_dict(
    data_frame, main_key_position=0, null_value="delete", header_line=0
):
    """
    Converts a single file_name from xlsx to json

    Parameters
    ----------
    data_frame : pandas.core.frame.DataFrame
    main_key_position : int, optional
    null_value : any, optional
    header_line : int, optional

    Returns
    -------
    dict
        the dictionary representing the xlsx based on `main_key_position`
    """
    from pandas import notnull

    if header_line == 0:
        header = list(data_frame.keys())
    else:
        header = list(data_frame.iloc[header_line - 1])
        data_frame = data_frame[header_line:]
        data_frame.columns = header

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
    data = {header[main_key_position]: data}

    return data


def xml_to_dict(ordered_data, list_reduction, manual_selection):
    """
    Convert a xml/orderedDict to dictionary

    Parameters
    ----------
    ordered_data : orderedDict
    list_reduction : bool
        if lists in the dictionary shall be converted to dictionaries with transformed keys
        (list_key + unique key from dictionary from list_element)
    manual_selection : bool

    Returns
    -------
    dict
        the normalized dictionary

    """

    from collections import OrderedDict
    from ._helper import _reduce_lists, _dictionize

    data = dict()
    for key in ordered_data:
        if isinstance(ordered_data[key], OrderedDict):
            data[key] = _dictionize(ordered_data[key])
        else:
            data[key] = ordered_data[key]

    if list_reduction:
        data = _reduce_lists(data, list_reduction, manual_selection)

    return data
