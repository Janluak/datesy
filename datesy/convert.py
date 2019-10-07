__doc__ = (
    "All actions of transforming data from different file formats are to be found here"
)
__all__ = [
    "rows_to_dict",
    "dict_to_rows",
    "pandas_data_frame_to_dict",
    "dict_to_pandas_data_frame",
    "xml_to_standard_dict",
]


def rows_to_dict(
    rows,
    main_key_position=0,
    null_value="delete",
    header_line=0,
    contains_open_ends=False,
):
    """
    Convert a row of rows (e.g. csv) to dictionary

    Parameters
    ----------
    rows : list(lists)
        the row based data to convert to `dict`
    main_key_position : int, optional
        if the main_key is not on the top left, its position can be specified
    null_value : any, optional
        if an emtpy field in the lists shall be represented somehow in the dictionary
    header_line : int, optional
        if the header_line is not the first one, its position can be specified
    contains_open_ends : bool, optional
        if each row is not in the same length (due to last set entry as last element in row),
        a length check for corrupted data can be ignored

    Returns
    -------
    dict
        dictionary containing the information from row-based data

    """
    data = dict()
    header = rows[header_line]

    for row in rows[header_line + 1 :]:
        sub_data = dict()
        for i in range(len(header)):
            if i == main_key_position:
                continue
            elif i >= len(row):
                if not contains_open_ends:
                    raise IndexError("not all elements are the same length")
                elif null_value != "delete":
                    sub_data[header[i]] = null_value
            elif not row[i] and null_value != "delete":
                sub_data[header[i]] = null_value
            elif not row[i]:
                continue
            else:
                sub_data[header[i]] = row[i]

        data[row[main_key_position]] = sub_data

    data = {header[main_key_position]: data}

    return data


def dict_to_rows(
    data, main_key_name=None, main_key_position=None, if_empty_value=None, order=None
):
    """
    Convert a dictionary to rows (list(lists))

    Parameters
    ----------
    data : dict
        the data to convert in form of a dictionary
    main_key_name : str, optional
        if the data isn't provided as `{main_key: data}` the key needs to be specified
    main_key_position : int, optional
        if the main_key shall not be on top left of the data the position can be specified
    if_empty_value : any, optional
        if a main_key's sub_key is not set something different than `blank` can be defined
    order : dict, list, None, optional
        if a special order for the keys is required

    Returns
    -------
    list(lists)
        list of rows representing the csv based on the `main_element_position`

    """
    if not main_key_name:
        from ._helper import _cast_main_key_name

        data, main_key_name = _cast_main_key_name(data)

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
            main_key_position if main_key_position else 0, main_key_name
        )  # put the json_key to position in csv
    else:
        from ._helper import _create_sorted_list_from_order

        # ToDo check what happens if orderedDict is used instead of dict -> crash with order?
        header = _create_sorted_list_from_order(
            all_elements=header_keys,
            order=order,
            main_element=main_key_name,
            main_element_position=main_key_position,
        )

    header_without_ordered_keys = header.copy()
    header_without_ordered_keys.remove(main_key_name)
    rows = [header]

    for element in data:
        row = [
            data[element][key] if key in data[element] else if_empty_value
            for key in header_without_ordered_keys
        ]
        row.insert(main_key_position if main_key_position else 0, element)
        rows.append(row)

    return rows


def dict_to_pandas_data_frame(
    data, data_as_index=False, main_key_name=None, order=None, inverse=False
):
    """
    Convert a dictionary to pandas.DataFrame

    Parameters
    ----------
    data : dict
        dictionary of handling
    data_as_index : bool, optional
        if the first column shall be used as index column
    main_key_name : str, optional
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
    if main_key_name and not isinstance(main_key_name, str):
        raise TypeError
    if not isinstance(inverse, bool):
        raise TypeError

    from ._helper import _create_sorted_list_from_order, _cast_main_key_name
    from pandas import DataFrame

    if not main_key_name:
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
        data_frame[main_key_name] = data_frame.index
        data_frame.set_index(order[0], inplace=True)

    data_frame.index.name = main_key_name

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


def xml_to_standard_dict(
    ordered_data,
    reduce_orderedDicts=False,
    reduce_lists=False,
    manual_selection_for_list_reduction=False,
):
    """
    Convert a xml/orderedDict to normal dictionary

    Parameters
    ----------
    ordered_data : orderedDict
        input xml data to convert to standard dict
    reduce_orderedDicts : bool, optional
        if collections.orderedDicts shall be converted to normal dicts
    reduce_lists : bool, list, set, optional
        if lists in the dictionary shall be converted to dictionaries with transformed keys
        (list_key + unique key from dictionary from list_element)
        if list or set is provided, only these values will be reduced
    manual_selection_for_list_reduction : bool, optional
        if manually decision on list reduction shall be used
        all keys in ``reduce_lists`` will be automatically reduced

    Returns
    -------
    dict
        the normalized dictionary

    """

    from collections import OrderedDict
    from ._helper import _reduce_lists, _dictionize

    data = dict()
    if reduce_orderedDicts:
        for key in ordered_data:
            if isinstance(ordered_data[key], OrderedDict):
                data[key] = _dictionize(ordered_data[key])
            else:
                data[key] = ordered_data[key]

    if manual_selection_for_list_reduction:
        raise NotImplemented
        # if reduce_lists and not isinstance(reduce_lists, bool):
        #     data = _reduce_lists(data, reduce_lists, manual_selection_for_list_reduction)
        # # manual selection here
    elif reduce_lists:
        data = _reduce_lists(data, reduce_lists, manual_selection_for_list_reduction)

    return data
