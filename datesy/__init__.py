__author__ = "Jan Lukas Braje"
__copyright__ = "Copyright (C) 2019 Jan Lukas Braje"
__versions__ = "0.6.13"  # versioneer

from .convert import *
from .inspect import *
from .matching import *
from .file_IO import *

# shortcuts
load_json = json_file.load
load_csv = csv_file.load
load_xml = xml_file.load
load_xls = xls_file.load
load_xlsx = xls_file.load
write_json = json_file.write
write_csv = csv_file.write
write_xml = xml_file.write
write_xlsx_from_DataFrame = xls_file.write_multi_sheet_from_DataFrames
write_xlsx_from_dict = xls_file.write_multi_sheet_from_dict_of_dicts
