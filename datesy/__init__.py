__author__ = "Jan Lukas Braje"
__copyright__ = "Copyright (C) 2019 Jan Lukas Braje"
__versions__ = "0.6.12"  # versioneer

from .convert import *
from .inspect import *
from .matching import *
from .file_IO import *

# shortcuts
load_json = json_file.load
load_csv = csv_file.load
write_json = json_file.write
write_csv = csv_file.write
load_xml = xml_file.load
