import unittest
from src.db.backend.table import Table
from src.db.backend.errors import MissingColumnError, UnknownColumnError


class TestTable(unittest.TestCase):
    def setUp(self):
        self.columns = ("id", "name", "age")
        self.table = Table(self.columns)

    def tearDown(self):
        self.table.clear()

    def test_initialization_empty(self):
        table = Table(("col1", "col2"))
        self.assertEqual(table.columns, ("col1", "col2"))
        self.assertEqual(len(table.records), 0)

    def test_initialization_with_records(self):
        records = [
            {"id": 1, "name": "Ivan", "age": 20},
            {"id": 2, "name": "Maria", "age": 22},
        ]
        table = Table(("id", "name", "age"), records)
        self.assertEqual(len(table.records), 2)
        self.assertEqual(table.records[0]["name"], "Ivan")
        self.assertEqual(table.records[1]["name"], "Maria")

    def test_initialization_with_invalid_record_missing_column(self):
        records = [{"id": 1, "name": "Ivan"}]
        with self.assertRaises(MissingColumnError):
            Table(("id", "name", "age"), records)

    def test_initialization_with_invalid_record_extra_column(self):
        records = [{"id": 1, "name": "Ivan", "age": 20, "extra": "bad"}]
        with self.assertRaises(UnknownColumnError):
            Table(("id", "name", "age"), records)

    def test_insert_record_success(self):
        record = {"id": 1, "name": "Ivan", "age": 20}
        self.table.insert_record(record)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0]["name"], "Ivan")
        self.assertEqual(self.table.records[0]["age"], 20)

    def test_insert_record_missing_column(self):
        record = {"id": 1, "name": "Ivan"}
        with self.assertRaises(MissingColumnError):
            self.table.insert_record(record)

    def test_insert_record_extra_column(self):
        record = {"id": 1, "name": "Ivan", "age": 20, "extra": "bad"}
        with self.assertRaises(UnknownColumnError):
            self.table.insert_record(record)

    def test_insert_record_preserves_original(self):
        record = {"id": 1, "name": "Ivan", "age": 20}
        self.table.insert_record(record)
        record["name"] = "Changed"
        self.assertEqual(self.table.records[0]["name"], "Ivan")

    def test_select_records_no_filters(self):
        records = [
            {"id": 1, "name": "Ivan", "age": 20},
            {"id": 2, "name": "Maria", "age": 22},
        ]
        for r in records:
            self.table.insert_record(r)
        result = self.table.select_records()
        self.assertEqual(len(result), 2)
        self.assertIsNot(result, self.table.records)

    def test_select_records_with_single_filter(self):
        records = [
            {"id": 1, "name": "Ivan", "age": 20},
            {"id": 2, "name": "Maria", "age": 22},
            {"id": 3, "name": "Petr", "age": 20},
        ]
        for r in records:
            self.table.insert_record(r)
        result = self.table.select_records(age=20)
        self.assertEqual(len(result), 2)

    def test_select_records_multiple_filters(self):
        records = [
            {"id": 1, "name": "Ivan", "age": 20},
            {"id": 2, "name": "Maria", "age": 22},
            {"id": 3, "name": "Petr", "age": 20},
        ]
        for r in records:
            self.table.insert_record(r)
        result = self.table.select_records(age=20, name="Ivan")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)

    def test_select_records_no_match(self):
        records = [
            {"id": 1, "name": "Ivan", "age": 20},
            {"id": 2, "name": "Maria", "age": 22},
        ]
        for r in records:
            self.table.insert_record(r)
        result = self.table.select_records(age=99)
        self.assertEqual(len(result), 0)

    def test_select_records_unknown_filter(self):
        with self.assertRaises(UnknownColumnError):
            self.table.select_records(unknown="value")

    def test_select_records_returns_copy(self):
        record = {"id": 1, "name": "Ivan", "age": 20}
        self.table.insert_record(record)
        result = self.table.select_records()
        result[0]["name"] = "Changed"
        self.assertEqual(self.table.records[0]["name"], "Ivan")

    def test_update_record_success(self):
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        updated = self.table.update_record(1, "id", name="Petr", age=21)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Petr")
        self.assertEqual(updated["age"], 21)
        self.assertEqual(self.table.records[0]["name"], "Petr")

    def test_update_record_partial_update(self):
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        updated = self.table.update_record(1, "id", age=25)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Ivan")
        self.assertEqual(updated["age"], 25)

    def test_update_record_not_found(self):
        result = self.table.update_record(999, "id", name="Petr")
        self.assertIsNone(result)

    def test_update_record_unknown_field(self):
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        with self.assertRaises(UnknownColumnError):
            self.table.update_record(1, "id", unknown="value")

    def test_update_record_invalid_id_field(self):
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        with self.assertRaises(UnknownColumnError):
            self.table.update_record(1, "invalid_field", name="Petr")

    def test_update_record_with_none_value(self):
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        updated = self.table.update_record(1, "id", name=None)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], None)

    def test_delete_record_success(self):
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        self.table.insert_record({"id": 2, "name": "Maria", "age": 22})
        deleted = self.table.delete_record(1, "id")
        self.assertIsNotNone(deleted)
        self.assertEqual(deleted["name"], "Ivan")
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0]["name"], "Maria")

    def test_delete_record_not_found(self):
        result = self.table.delete_record(999, "id")
        self.assertIsNone(result)

    def test_delete_record_invalid_id_field(self):
        with self.assertRaises(UnknownColumnError):
            self.table.delete_record(1, "invalid_field")

    def test_get_all_records(self):
        records = [
            {"id": 1, "name": "Ivan", "age": 20},
            {"id": 2, "name": "Maria", "age": 22},
        ]
        for r in records:
            self.table.insert_record(r)
        result = self.table.get_all_records()
        self.assertEqual(len(result), 2)
        self.assertIsNot(result, self.table.records)

    def test_get_all_records_empty(self):
        result = self.table.get_all_records()
        self.assertEqual(len(result), 0)

    def test_count_records(self):
        self.assertEqual(self.table.count_records(), 0)
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        self.assertEqual(self.table.count_records(), 1)
        self.table.insert_record({"id": 2, "name": "Maria", "age": 22})
        self.assertEqual(self.table.count_records(), 2)

    def test_clear(self):
        self.table.insert_record({"id": 1, "name": "Ivan", "age": 20})
        self.table.insert_record({"id": 2, "name": "Maria", "age": 22})
        self.assertEqual(len(self.table.records), 2)
        self.table.clear()
        self.assertEqual(len(self.table.records), 0)


if __name__ == "__main__":
    unittest.main()