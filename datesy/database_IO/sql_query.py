_dual_value_commands = ["between", "not between"]
_revert_commands = ["in", "not in"]
_string_commands = ["contains", "not contains", "not like", "like"] + _revert_commands
_allowed_sql_query_commands = (
    ["not", "<>", "!=", "=", "<", ">", ">=", "<=", "is", "is not"]
    + _dual_value_commands
    + _string_commands
)
_command_translations = {
    "contains": "like",
    "not contains": "not like",
    "!=": "<>",
    "in": "like",
    "not in": "not like",
}


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
        self.name = f"`{database_name}`.`{table_name}`"
        self._primary = primary

        self._affected_columns = list()  # all columns relevant for request

        self._delete = False
        self._length = False
        self._distinct = bool()

        self._updates = dict()
        self._joins = list()
        self._wheres = list()

        self._affected_rows = int()  # limit of rows
        self._offset_affected_rows = int()
        self._order_by = {primary: "ASC"} if primary else dict()  # columns to order by

    @property
    def columns(self):
        return self._affected_columns

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
            self._affected_columns.append(f"{self._table_name}.{column}")
        return self

    def add_desired_columns_of_foreign_table(self, **kwargs):
        """
        Add desired columns from other table

        Parameters
        ----------
        kwargs
            key: table
            value: column

        """
        for table in kwargs:
            self._affected_columns.append(f"{table}.{kwargs[table]}")
            return self

    def add_where_statements(
        self, args=tuple(tuple()), *, column=None, command=None, value=None, **kwargs
    ):  # ToDo catch OR
        for key in kwargs:
            statement = f"({key} = {kwargs[key]})"
            self._wheres.append(statement)
            # print(self._wheres)
            # self._wheres.append(statement)

        if args:
            if isinstance(args, str):
                args = [args]
            elif isinstance(args[0], tuple):
                args = list(args)
            else:
                args = [args]
        if column and command and value:
            args.append((column, command, value))

        for statement in args:
            if isinstance(statement, str):
                statement = statement.split(" ")
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

            # handling special commands
            if statement[1].lower() in _dual_value_commands:
                statement[2] = f"{statement[2][0]} AND {statement[2][1]}"
            if statement[1].lower() in _string_commands:
                statement[2] = f"'%{statement[2]}%'"
            if statement[1].lower() in _revert_commands:
                statement = statement[::-1]

            # translating commands
            if statement[1] in _command_translations:
                statement[1] = _command_translations[statement[1]]

            if statement[2] is None:
                statement[2] = "NULL"

            self._wheres.append(f"(`{statement[0]}` {statement[1]} {statement[2]})")
        return self

    def add_join(
        self, table_1, column_1, table_2, column_2, join_type="INNER", **further_columns
    ):
        """
        Add join of two tables

        Parameters
        ----------
        table_1
        column_1
        table_2
        column_2
        further_columns
        join_type : str, optional
            specify the join type (choices= inner, left, right, full, self)

        """
        if join_type.lower() not in ["inner", "left", "right", "full", "self"]:
            raise ValueError(f"unsupported join type {join_type}")
        join = f"{join_type} JOIN {column_2} ON {table_1}.{column_1} = {table_2}.{column_2}"
        if further_columns:
            raise NotImplemented
            # ToDo improve handling of joins
        self._joins.append(join)
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
        value : str, int, list, dict, set, tuple, optional
            value to be set (bool will be interpreted as string?) # ToDo databases have boolean? how to set?
        kwargs
            ``column = value``

        """
        if column:
            self._updates[column] = value
        self._updates.update(kwargs)
        return self

    # ### organize operation ###
    def order(self, column, increasing=True, foreign_table=False):
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
            TypeError(f"column to order by must be string, given: {type(column)}")

        if foreign_table:
            table = foreign_table
        else:
            table = self._table_name

        if increasing:
            self._order_by[f"{table}.{column}"] = "ASC"
        else:
            self._order_by[f"{table}.{column}"] = "DESC"
        if self._primary and self._primary in self._order_by:
            del self._order_by[f"{table}.{self._primary}"]
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
    def __repr__(self):  # construct a query for execution
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
                set_value = ", ".join(
                    [
                        f"{key} = '{value}'" if value is not None else f"{key} = NULL"
                        for key, value in self._updates.items()
                    ]
                )
                query = f"UPDATE {self.name} SET {set_value}"
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

    # for debugging
    # def __str__(self):
    #     return str(self.__dict__)
