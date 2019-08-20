from aybasics import logger


def _dictionize(sub_dict):
    from collections import OrderedDict
    # ToDo catch #text of attribute and insert values correctly to general #text
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


def _cast_main_key(data):
    if isinstance(data, dict):
        if len(data.keys()) == 1:
            main_key = list(data.keys())[0]
            data = list(data.values())[0]
            return data, main_key
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
    main_key_position : int
    dialect : [str, None]
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
        write_json(file.replace(".csv", ".json"), data)
    logger.info("{} rows: {}".format(file.split("/")[-1], rows_no))
    return data


def _json_to_csv(file, memory, save_to_file, dialect, main_key_position, if_empty_value, order, main_key=None,
                 data=False):
    """

    Parameters
    ----------
    file : str
    main_key : str
    dialect : [str, None]
    main_key_position : int
    if_empty_value
    order : [dict, None]
    data : object

    Returns
    -------

    """
    if not data:
        from .load import load_json
        data = load_json(file)
        logger.info("current file: {}".format(file.split("/")[-1]))
    if not main_key:
        data, main_key = _cast_main_key(data)

    header_keys = set()
    for element in data:
        for key in data[element].keys():
            header_keys.add(key)
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
        write_csv_from_rows(file, rows, dialect)
    return rows


def _xml_to_json(file, memory, save_to_file, list_reduction, manual_selection):
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

    # for key in data:
    #     print(data[key])
    #     for key1 in data[key]:
    #         try:
    #             print(data[key][key1].keys())
    #             print(data[key][key1])
    #         except AttributeError:
    #             for element in data[key][key1]:
    #                 print(element)
    #             pass

    if memory:
        memory[file] = data

    if save_to_file:
        from .write import write_json
        write_json(file.replace(".xml", ".json"), data)


def _json_to_xlsx(file, memory, save_to_file, main_key, sheets, data=False):
    if not data:
        from .load import load_json
        data = load_json(file)
        logger.info("current file: {}".format(file.split("/")[-1]))

    data_frame = _json_to_pandas_data_frame(data, main_key)

    if memory:
        memory[file] = data_frame

    if save_to_file:
        from aybasics import write_xlsx
        write_xlsx(file.replace(".json", ".xlsx"), data_frame, sheets)


def _json_to_pandas_data_frame(data, main_key=None, inverse=False):
    from pandas import DataFrame
    if not main_key:
        data, main_key = _cast_main_key(data)

    if not inverse:
        data_frame = DataFrame.from_dict(data, orient="index")
    else:
        data_frame = DataFrame.from_dict(data)
    data_frame.index.name = main_key

    return data_frame


def _xlsx_to_csv(file, memory, save_to_file, main_key_position, null_value, header_line, sheets):
    raise NotImplemented


def _xlsx_to_json(file, memory, save_to_file, main_key_position, null_value, header_line, sheets):
    from .load import load_xls
    from pandas import notnull
    data_frame = load_xls(file, sheets, ret_single=True)    # ToDo support multiple sheets
    # print("sheets:", sheets)
    # print(data_frame["Tabelle1"])
    # select header_line
    if header_line == 0:
        header = list(data_frame.keys())
    else:
        raise NotImplemented
    """
    # select header_line
    if header_line == 0:
        logger.warning("header_line = 0")
        header = list(data_frame.keys())
    else:
        header = data_frame.iloc[header_line - 1:header_line]
        line_no = 0
        for row in data_frame.itertuples():
            line_no += 1
            if line_no == header_line:
                header = row[1:]
    data_frame = data_frame[header_line + 1:]
    """

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

    """
    # ToDo support multiple sheets
    data = dict()
    for sheet in data_frame:
        print(type(data_frame[sheet]))
        print(data_frame[sheet])
        data[sheet] = data_frame[sheet].where((notnull(data_frame)), exchange_key)

        # delete null_values if null_value == "delete"
        data[sheet] = data_frame[sheet].set_index(header[main_key_position]).T.to_dict()
        for key in data[sheet].copy():
            for key2 in data[sheet][key].copy():
                if not data[sheet][key][key2] and null_value == "delete":
                    del data[sheet][key][key2]
        data[sheet] = {header[0]: data}
        """

    if memory:
        memory[file] = data

    if save_to_file:
        from .write import write_json
        write_json(file.replace(".xlsx" if ".xlsx" in file else ".xls", ".json"), data)
    logger.info("{} rows: {}".format(file.split("/")[-1], data_frame[header[0]].count() + 1))
    return data
