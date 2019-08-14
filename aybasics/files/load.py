

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
