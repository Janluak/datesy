from aybasics import logger
from aybasics.files._converting import _cast_main_key


def write_json(file: str, data: dict):
    """
    saves a dictionary to file as json

    Parameters
    ----------
    file : str
        the file_name to save under. if no ending is provided, saved as .json
    data : dict
        the dictionary to be saved as json

    """
    if "." not in file:
        file += ".json"
    logger.info("saving to file: {}".format(file))
    from json import dump
    with open(file, 'w') as fp:
        dump(data, fp)


def write_csv_from_dict(file: str, data: dict, main_key=None, order=None, if_empty_value=None, main_key_position=0, **kwargs):
    """
    saves a row based document to csv file from a dictionary
    Parameters
    ----------
    file : str
        the file_name to save under. if no ending is provided, saved as .csv
    data : dict
        the dictionary to be saved as json
    main_key : str
        if the json or dict does not have the main key as a single {main_key : dict} present, it needs to be specified
    order : dict {int: [str, int, float]}
        for defining a specific order of the
    if_empty_value
        the value to set when no data is available
    main_key_position : int
        the position in csv of the json key
    kwargs
        csv dialect options

    """
    if not main_key:
        data, main_key = _cast_main_key(data)

    if "." not in file:
        file += ".csv"
    if kwargs:
        from .converting import _register_csv_dialect
        _register_csv_dialect(**kwargs)

    logger.info("saving to file: {}".format(file))
    from ._converting import _json_to_csv

    _json_to_csv(file=file, main_key=main_key, main_key_position=main_key_position, if_empty_value=if_empty_value, order=order,
                 data=data, dialect="custom" if kwargs else None, memory=None, save_to_file=True)


def write_csv_from_rows(file: str, rows: list, **kwargs):
    """
    saves a row based document from rows to file

    Parameters
    ----------
    file : str
        the file_name to save under. if no ending is provided, saved as .csv
    rows : list
        list of lists to write to file
    kwargs
        csv dialect options

    """
    if "." not in file:
        file += ".csv"
    logger.info("saving to file: {}".format(file))
    from csv import writer
    if kwargs and "dialect" not in kwargs:
        from .converting import _register_csv_dialect
        _register_csv_dialect(**kwargs)
    with open(file.replace(".json", ".csv"), "w") as fw:
        w = writer(fw,  dialect="custom" if kwargs and "dialect" not in kwargs else "unix")
        logger.info("filename: {}".format(file))
        for row in rows:
            w.writerow(row)


def write_xlsx(file: str, data_frame, sheet=None):
    """
    saves a pandas data_frame to file
    Parameters
    ----------
    file : str
        the file_name to save under. if no ending is provided, saved as .xlsx
    data_frame : [pandas.DataFrame, dict]
        either a data_frame or a dict of data_frames
    sheet : str
        a sheet name for the data
        ! only for single data_frames. otherwise the dict[key] is used for sheet name !

    """
    if "." not in file:
        file += ".xlsx"
    logger.info("saving to file: {}".format(file))
    from pandas import ExcelWriter
    writer = ExcelWriter(file)
    if isinstance(data_frame, dict):
        for key in data_frame:
            data_frame[key].to_excel(writer, sheet_name=key)
    else:
        data_frame.to_excel(writer, sheet_name=sheet if sheet else "Sheet1")
    writer.save()
