from aybasics import logger


def _csv_to_json(file, main_key_position, null_value, dialect):
    """
    Converts a single file from csv to json
    Parameters
    ----------
    file : str
        file directory for converting
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
    from json import load
    from csv import writer
    print(key_name)
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

    print("header:", header)
    print(f)

    with open(file.replace("json", "csv"), "w") as fw:
        w = writer(fw, dialect=dialect if dialect else "unix")
        print(header)
        w.writerow(header)
        header.remove(key_name)
        logger.info("filename: {}".format(f))
        print(header)
        for element in f:
            print(element)
            row = [f[element][key] if key in f[element] else if_empty_value for key in header]
            row.insert(key_position, element)
            logger.success(row)
            w.writerow(row)
