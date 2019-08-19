from aybasics import logger


# ToDo use load.py module for file loading
# ToDo source writing parts to new module write

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


def _csv_to_json(file, main_key_position, null_value, dialect):
    """
    Converts a single file from csv to json
    Parameters
    ----------
    file : str
    main_key_position : int
    dialect : [str, None]
    null_value

    Returns
    -------
    data : dict
        dictionary containing the information from csv

    """
    import json, csv
    rows = 0
    data = dict()
    with open(file, "r") as f:
        logger.info("current file: {}".format(file.split("/")[-1]))
        f = csv.reader(f, dialect=dialect if dialect else "unix")
        header = next(f)
        for row in f:
            if null_value == "delete":
                data[row[main_key_position]] = {header[i]: row[i] for i in range(len(header)) if
                                                row[i] and i != main_key_position}
            else:
                data[row[main_key_position]] = {header[i]: row[i] if row[i] else null_value for i in range(len(header))
                                                if i != main_key_position}
            rows += 1

        with open(file.replace("csv", "json"), 'w') as fp:
            json.dump(data, fp)
        logger.info("{} rows: {}".format(file.split("/")[-1], rows))
    return data


def _json_to_csv(file, key_name, dialect, key_position, if_empty_value, order):
    """

    Parameters
    ----------
    file : str
    key_name : str
    dialect : str
    key_position : int
    if_empty_value
    order : dict

    Returns
    -------

    """

    from json import load
    from csv import writer
    with open(file, "r") as f:
        logger.info("current file: {}".format(file.split("/")[-1]))
        f = load(f)

        header_keys = set()

        for element in f:
            for key in f[element].keys():
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

    with open(file.replace("json", "csv"), "w") as fw:
        w = writer(fw, dialect=dialect if dialect else "unix")
        w.writerow(header)
        header.remove(key_name)
        logger.info("filename: {}".format(f))
        for element in f:
            row = [f[element][key] if key in f[element] else if_empty_value for key in header]
            row.insert(key_position, element)
            logger.success(row)
            w.writerow(row)


def _xml_to_json(file, list_reduction, manual_selection):
    from collections import OrderedDict
    from json import dump

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

    with open(file.replace("xml", "json"), 'w') as fp:
        dump(data, fp)
