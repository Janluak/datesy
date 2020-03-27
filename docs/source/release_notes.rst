Release Notes
=============

0.8.1
*****

Bug Fixes
~~~~~~~~~

* sql_query: possible to use strings as values when using ``…where(column=value)``



0.8.0
*****

database connection: connect to a database and interact with it in a pythonic way

Features
~~~~~~~~

* database abstraction available

    * database
    * table
    * row
    * item

* database interaction now possible for:

    * mysql


0.7.1
*****

saving jsons: beautified to human readability & sorting keys available

0.7.0
*****

initial release

Features
~~~~~~~~

* reading/writing file types

    * csv
    * json
    * xml
    * xls(x)

* converting data types

    * rows -> dict
    * dict -> rows
    * dict -> DataFrame
    * DataFrame -> dict

* matching strings

    * simplifying strings
    * fast/considerate matching
    * matching with manual selection

Bug Fixes
~~~~~~~~~

* initial release
