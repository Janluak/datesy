import unittest
import datetime
from collections import OrderedDict


class TestStandardMYSQL(unittest.TestCase):
    def setUp(self) -> None:
        # import logging
        # logging.getLogger().setLevel(logging.INFO)
        from datesy.database_IO import MySQL
        self.db = MySQL("localhost", "datesy_user", "test_pw", "datesydb", auto_creation=True)
        self.table = self.db.table("test_table")

    def test_all_tables(self):
        self.assertEqual(["test_table"], ["test_table"])
        self.assertEqual("test_table", self.db.test_table.name)

    def test_schema(self):
        schema = OrderedDict(
            [('primary_column',
              {'default': None,
               'extra': 'auto_increment',
               'key': 'PRI',
               'null': 'NO',
               'type': 'int'}),
             ('value1',
              {'default': None,
               'extra': '',
               'key': '',
               'null': 'YES',
               'type': 'varchar(100)'}),
             ('timestamp',
              {'default': None,
               'extra': '',
               'key': '',
               'null': 'YES',
               'type': 'datetime'})])

        self.assertEqual(schema, self.table.schema)
        self.assertEqual(schema.keys(), self.table.schema.keys())

    def test_primary(self):
        self.assertEqual("primary_column", self.table.primary)

    def test_insert_with_list(self):
        self.table[1] = ["value_row_1", "2020-01-01 02:40:01"]
        self.assertEqual(str((1, 'value_row_1', datetime.datetime(2020, 1, 1, 2, 40, 1))), str(self.table[1]))
        del self.table[1]

    def test_insert_with_dict(self):
        self.table[1] = {"value1": "value_row_1", "timestamp": "2020-01-01 02:40:01"}

        self.assertEqual(str((1, 'value_row_1', datetime.datetime(2020, 1, 1, 2, 40, 1))), str(self.table[1]))
        del self.table[1]

    def test_update(self):
        self.table[1] = ["value_row_1", "2020-01-01 02:40:01"]
        self.table[1] = ["value_row_1_new", "2020-01-01 02:40:02"]

        self.assertEqual(str((1, 'value_row_1_new', datetime.datetime(2020, 1, 1, 2, 40, 2))), str(self.table[1]))
        del self.table[1]

    def test_get_where(self):
        expected = ["(1, 'value_row_1', datetime.datetime(2020, 1, 1, 2, 40, 1))",
                    "(2, 'value_row_2', datetime.datetime(2020, 2, 2, 4, 44, 4))"]

        self.table[1] = ["value_row_1", "2020-01-01 02:40:01"]
        self.table[2] = ["value_row_2", "2020-02-02 04:44:04"]

        result = self.table.get_where(("primary_column", ">", 0))
        self.assertEqual(len(expected), len(result))
        for i in range(len(expected)):
            self.assertEqual(expected[i], str(result[i]))

    def test_update_where_explicit(self):
        expected = str((1, "value_row_1", datetime.datetime(2020, 1, 1, 2, 40, 1)))

        self.table[1] = {"value1": "value_row_1"}
        self.table.update_where([1, "value_row_1", "2020-01-01 02:40:01"], ("primary_column", ">", 0))

        self.assertEqual(expected, str(self.table[1]))

    def test_update_where_explicit2(self):
        expected = ["(1, 'new_value', datetime.datetime(2020, 1, 1, 2, 40, 1))",
                    "(2, 'new_value', datetime.datetime(2020, 2, 2, 4, 44, 4))"]

        self.table[1] = ["value_row_1", "2020-01-01 02:40:01"]
        self.table[2] = ["value_row_2", "2020-02-02 04:44:04"]

        self.table.update_where({"value1": "new_value"}, ("primary_column", ">", 0))

        result = self.table.get_where(("primary_column", ">", 0))
        self.assertEqual(len(expected), len(result))
        for i in range(len(expected)):
            self.assertEqual(expected[i], str(result[i]))

    def test_delete_where(self):
        expected = ["(1, 'value_row_1', datetime.datetime(2020, 1, 1, 2, 40, 1))",
                    "(2, 'value_row_2', datetime.datetime(2020, 2, 2, 4, 44, 4))"]

        self.table[1] = ["value_row_1", "2020-01-01 02:40:01"]
        self.table[2] = ["value_row_2", "2020-02-02 04:44:04"]
        self.table[3] = ["value_row_3", "2020-01-01 03:40:01"]
        self.table[4] = ["value_row_4", "2020-01-01 04:40:01"]

        result = self.table.get_where(("primary_column", ">", 0))
        expected_between = expected.copy()
        expected_between.append("(3, 'value_row_3', datetime.datetime(2020, 1, 1, 3, 40, 1))")
        expected_between.append("(4, 'value_row_4', datetime.datetime(2020, 1, 1, 4, 40, 1))")
        self.assertEqual(len(expected_between), len(result))
        for i in range(len(expected)):
            self.assertEqual(expected_between[i], str(result[i]))

        self.table.delete_where(("primary_column", ">", 2))

        result = self.table.get_where(("primary_column", ">", 0))
        self.assertEqual(len(expected), len(result))
        for i in range(len(expected)):
            self.assertEqual(expected[i], str(result[i]))

    def tearDown(self) -> None:
        self.table.truncate()


class TestContextMYSQL(unittest.TestCase):
    def test_context(self):
        from datesy.database_IO import MySQL
        dbs = TestStandardMYSQL()
        with MySQL("localhost", "datesy_user", "test_pw", "datesydb", auto_creation=False) as db:
            dbs.table = db.table("test_table")

            dbs.test_insert_with_list()
            dbs.table.truncate()

            dbs.test_insert_with_dict()
            dbs.table.truncate()

            dbs.test_update()
            dbs.table.truncate()

            dbs.test_get_where()
            dbs.table.truncate()

            dbs.test_update_where_explicit()
            dbs.table.truncate()

            dbs.test_update_where_explicit2()
            dbs.table.truncate()

            dbs.test_delete_where()
            dbs.table.truncate()


if __name__ == '__main__':
    unittest.main()
