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


def _csv_to_json(file, main_key_position, null_value, dialect, header_line):
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

    from .write import write_json
    write_json(file.replace(".csv", ".json"), data)
    logger.info("{} rows: {}".format(file.split("/")[-1], rows_no))
    return data


def _json_to_csv(file, key_name, dialect, key_position, if_empty_value, order, data=False):
    """

    Parameters
    ----------
    file : str
    key_name : str
    dialect : [str, None]
    key_position : int
    if_empty_value
    order : [dict, None]

    Returns
    -------

    """
    if not data:
        from .load import load_json
        data = load_json(file)
        logger.info("current file: {}".format(file.split("/")[-1]))
    header_keys = set()

    for element in data:
        for key in data[element].keys():
            header_keys.add(key)

    if not order:
        header = list(header_keys)
        header.insert(key_position, key_name)   # put the json_key to position in csv
    else:
        # order keys need to be int
        if not all(isinstance(order_no, int) for order_no in order.keys()):
            raise ValueError("all keys of order dictionary need to be of type int")

        #
        placed_keys = set(order.values())
        placed_keys.add(key_name)
        order[key_position] = key_name
        header = list(header_keys - placed_keys)
        for order_no in sorted(list(order.keys())):
            header.insert(order_no, order[order_no])

    header_without_ordered_keys = header.copy()
    header_without_ordered_keys.remove(key_name)
    rows = [header]

    for element in data:
        row = [data[element][key] if key in data[element] else if_empty_value for key in header_without_ordered_keys]
        row.insert(key_position, element)
        rows.append(row)

    from .write import write_csv_from_rows
    write_csv_from_rows(file, rows, dialect)
    return rows


def _xml_to_json(file, list_reduction, manual_selection):
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
    print(data)

    if list_reduction:
        data = _reduce_lists(data, list_reduction, manual_selection)

    for key in data:
        print(data[key])
        for key1 in data[key]:
            try:
                print(data[key][key1].keys())
                print(data[key][key1])
            except AttributeError:
                for element in data[key][key1]:
                    print(element)
                pass

    from .write import write_json
    write_json(file.replace("xml", "json"), data)
