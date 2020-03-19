from unittest import TestCase


class TestSQLQueryWhereStatements(TestCase):
    def setUp(self) -> None:
        from datesy.database_IO.sql_query import SQLQueryConstructor
        self.query = SQLQueryConstructor("database_test", "table_test", "primary_key_value")

    def test_add_where_statements_kwargs(self):
        self.query.add_where_statements(column="test_col", command="=", value="4")

        expected = "SELECT * FROM `database_test`.`table_test` WHERE (`database_test`.`table_test`.`test_col` = 4) " \
                   "ORDER BY `database_test`.`table_test`.`primary_key_value` ASC;"

        result = str(self.query)
        self.assertEqual(expected, result)

    def test_add_where_statements_arg_in_tuple(self):
        self.query.add_where_statements(("test_col", "=", "4"))

        expected = "SELECT * FROM `database_test`.`table_test` WHERE (`database_test`.`table_test`.`test_col` = 4) " \
                   "ORDER BY `database_test`.`table_test`.`primary_key_value` ASC;"

        result = str(self.query)
        self.assertEqual(expected, result)

    def test_add_where_statements_arg_as_str(self):
        self.query.add_where_statements("test_col = 4")

        expected = "SELECT * FROM `database_test`.`table_test` WHERE (`database_test`.`table_test`.`test_col` = 4) " \
                   "ORDER BY `database_test`.`table_test`.`primary_key_value` ASC;"

        result = str(self.query)
        self.assertEqual(expected, result)

    def test_add_where_statements_args_tuple_and_str(self):
        self.query.add_where_statements(("test_col", ">=", "4"), "identifier contains 1")

        expected = "SELECT * FROM `database_test`.`table_test` WHERE (`database_test`.`table_test`.`test_col` >= 4) AND " \
                   "(`database_test`.`table_test`.`identifier` like '%1%') " \
                   "ORDER BY `database_test`.`table_test`.`primary_key_value` ASC;"

        result = str(self.query)
        self.assertEqual(expected, result)

    def test_add_where_statements_args_multi_tuple(self):
        self.query.add_where_statements(("test_col", ">=", "4"), ("test_col2", "=", "3"))

        expected = "SELECT * FROM `database_test`.`table_test` WHERE (`database_test`.`table_test`.`test_col` >= 4) AND " \
                   "(`database_test`.`table_test`.`test_col2` = 3) " \
                   "ORDER BY `database_test`.`table_test`.`primary_key_value` ASC;"

        result = str(self.query)
        self.assertEqual(expected, result)
