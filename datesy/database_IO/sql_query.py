_dual_value_commands = ["between", "not between"]
_string_commands = ["contains", "not contains", "not like", "like"]
_allowed_sql_query_commands = (
    ["not", "<>", "!=", "=", "<", ">", ">=", "<=", "is", "is not", "in", "not in"]
    + _dual_value_commands
    + _string_commands
)
_command_translations = {"contains": "like", "not contains": "not like", "!=": "<>"}


class SQLQueryConstructor:
    """
    A SQL query constructor class.
    Various different statements may be given without taking care of the order.
    Once fetched, all statements will be deleted and new basic query starts with ``SELECT * FROM table_name``.
    """

    def __init__(self, database_name, table_name, primary=str()):
        self._consistent = False  # for flagging inconsistent constructor
        self._database_name = database_name
        self._table_name = table_name
        self.name = self.__create_escaped_references(table_name, table=True)
        self._primary = primary

        self._affected_columns = list()  # all columns relevant for request

        self._delete = False
        self._length = False
        self._distinct = bool()

        self._updates = dict()
        self._joins = list()
        self._wheres = list()
        self._where_or = False

        self._affected_rows = int()  # limit of rows
        self._offset_affected_rows = int()
        self._order_by = (
            {self.__create_escaped_references(primary, column=True): "ASC"}
            if primary
            else dict()
        )  # columns to order by

    @property
    def columns(self):
        return self._affected_columns

    def __create_escaped_references(self, name, table=False, column=False):
        if isinstance(name, str):
            parts = name.split(".")
        elif isinstance(name, (list, tuple)):
            parts = name
        else:
            raise TypeError(
                "name must be either str of column or table or a list with all specified values"
            )

        length = len(parts)
        if table:
            if length == 1:
                return f"`{self._database_name}`.`{parts[0]}`"
            if length == 2:
                return f"`{parts[0]}`.`{parts[1]}`"
        elif column:
            if length == 1:
                return f"`{self._database_name}`.`{self._table_name}`.`{parts[0]}`"
            if length == 2:
                return f"`{self._database_name}`.`{parts[0]}`.`{parts[1]}`"
            if length == 3:
                return f"`{parts[0]}`.`{parts[1]}`.`{parts[2]}`"

    # ### Basic request type ###
    def delete_request(self):
        """
        Delete content in table (or truncate if no where statements available)
        """
        self._delete = True
        return self

    def length_request(self, distinct=False):
        """
        Return number of rows instead of row_content

        Parameters
        ----------
        distinct : bool, optional
            if set of entries is counted instead of every entry

        """
        self._length = True
        self._distinct = distinct
        return self

    # ### give data for query ###
    def add_desired_columns(self, *args):
        for column in args:
            self._affected_columns.append(
                self.__create_escaped_references(column, column=True)
            )
        return self

    def add_desired_foreign_columns(self, *args, table, database=None):
        """
        Add desired columns from other table or database

        Parameters
        ----------
        args : str
            columns
        table : str
            foreign table name
        database : str
            foreign database name

        """
        if database is None:
            database = self._database_name

        for column in args:
            reference = self.__create_escaped_references(
                (database, table, column), column=True
            )
            self._affected_columns.append(reference)
        return self

    def add_where_statements(
        self, *args, column=None, command=None, value=None, OR=False, **kwargs
    ):
        wheres = list()
        for key in kwargs:
            if isinstance(kwargs[key], str):
                kwargs[key] = f"'{kwargs[key]}'"
            statement = f"({self.__create_escaped_references(key, column=True)} = {kwargs[key]})"
            wheres.append(statement)

        statements = list()
        for arg in args:
            statements.append(arg)

        if column and command and value:
            statements.append((column, command, value))

        for statement in statements:
            if isinstance(statement, str):
                statement = statement.split(" ")
            else:
                statement = list(statement)
            if not isinstance(statement, (list, tuple)):
                raise TypeError(
                    "must be list or tuple, or string with spaces between column, command and value"
                )
            if len(statement) != 3:
                raise IndexError(
                    "each statement length must be 3: column, command, value"
                )

            # allowed statements
            if statement[1].lower() not in _allowed_sql_query_commands:
                raise ValueError(
                    f"unsupported argument {statement[1]}, only allowed: {_allowed_sql_query_commands}"
                )

            # set column reference with escape chars
            statement = [
                self.__create_escaped_references(statement[0], column=True)
            ] + statement[1:]

            # handling special commands
            if statement[1].lower() in _dual_value_commands:
                statement[2] = f"{statement[2][0]} AND {statement[2][1]}"
            if statement[1].lower() in _string_commands:
                statement[2] = f"'%{statement[2]}%'"

            # translating commands
            if statement[1] in _command_translations:
                statement[1] = _command_translations[statement[1]]

            if statement[2] is None:
                statement[2] = "NULL"

            wheres.append(f"({statement[0]} {statement[1]} {statement[2]})")

        if len(wheres) == 1 and self._where_or:
            last_where = self._wheres[-1]
            self._wheres[-1] = f"({last_where} OR {wheres[0]})"
            self._where_or = False

        elif OR and len(wheres) == 1:
            self._where_or = True
            self._wheres.append(wheres[0])

        elif OR and len(wheres) > 1:
            wheres = f"({' OR '.join(wheres)})"
            self._wheres.append(wheres)

        else:
            for where in wheres:
                self._wheres.append(where)
        return self

    def add_join(self, column_1, column_2, join_type="INNER"):
        """
        Add join of two tables

        Parameters
        ----------
        column_1 : str, tuple, list
            string of column of desired join or iterable of ``[database (optional), table, column]``
        column_2 : str, tuple, list
            string of column of desired join or iterable of ``[database (optional), table, column]``
        join_type : str, optional
            specify the join type (choices= inner, left, right, full, self)

        """
        if join_type.lower() not in ["inner", "left", "right", "full", "self"]:
            raise ValueError(f"unsupported join type {join_type}")

        if not all(isinstance(i, (str, list, tuple)) for i in [column_1, column_2]):
            raise TypeError(
                f"column_1 and column_2 must be both either string or iterable"
            )

        column_1 = self.__create_escaped_references(column_1, column=True)
        column_2 = self.__create_escaped_references(column_2, column=True)
        table_1 = ".".join(column_1.split(".")[:-1])
        table_2 = ".".join(column_2.split(".")[:-1])

        if table_1 == self.name:
            __join = f"{join_type} JOIN {table_2} ON {column_1}={column_2}"
        elif table_2 == self.name:
            __join = f"{join_type} JOIN {table_1} ON {column_2}={column_1}"
        else:
            for i in self._joins[::-1]:
                if table_1 in i:
                    __join = f"{join_type} JOIN {table_2} ON {column_1}={column_2}"
                    break
                elif table_2 in i:
                    __join = f"{join_type} JOIN {table_1} ON {column_2}={column_1}"
                    break

        try:
            self._joins.append(__join)
        except NameError:
            raise ValueError("cant join on any already existing tables of this query")
        return self

    def add_new_values(
        self, column=None, value=None, **kwargs
    ):  # column=value for each entry to set
        """
        Updates/inserts rows
        if where_statements present, update these rows. else insert new row

        Parameters
        ----------
        column : str, optional
            column name to set value to
        value : str, int, list, dict, set, tuple, bool, optional
            value to be set (bool will be interpreted as string ``'True'/'False'``)
        kwargs
            ``column = value``

        """
        if column:
            self._updates[self.__create_escaped_references(column, column=True)] = (
                value if not isinstance(value, bool) else {True: 1, False: 0}[value]
            )
        for key in kwargs.copy():
            kwargs[self.__create_escaped_references(key, column=True)] = (
                kwargs[key]
                if not isinstance(kwargs[key], bool)
                else {True: 1, False: 0}[value]
            )
            del kwargs[key]
        self._updates.update(kwargs)
        return self

    # ### organize operation ###
    def order(
        self, column, increasing=True, foreign_table=False, foreign_database=False
    ):
        """
        Order the result by column (and increasing or decreasing values)

        Parameters
        ----------
        column : str
            string representation of a column
        increasing : bool, optional
            if increasing or decreasing ordering
        foreign_table : str
            of the order shall base on a column from foreign table from a join

        """
        if not isinstance(column, str):
            raise TypeError(f"column to order by must be string, given: {type(column)}")
        if foreign_database and not foreign_table:
            raise ValueError(
                "if foreign database is given, the foreign table needs to be specified as well"
            )

        reference = [column]

        if foreign_table:
            reference.insert(0, foreign_table)
        if foreign_database:
            reference.insert(0, foreign_database)
        reference = self.__create_escaped_references(reference, column=True)

        if increasing:
            self._order_by[reference] = "ASC"
        else:
            self._order_by[reference] = "DESC"
        if self._primary and self._primary in self._order_by:
            del self._order_by[
                self.__create_escaped_references(self._primary, column=True)
            ]
        return self

    def limit(self, number_of_rows, offset=int()):
        """
        Limit the query to run only until ``number_of_rows`` affected (e.g. found or updated)

        Parameters
        ----------
        number_of_rows : int
            the number of rows to max. affect
        offset : int, optional
            number of rows to skip once starting the counter

        """
        if not isinstance(number_of_rows, int):
            TypeError(f"number of rows must be integer, given: {type(number_of_rows)}")
        self._affected_rows = number_of_rows
        self._offset_affected_rows = offset
        return self

    # ### calculate query ###
    def __str__(self):  # construct a query for execution
        if self._affected_columns:
            columns = f"{', '.join([i for i in self._affected_columns])}"
        else:
            columns = "*"

        if self._delete:
            if self._wheres:
                query = f"DELETE FROM {self.name}"
            else:
                query = f"TRUNCATE {self.name}"

        elif self._updates:
            if self._wheres:
                query = f"UPDATE {self.name}"
            else:
                update_items = tuple(self._updates.items())
                columns = ", ".join([i[0] for i in update_items])
                values = ", ".join(
                    [f"'{i[1]}'" for i in update_items if i[1] is not None]
                )
                query = f"INSERT INTO {self.name} ({columns}) VALUES ({values})"

        elif self._length:
            query = f"SELECT{' DISTINCT' if self._distinct else ''} COUNT({columns}) FROM {self.name}"
        else:
            query = f"SELECT {columns} FROM {self.name}"

        if self._joins:
            query += " " + " ".join(self._joins)

        if self._updates and self._wheres:
            set_value = ", ".join(
                [
                    f"{key} = '{value}'" if value is not None else f"{key} = NULL"
                    for key, value in self._updates.items()
                ]
            )
            query += f" SET {set_value}"

        if self._wheres:
            query += " WHERE " + " AND ".join(self._wheres)

        if (
            self._order_by
            and not self._updates
            and not self._delete
            and not self._length
        ):
            if self._affected_columns:
                for column in self._order_by.copy():
                    if column not in self._affected_columns:
                        del self._order_by[column]
            if self._order_by:
                orders = [f"{i} {self._order_by[i]}" for i in self._order_by]
                query += f" ORDER BY {', '.join(orders)}"

        if self._affected_rows:
            query += f" LIMIT {self._affected_rows}"
        if self._offset_affected_rows:
            query += f" OFFSET {self._offset_affected_rows}"

        if not self._consistent:
            self.__init__(
                self._database_name, self._table_name, self._primary
            )  # flush all entries
        return query + ";"
