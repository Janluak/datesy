from collections import OrderedDict
import logging
import atexit
from ast import literal_eval
from .sql_query import SQLQueryConstructor

__all__ = ["Database", "Table"]


class Database:
    """
    Representing a database as an object

    On initialization the connection to the database is established.
    For clean working please call ``close()`` at end of db usage.

    Parameters
    ----------
    host : str
        `url` or `ip` of host
    port : int
        port_no
    user : str
        user_name
    password : str
        password for this user
    database : str
        the database to connect to
    auto_creation : bool, optional
        if all tables shall be initiated as variables of object
    kwargs
        specific information to database, see details to each database

    """

    def __init__(self, host, port, user, password, database, auto_creation=False):
        import warnings

        warnings.warn(
            "\n\nDatabase interface still in development. Changes may apply\n",
            UserWarning,
        )
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self.__name = database
        self.__tables = list()

        self._connect_to_db()  # function must be defined for every database representing subclass
        if auto_creation:
            self._construct_all_tables()
        atexit.register(self.close)

    def __enter__(self):
        atexit.unregister(self.close)  # due to context manager no need for atexit
        return self

    @property
    def name(self):
        """
        Name of the database

        Returns
        -------
        str

        """
        return self.__name

    @property
    def tables(self):
        """
        Get the available tables of database

        Returns
        -------
        list
            representing all tables of database

        """
        if not self.__tables:
            self._cursor.execute(self._table_update_query)
            for table_data in self._cursor:
                self.__tables.append(table_data[0])
        return self.__tables

    def update_table_data(self):
        """
        Update the data concerning the list of available tables

        Returns
        -------
        list
            available tables at database

        """
        self.__tables = list()
        return self.tables

    def table(self, table_name):
        """
        Return a database_table as an object

        Parameters
        ----------
        table_name : str
            the desired table

        Returns
        -------
        Table
            class Table as representation of table

        """
        return Table(table_name, self)

    def _check_auto_creation(self):
        doubles = set(self.__dir__()).intersection(set(self.tables))
        if doubles:
            raise EnvironmentError(
                f"builtin function of class matches table_name in database {self.name}\n"
                f"can't create all tables as attributes to database_object\n"
                f"please disable auto_creation or rename matching table '{doubles}' in database"
            )
        hidden_values = {
            table_name for table_name in self.tables if "__" == table_name[0:2]
        }
        if any("__" == table_name[0:2] for table_name in self.tables):
            logging.warning(
                f"table_name in database {self.name} contains '__' in beginning -> not accessable with `Python` "
                f"please disable auto_creation or rename '{hidden_values}' in database"
            )

    def _construct_all_tables(self):
        self._check_auto_creation()
        for table_name in self.tables:
            setattr(self, table_name, Table(table_name, self))

    def close(self):
        """
        Close connection to database

        """
        # ToDo catch exception for unread cursor
        self.__exit__(None, None, None)
        atexit.unregister(self.close)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cursor.close()
        self._conn.close()
        logging.info("closed connection to database")
        if exc_type:
            raise exc_type(exc_val)


