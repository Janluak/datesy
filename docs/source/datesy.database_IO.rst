Database I/O subpackage
=======================

All functions of `datesy` taking care of database I/O are listed here.
The functionality is the same for all supported database types.
Simply exchange ``_db_helper.Database`` with the desired database.


Database
--------

.. autoclass:: datesy.database_IO._db_helper.Database
   :members:

Table
-----

.. autoclass:: datesy.database_IO._db_helper.Table
   :members:

   .. automethod:: __getitem__
   .. automethod:: __setitem__
   .. automethod:: __delitem__

Row
---

.. autoclass:: datesy.database_IO._db_helper.Row
   :members:

   .. automethod:: __getitem__
   .. automethod:: __setitem__
   .. automethod:: __delitem__

Item
----

.. autoclass:: datesy.database_IO._db_helper.Item
   :members:

   .. automethod:: __set__
   .. automethod:: __delete__

