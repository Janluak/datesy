from aybasics import logger


def load_json(files):
    from json import load
    data = dict()
    if not isinstance(files, list):
        files = [files]
    for file in files:
        with open(file, "r") as f:
            data[file] = load(f)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_csv(files, dialect=None):
    from csv import reader
    data = dict()
    if not isinstance(files, list):
        files = [files]
    for file in files:
        with open(file, "r") as f:
            data[file] = list()
            rows = reader(f, dialect=dialect if dialect else "unix")
            for row in rows:
                data[file].append(row)
    try:
        [value] = data.values()
        return value
    except ValueError:
        return data


def load_xls(files, sheets=None, ret_single=False):
    from pandas import read_excel, ExcelFile
    data = dict()
    if not isinstance(files, list):
        files = [files]
    for file in files:
        data[file] = dict()
        excel_file = ExcelFile(file)
        if not sheets:
            for sheet in excel_file.sheet_names:
                data[file][sheet] = read_excel(file, sheet_name=sheet)
        else:
            if not isinstance(sheets, list):
                sheets = [sheets]
            for sheet in sheets:
                data[file][sheet] = read_excel(file, sheet_name=sheet)
        if ret_single:  # ToDo get rid after supporting multiple sheets in _converting.py
            data[file] = read_excel(file)

    try:
        [value] = data.values()
        return value
    except ValueError:
        return data
