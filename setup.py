"""
The setup file.
If development mode (=changes in package code directly delivered to python) `pip install -e .` in directory of this file
"""

from setuptools import setup

# https://python-packaging.readthedocs.io/en/latest/minimal.html

setup(name='aybasics',
      version='1.0',
      description='Some basic tools for IM and doing stuff with data',
      url='###',
      author='Jan Lukas Braje',
      author_email='jan@braje.org',
      license='Apache 2.0',
      packages=[],
      python_requires='>=3.7',
      zip_safe=False,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Information Technology",
          "License :: OSI Approved :: Apache Software License 2.0",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3.7"
      ],
      # https://pypi.org/pypi?%3Aaction=list_classifiers
      install_requires=[
          "loguru",
          "numpy",
          "pandas",
          "xmltodict"

      ])
