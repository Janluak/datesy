from aybasics import logger


def write_json(file, data):
    logger.info("saving to file: {}".format(file))
    from json import dump
    with open(file, 'w') as fp:
        dump(data, fp)


def write_csv_from_dict(file, data, key_name, order=None, if_empty_value=None, key_position=0, **kwargs):
    from ._converting import _json_to_csv
    if kwargs:
        from .converting import _register_csv_dialect
        _register_csv_dialect(**kwargs)

    _json_to_csv(file=file, main_key=key_name, main_key_position=key_position, if_empty_value=if_empty_value, order=order,
                 data=data, dialect="custom" if kwargs else None)


def write_csv_from_rows(file, rows, dialect):
    logger.info("saving to file: {}".format(file))
    from csv import writer
    with open(file.replace(".json", ".csv"), "w") as fw:
        w = writer(fw, dialect=dialect if dialect else "unix")
        logger.info("filename: {}".format(file))
        for row in rows:
            w.writerow(row)


def write_xlsx(file, data_frame, sheet=None):
    logger.info("saving to file: {}".format(file))
    from pandas import ExcelWriter
    writer = ExcelWriter(file)
    if isinstance(data_frame, dict):
        for key in data_frame:
            data_frame[key].to_excel(writer, sheet_name=key)
    else:
        data_frame.to_excel(writer, sheet_name=sheet if sheet else "Sheet1")
    writer.save()
