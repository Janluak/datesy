Database I/O subpackage
=======================

All functions of `datesy` taking care of database I/O are listed here.
The functionality is the same for all supported database types.
Simply exchange ``_db_helper.Database`` with the desired database.


.. autoclass:: datesy.database_IO._db_helper.Database
   :members:

.. autoclass:: datesy.database_IO._db_helper.Table
   :members:

   .. automethod:: __getitem__