class Table:
    """
    Create a representation of a database table

    Parameters
    ----------
    table_name : str
    database : Database

    """

    def __init__(self, table_name, database):
        self.__table_name = table_name
        self.__db = database

        self.__schema = OrderedDict()
        self.__primary = str()  # primary key
        self.__query = SQLQueryConstructor(self.database.name, self.name, self.primary)
        self._debug_query: bool = False

    @property
    def name(self):
        return self.__table_name

    @property
    def database(self):
        return self.__db

    @property
    def query(self):
        return self.__query

    def run_query(self, debug=False):
        """
        Run the currently composed query
        Parameters
        ----------
        debug : bool, optional
            if the query shall be printed to command_line

        Returns
        -------
        list
            data from database

        """
        query = str(self.query)
        if debug or self._debug_query:
            print(query)
        return self.execute_raw_sql(query)

    def execute_raw_sql(self, sql_query):
        """
        Execute raw sql statements

        Parameters
        ----------
        sql_query : str
            sql query

        Returns
        -------
        list
            data from database

        """
        logging.info(f"raw sql_query: {sql_query}")
        self.database._cursor.execute(sql_query)
        rows = list()
        for row in self.database._cursor:
            rows.append(row)
        self.database._conn.commit()
        return rows

    @property
    def schema(self):
        """
        Get schema of table

        Returns
        -------
        OrderedDict
            dictionary containing the column as key and schema_info as dictionary for every column

        """
        if not self.__schema:
            for row in self.execute_raw_sql(self._schema_update_query):
                # ToDo check for more available data via SQL/maybe putting to db specific subclass
                self.__schema[row[0]] = {
                    "type": row[1],
                    "null": row[2],
                    "key": row[3],
                    "default": row[4],
                    "extra": row[5],
                }
        return self.__schema

    @property
    def primary(self):
        """
        Get the primary key of this table

        Returns
        -------
        str, None
            the primary column as string if one exists

        """
        if isinstance(self.__primary, str) and not self.__primary:
            for column in self.schema:
                if self.schema[column]["key"] == "PRI":
                    self.__primary = column
                    break
            if not self.__primary:
                self.__primary = None  # table has no primary key

        return self.__primary

    def update_schema_data(self):
        """
        Update the schema of the table

        Returns
        -------
        OrderedDict
            dictionary containing the column as key and schema_info as dictionary for every column

        """
        self.__schema = OrderedDict()
        self.__primary = str()
        return self.schema

    def update_primary_data(self):
        """
        Update the primary key of the table

        Returns
        -------
        str, None
            the primary column as string if one exists
        """
        self.__schema = OrderedDict()
        self.__primary = str()
        return self.primary

    def _get_column_values(self, *columns):
        self.query.add_desired_columns(*columns)
        if len(self.query.columns) == 1:
            values = self.run_query()
            return [i[0] for i in values]
        else:
            return self.run_query()

    def __len__(self):
        self.query.length_request()
        return int(self.run_query()[0][0])

    def __iter__(self):
        if self.primary:
            self._keys = iter(self._get_column_values(self.primary))
            return self._keys
        else:
            range_list = range(len(self))
            # ToDo make a generator for not fetching data after a stop in loop occurred
            return iter(
                self.execute_raw_sql(self.query.limit(1, offset))[0]
                for offset in range_list
            )

    def __getitem__(self, key):
        """
        Get row of primary key

        works like ``value = database.table[key]``

        Parameters
        ----------
        key : any
            matching value in primary column

        Returns
        -------
        Row
            tuple items representing every matched row in database

        """

        if not self.primary:
            raise AttributeError(
                "table has no primary_key column. operation not permitted"
            )

        self.query.add_where_statements(**{self.primary: key})
        data = self.run_query()
        if len(data) != 1:
            raise KeyError(f"{key} not in table {self.name}")
        [row] = data
        return Row(self, row)

    def get_where(self, *args, **kwargs):
        """
        Get rows where value matches the defined column: ``columns=key``

        Parameters
        ----------
        **kwargs
            column = key values

        Returns
        -------
        list(Row)
            tuple items representing every matched row in database

        """
        self.query.add_where_statements(*args, **kwargs)
        rows = [Row(self, row) for row in self.run_query()]
        return rows

    def _parse_input_row_data(self, row: (list, dict), primary_key=None):
        if isinstance(row, dict) and primary_key:
            row[self.primary] = primary_key
            return row

        elif isinstance(row, dict):
            return row

        elif isinstance(row, list):
            if primary_key:
                row.insert(list(self.schema).index(self.primary), primary_key)
            if len(row) != len(self.schema):
                raise ValueError(
                    f"length of given row (given {len(row)} must be same length of table "
                    f"({len(self.schema)})\nemtpy values must be represented with '' or str()"
                )
            data = dict()
            for pos in range(len(row)):
                if row[pos] != "":
                    data[list(self.schema.keys())[pos]] = row[pos]
            return data

        else:
            raise TypeError("row must be either list or dict")

    def __setitem__(self, primary_key, row):
        """
        Set/update a single row for primary key

        works like ``database.table[key] = row``

        Parameters
        ----------
        primary_key : any, None
            the value of the primary column. If None -> new row inserted
        row : list, dict
            the row data in either correct order or in a dict with column_name

        """
        if not self.primary:
            raise AttributeError(
                "table has no primary_key column. operation not permitted"
            )

        if isinstance(row, list) and len(row) + 1 != len(self.schema):
            raise ValueError(
                "row must be same length as table (without primary key) with '' for emtpy values"
            )

        try:
            self.__getitem__(primary_key)
            if isinstance(row, list):
                row.insert(list(self.schema.keys()).index(self.primary), primary_key)
            elif isinstance(row, dict):
                row[self.primary] = primary_key
            self.update_where(row, primary_key=primary_key)
        except KeyError:
            self.insert(row, primary_key)

    def update_where(
        self,
        values: (list, dict),
        *args,
        primary_key=None,
        limit_rows: int = False,
        **kwargs,
    ):
        """
        Update all rows based on given conditions

        Parameters
        ----------
        values : list, dict
            new values to set. either as a full row in a list or specified columns with dictionary
        args
            conditions
        primary_key : any, optional
            the value of the primary column (if table has primary_key)
        limit_rows : int
            number of rows to affect
        kwargs
            conditions

        """
        if primary_key:
            kwargs[self.primary] = primary_key

        values = self._parse_input_row_data(values)

        self.query.add_new_values(**values)

        self.query.add_where_statements(*args, **kwargs)
        if limit_rows:
            self.query.limit(limit_rows)

        self.run_query()

    def insert(self, row: (list, dict), primary_key=None):
        """
        Insert new row

        Parameters
        ----------
        row : list, dict
            row_data
        primary_key : any, optional
            primary_key optional for tables with primary_key

        """
        row = self._parse_input_row_data(row, primary_key)

        self.query.add_new_values(**row)
        self.run_query()

    def __delitem__(self, key):
        """
        Delete single row for given primary key

        works like ``del database.table[key]``

        Parameters
        ----------
        key : any
            matching value in primary column

        """
        if not self.primary:
            raise AttributeError(
                "table has no primary_key column. operation not permitted"
            )

        self.__getitem__(key)
        self.delete_where(**{self.primary: key})

    def delete_where(self, *args, **kwargs):
        """
        Delete rows matching the where conditions

        Parameters
        ----------
        args : conditions
        kwargs : conditions

        """
        if not args and not kwargs:
            raise OverflowError("Please use truncate to delete the hole table")
        self.query.delete_request()
        self.query.add_where_statements(*args, **kwargs)
        self.run_query()

    # def as_dict(self):
    #     if not self.primary:
    #         raise AttributeError(
    #             "table has no primary_key column. operation not permitted"
    #         )
    #
    #     # ToDo download all data and return as dict
    #     raise NotImplemented("coming soon")
    #
    # def as_rows(self):
    #     # ToDo download all data and return as rows
    #     raise NotImplemented("coming soon")
    #
    # def as_df(self):
    #     # ToDo download all data and return as pandas.dataframe
    #     raise NotImplemented("coming soon")

    def truncate(self):
        self.execute_raw_sql(f"TRUNCATE TABLE {self.name}")

    # ToDo implement min/max

    # ToDo implement is (not) NULL


