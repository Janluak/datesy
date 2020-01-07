from collections import OrderedDict
import logging, re
import atexit

__all__ = ["Database", "Table"]


class Table:
    """
    Create a representation of a database table

    Parameters
    ----------
    table_name : str
    database : Database

    """
    def __init__(self, table_name, database):
        self._table = table_name
        self._db = database

        self.__schema = OrderedDict()
        self.__primary = str()  # primary key
        self.__column_for_request = str()

        self.working_columns = set()  # desired columns for interaction

    def _build_query(self, *args, **kwargs):
        """
        Compose the query for the desired task

        Parameters
        ----------
        args : str
            strings with the statements. E.g. ``"column > 351"``
        kwargs
            if a column shall have exactly a value

        Returns
        -------
        str
            query able to execute

        """
        # collecting all where statements
        where_statements = list()

        # casting all equal statements
        for kw in kwargs:
            where_statements.append(f"`{kw}` = {kwargs[kw]}")

        # casting all other statements
        for arg in args:
            elements = arg.split(" ")

            # word based statement (like `"123" in column_name`)
            if len(elements) > 2 and not any(i in arg for i in "<>=!"):
                column = elements[-1]

                if column not in self.schema.keys():
                    raise ValueError(f"column {column} not in table")

                value = elements[0]
                commands = elements[1:-1]
                if "not" in commands:
                    boolean = False
                else:
                    boolean = True

                where_statements.append(self._query_contains(column, value, boolean))   # db specific -> must be defined in inherited class

            # special character based statement (like `column_name > 123`)
            else:
                # either special character or word based statements allowed
                if " not " in arg or " in " in arg:
                    raise ValueError("please only use words like `in`, & `not` or the command_characters {<, >, !, =}")

                # craft column name and value separated by operators
                column, value = [e for e in re.split(r"[><=! ]", arg) if e]

                if column not in self.schema.keys():
                    raise ValueError(f"column {column} not in table")

                # negation check
                if "<>" in arg or "!" in arg:
                    boolean = False
                else:
                    boolean = True

                # Null statements
                if value.lower() == "null" or value == None:
                    where_statements.append(self._query_null(column, boolean))  # db specific -> must be defined in inherited class

                # other statements
                else:
                    arg = arg.replace(column, "").replace(value, "")
                    if "=" in arg:
                        command = "=" if boolean else self._query_unequals  # db specific -> must be defined in inherited class
                    elif ">" in arg:
                        command = ">"
                    elif "<" in arg:
                        command = "<"
                    else:
                        raise ValueError("please use only these command characters: {<, >, !, =}")

                    where_statements.append(f"`{column}` {command} {value}")

        where_statement = " AND ".join(where_statements)

        query = f"SELECT {self.__columns_string()} FROM {self._table} WHERE " + where_statement
        logging.info(f"composed query: {query}")
        return query

    def _execute_query(self, query):
        self._db._cursor.execute(query)
        rows = list()
        for row in self._db._cursor:
            rows.append(row)
        return rows

    def __columns_string(self, desired_columns=False):
        # if no columns specified
        if not self.working_columns and not desired_columns:
            return "*"

        if not set(self.working_columns).issubset(set(self.schema.keys())):
            raise ValueError("not all specified columns are in table")

        if self.working_columns:
            desired_columns = self.working_columns

        columns_string = f"""{str([i for i in desired_columns]).replace("', '", ", ")[2:-2]}"""

        return columns_string

    def __get_column_for_request(self):
        return next(self.__column_for_request)

    def __set_column_for_request(self, column):
        if not isinstance(column, str):
            raise ValueError("column not type str")
        self.__column_for_request = iter([column])

    _column_for_request = property(__get_column_for_request, __set_column_for_request)

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
            self._db._cursor.execute(self._schema_update_query)
            for row in self._db._cursor:
                # ToDo check for more available data via SQL/maybe putting to db specific subclass
                self.__schema[row[0]] = {"type": row[1], "null": row[2], "key": row[3], "default": row[4],
                                         "extra": row[5]}
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

    def __getitem__(self, key):
        """
        Get rows where key matches the primary column

        works like ``database.table[key]``

        Parameters
        ----------
        key : any
            matching value in primary column

        Returns
        -------
        list
            tuple items representing every matched row in database

        """

        query = self._build_query(f"{self.primary}={key}")
        return self._execute_query(query)

    def get_where(self, *args, **kwargs):
        """
        Get rows where value matches the defined column: ``columns=key``

        Parameters
        ----------
        **kwargs
            column = key values

        Returns
        -------
        list
            tuple items representing every matched row in database

        """
        if len(kwargs) == 1 and not args:
            [self._column_for_request] = kwargs.keys()
            [value] = kwargs.values()
            return self.__getitem__(value)

        query = self._build_query(*args, **kwargs)
        return self._execute_query(query)

    def __setitem__(self, key, row):
        raise NotImplemented("coming soon")

    def set_where(self, row, **kwargs):
        raise NotImplemented("coming soon")

    def __delitem__(self, key):
        raise NotImplemented("coming soon")

    def delete_where(self, key, where):
        raise NotImplemented("coming soon")


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
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self.__tables = list()

        self._connect_to_db()  # function must be defined for every database representing subclass
        if auto_creation:
            self._constructor()
        atexit.register(self.close)

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
            raise EnvironmentError(f"builtin function of class matches table_name in database {self._database}\n"
                                   f"can't create all tables as attributes to database_object\n"
                                   f"please disable auto_creation or rename matching table '{doubles}' in database")
        hidden_values = {table_name for table_name in self.tables if "__" == table_name[0:2] }
        if any("__" == table_name[0:2] for table_name in self.tables):
            logging.warning(
                f"table_name in database {self._database} contains '__' in beginning -> not accessable with `Python` "
                f"please disable auto_creation or rename '{hidden_values}' in database"
            )

    def _constructor(self):
        self._check_auto_creation()
        for table_name in self.tables:
            setattr(self, table_name, Table(table_name, self))

    def close(self):
        """
        Close connection to database

        """
        self._cursor.close()
        self._conn.close()
        atexit.unregister(self.close)
