
`datesy` helps you to easily convert certain types of data.
Typical data formats are row-based or in form of a dictionary.

Rows to dictionary
~~~~~~~~~~~~~~~~~~

When e.g. reading a csv_file as stated above, a row-based data structure is returned.
If for further processing the rows shall be dictionized, it's as simple as this:

.. code-block:: python

    example_rows = [
                    ["Header1", "Header2", "Header3"],
                    ["Value11", "Value12", "Value13"],
                    ["Value21", "Value22", "Value23"]
                   ]

    example_rows = datesy.rows_to_dict(rows=example_dict)


    example_dict = {
                     "Header1": {
                       "Value11": {
                         "Header2": "Value12",
                         "Header3": "Value13",
                       },
                       "Value21": {
                         "Header2": "Value22",
                         "Header3": "Value23"
                       }
                     }
                   }

Relevant ID position / main key position:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It might occur, your most relevant key is not on the first position:

.. code-block:: python

    example_rows = [
                    ["Header1", "Header2", "Header3"],
                    ["Value11", "Value12", "Value13"],
                    ["Value21", "Value22", "Value23"]
                   ]
    example_dict = datesy.rows_to_dict(rows=example_rows, main_key_position=2)

    example_dict = {
                     "Header3": {
                       "Value13": {
                         "Header1": "Value11",
                         "Header2": "Value12"
                       },
                       "Value23": {
                         "Header1": "Value21",
                         "Header2": "Value22"
                       }
                     }
                   }

As you can see, the third entry (`int=2`) is used as the main_key.


Missing values
^^^^^^^^^^^^^^

Of course, data may be missing a value:

.. code-block:: python

    example_rows = [
                    ["Header1", "Header2", "Header3"],
                    ["Value11",, "Value13"],
                    ["Value21", "Value22", "Value23"]
                   ]
    example_dict = datesy.rows_to_dict(rows=example_rows, null_value="delete")

    example_dict = {
                     "Header1": {
                       "Value11": {
                         "Header3": "Value13"
                       },
                       "Value21": {
                         "Header2": "Value22",
                         "Header3": "Value23"
                       }
                     }
                   }

As you can see, the emtpy value in the rows is not represented in the dictionary.
Instead of missing the header_key you can also put any other value than ``delete`` to this parameter for putting this to the exact spot:

.. code-block:: python

    example_rows = [
                    ["Header1", "Header2", "Header3"],
                    ["Value11",, "Value13"],
                    ["Value21", "Value22", "Value23"]
                   ]

    example_dict = datesy.rows_to_dict(rows=example_rows, null_value=None)

    example_dict = {
                     "Header1": {
                       "Value11": {
                         "Header2": None,
                         "Header3": "Value13"
                       },
                       "Value21": {
                         "Header2": "Value22",
                         "Header3": "Value23"
                       }
                     }
                   }


Open ends / missing last row entries
....................................

If the rows do not contain emtpy values at the end of the row:

Normally, a check prevents handling this data as row-based data should always have the same length.
Yet, if emtpy values at the end of the row are not stored like this, you can disable this check and still convert data:

.. code-block:: python

    example_rows = [
                    ["Header1", "Header2", "Header3"],
                    ["Value11", "Value12"],
                    ["Value21", "Value22", "Value23"]
                   ]

    example_dict = datesy.rows_to_dict(rows=example_rows, contains_open_ends=True)

    example_dict = {
                     "Header1": {
                       "Value11": {
                         "Header2": "Value12"
                       },
                       "Value21": {
                         "Header2": "Value22",
                         "Header3": "Value23"
                       }
                     }
                   }


Selecting the header_line
^^^^^^^^^^^^^^^^^^^^^^^^^

For irrelevant data at the top of the row-based data, you can set the header_line to the desired position:

.. code-block:: python

    example_rows = [
                    ["Undesired1", "Undesired2", "Undesired3"],
                    ["Header1", "Header2", "Header3"],
                    ["Value11", "Value12", "Value13"],
                    ["Value21", "Value22", "Value23"]
                   ]

    example_dict = datesy.rows_to_dict(rows=example_rows, header_line=1)

    example_dict = {
                     "Header1": {
                       "Value11": {
                         "Header2": "Value12",
                         "Header3": "Value13"
                       },
                       "Value21": {
                         "Header2": "Value22",
                         "Header3": "Value23"
                       }
                     }
                   }


Dictionary to rows
~~~~~~~~~~~~~~~~~~

Just as simple is the converting vice_versa from dictionary to rows:

.. code-block:: python

    example_dict = {
                 "Header1": {
                   "Value11": {
                     "Header2": "Value12",
                     "Header3": "Value13",
                   },
                   "Value21": {
                     "Header2": "Value22",
                     "Header3": "Value23"
                   }
                 }
               }

    example_rows = datesy.dict_to_rows(data=example_dict)

    example_rows = [
                    ["Header1", "Header2", "Header3"],
                    ["Value11", "Value12", "Value13"],
                    ["Value21", "Value22", "Value23"]
                   ]

Missing keys / not set data
^^^^^^^^^^^^^^^^^^^^^^^^^^^

When having data where certain keys are not set:

.. code-block:: python

    example_dict = {
                     "Header1": {
                       "Value11": {
                         "Header2": "Value12"
                       },
                       "Value21": {
                         "Header2": "Value22",
                         "Header3": "Value23"
                       }
                     }
                   }

    example_rows = datesy.dict_to_rows(data=example_dict)

    example_rows = [
                    ["Header1", "Header2", "Header3"],
                    ["Value11", "Value12", ],
                    ["Value21", "Value22", "Value23"]
                   ]


Specify emtpy values:
.....................

Of course you can specify values to be set if a key is not set/emtpy:

.. code-block:: python

    example_dict = {
                     "Header1": {
                       "Value11": {
                         "Header2": "Value12"
                       },
                       "Value21": {
                         "Header2": "Value22",
                         "Header3": "Value23"
                       }
                     }
                   }

    example_rows = datesy.dict_to_rows(data=example_dict, if_emtpy_value=False)

    example_rows = [
                    ["Header1", "Header2", "Header3"],
                    ["Value11", "Value12", False],
                    ["Value21", "Value22", "Value23"]
                   ]

Ordering the header
^^^^^^^^^^^^^^^^^^^

Just like picking the most relevant key in `rows_to_dict`, you can specify a certain order for the row-based data:

.. code-block:: python

    example_dict = {
                     "Header1": {
                       "Value11": {
                         "Header2": "Value12",
                         "Header3": "Value13"
                       },
                       "Value21": {
                         "Header2": "Value22",
                         "Header3": "Value23"
                       }
                     }
                   }

    example_rows = datesy.dict_to_rows(data=example_dict, order=["Header2", "Header3", "Header1"])

    example_rows = [
                    ["Header2", "Header3", "Header1"],
                    ["Value12", "Value13", "Value11"],
                    ["Value22", "Value23", "Value21"]
                   ]


Data without main_key
^^^^^^^^^^^^^^^^^^^^^

What happens if you have data without a main_key like `Header1` specified? Simply tell `datesy` about it:

.. code-block:: python

    example_dict = {
                     "Value11": {
                       "Header2": "Value12",
                       "Header3": "Value13",
                     },
                     "Value21": {
                       "Header2": "Value22",
                       "Header3": "Value23"
                     }
                   }


    example_rows = datesy.dict_to_rows(data=example_dict, main_key_name="Header1")

    example_rows = [
                    ["Header1", "Header2", "Header3"],
                    ["Value11", "Value12", "Value13"],
                    ["Value21", "Value22", "Value23"]
                   ]