class Row:
    """
    Representation of a database row entry

    Parameters
    ----------
    table: Table
        table belonging to
    data: list, tuple, dict
        data to represent
    """

    def __init__(self, table, data):
        self.__table: Table = table
        self.__schema = table.schema
        self.__columns = table.schema.keys()

        if isinstance(data, (list, tuple)):
            self.__content = OrderedDict()
            pos = 0
            for key in table.schema:
                self.__content[key] = data[pos]
                pos += 1

        elif isinstance(data, (dict, OrderedDict)):
            if not all(key in table.schema for key in data):
                raise ValueError("columns of row not in table schema")
            self.__content = data

        else:
            raise TypeError(f"data must be either list or dict, not {type(data)}")

    def schema_validation(self, key, value):
        # ToDo do local schema validation for saving time in connection to server?
        return True

    def _where_reference_to_row(self, *missing_columns):
        """
        Create a query reference to the belonging row

        """

        if self.__table.primary:
            self.__table.query.add_where_statements(
                **{self.__table.primary: self.__content[self.__table.primary]}
            )
        else:
            if missing_columns:
                columns = set(self.__table.schema.keys()) - set(missing_columns)
                self.__table.query.add_desired_columns(*columns)
            self.__table.query.add_where_statements(**self.__content)
            self.__table.query.limit(1)

    def sync(self, *missing_columns):
        """
        Update row from database to local

        Parameters
        ----------
        missing_columns : str, optional
            if rows shall be left out when updating (e.g. if known that a timestamp has changed and it shall be fetched)

        """
        self._where_reference_to_row(*missing_columns)
        if not self.__table.primary:
            self.__table.query.limit(1)
        try:
            self.__init__(self.__table, self.__table.run_query()[0])
        except IndexError:
            raise LookupError("The query did not work, no result from database")

    def __getitem__(self, column):
        """
        Get column_value of row
        
        works like ``value = database.table.row[column]``
        
        Parameters
        ----------
        column : int, str
            position in table or column_name

        Returns
        -------
        Item

        """
        if isinstance(column, int):
            column = list(self.__columns)[column]
        elif not isinstance(column, str):
            raise TypeError("only int for position or str for column name allowed")

        return Item(self, column, self.__table, self.__content[column])

    def __setitem__(self, column, value):
        """
        Set new value to column

        works like ``database.table.row[column] = value``

        Parameters
        ----------
        column : int, str
            position in table or column_name
        value : any
            new value

        """
        if isinstance(column, int):
            column = list(self.__columns)[column]
        elif not isinstance(column, str):
            raise TypeError("only int for position or str for column name allowed")

        if not self.schema_validation(column, value):
            raise TypeError(
                f"wrong data type! for given column `{column}` type {self.__schema[column]['type']} required"
            )

        if not self.__table.primary or column == self.__table.primary:
            self.__table.update_where({column: value}, limit_rows=1, **self.__content)
        else:
            self.__table.update_where(
                {column: value},
                **{self.__table.primary: self.__content[self.__table.primary]},
            )

        self.sync(column)

    def __delitem__(self, column):
        """
        Delete/reset to default a column

        works like ``del database.table.row[column]``

        Parameters
        ----------
        column : int, str
            position in table or column_name

        """

        if isinstance(column, int):
            column = list(self.__columns)[column]
        elif not isinstance(column, str):
            raise TypeError("only int for position or str for column_name allowed")

        self.__setitem__(column, self.__schema[column]["default"])

    def __len__(self):
        return len(self.__content.values())

    def __repr__(self):
        return repr(self.__content)

    def __iter__(self):
        return iter(self.__content.values())

    def __str__(self):
        return str(tuple(self.__content.values()))

    def __dict__(self):
        return self.__content


