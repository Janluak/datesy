"""
The setup file_name.
If development mode (=changes in package code directly delivered to python) `pip install -e .` in directory of this file_name
"""

from setuptools import setup
from static_information import *

# https://python-packaging.readthedocs.io/en/latest/minimal.html

setup(name=project_name,
      version=version,
      description='basic tools for taking care for making the intro to handling handling with python easier',
      url=url,
      author=author,
      author_email=author_email,
      license=packet_license,
      packages=["aybasics"],
      python_requires='>=3.7',
      zip_safe=False,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Information Technology",
          "License :: OSI Approved :: Apache Software License 2.0",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3.7"
      ],
      # https://pypi.org/pypi?%3Aaction=list_classifiers
      install_requires=[
          "numpy",
          "pandas",
          "xmltodict",
          "xlrd",
          "openpyxl"

      ])