class Item(object):
    """
    Representation of a database entry

    Parameters
    ----------
    row: Row

    column: str

    table: Table

    value: any
    """

    def __init__(self, row, column, table, value=None):
        try:
            self.__value = literal_eval(value)
        except ValueError:
            self.__value = value
        self.__row: Row = row
        self.__column = column
        self.__table: Table = table
        self.__real_type = table.schema[column]["type"]
        self.__python_type = type(self.__value)
        self._switchable_types = tuple()

    @property
    def value(self):
        """
        Value of this item

        Returns
        -------
        value : any
        """
        return self.__value

    @property
    def column(self):
        """
        Column this item belonging to

        Returns
        -------
        column : str

        """
        return self.__column

    @property
    def table(self):
        """
        Table this item is belonging to

        Returns
        -------
        table :  Table

        """
        return self.__table

    @property
    def database(self):
        """
        Database this item is belonging to

        Returns
        -------
        database : Database
        """
        return self.__table.database

    def sync(self):
        """
        Update entry from database to local

        """
        self.table.query.add_desired_columns(self.column)
        self.__row._where_reference_to_row()
        try:
            result = self.table.run_query()
            self.__value = result[0][0]
            return self.__value
        except IndexError:
            raise LookupError("The query did not work, no result from database")

    def __set__(self, instance, value):
        """
        Set new value

        Parameters
        ----------
        instance
        value : any
            new value

        """
        if not isinstance(
            value, (self.__python_type, type(None)) + self._switchable_types
        ):
            raise TypeError(f"expected {self.__python_type}, got {type(value)}")
        # ToDo schema validation
        self.table.query.add_new_values(**{self.column: value})
        self.__row._where_reference_to_row(self.column)
        self.table.run_query()

        self.sync()

    def __delete__(self, instance):
        """
        Delete/reset to default this value

        """

        self.__set__(self, self.table.schema[self.column]["default"])

    def __repr__(self):
        return repr(self.__value)

    def __int__(self):
        return int(self.__value)

    def __float__(self):
        return float(self.__value)

    def __str__(self):
        return str(self.__value)

    def __iter__(self):
        return iter(self.__value)

    def __len__(self):
        return len(self.__value)

    def __getitem__(self, item):
        if isinstance(self.__value, dict):
            return self.__value[item]
        else:
            raise TypeError("'Item' object is not subscribable")
