import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
)


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()
        self.db.create_table("students", ("id", "name", "age"))

    def tearDown(self):
        self.db.clear_all()

    def test_create_table_success(self):
        self.db.create_table("teachers", ("id", "name"))
        self.assertTrue(self.db.table_exists("teachers"))

    def test_create_table_already_exists(self):
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", ("id", "name"))

    def test_table_exists_true(self):
        self.assertTrue(self.db.table_exists("students"))

    def test_table_exists_false(self):
        self.assertFalse(self.db.table_exists("nonexistent"))

    def test_insert_record_success(self):
        record = {"id": 1, "name": "Ivan", "age": 20}
        self.db.insert_record("students", record)
        records = self.db.get_all_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Ivan")

    def test_insert_record_multiple(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Maria", "age": 22})
        self.assertEqual(self.db.count_records("students"), 2)

    def test_insert_record_missing_column(self):
        record = {"id": 1, "name": "Ivan"}
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("students", record)

    def test_insert_record_extra_column(self):
        record = {"id": 1, "name": "Ivan", "age": 20, "extra": "bad"}
        with self.assertRaises(UnknownColumnError):
            self.db.insert_record("students", record)

    def test_insert_record_to_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record("nonexistent", {"id": 1, "name": "Ivan", "age": 20})

    def test_select_records_no_filters(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Maria", "age": 22})
        records = self.db.select_records("students")
        self.assertEqual(len(records), 2)

    def test_select_records_with_filter(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Maria", "age": 22})
        records = self.db.select_records("students", age=20)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Ivan")

    def test_select_records_multiple_filters(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Ivan", "age": 22})
        records = self.db.select_records("students", name="Ivan", age=20)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], 1)

    def test_select_records_no_match(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        records = self.db.select_records("students", age=99)
        self.assertEqual(len(records), 0)

    def test_select_records_unknown_filter(self):
        with self.assertRaises(UnknownColumnError):
            self.db.select_records("students", unknown="value")

    def test_select_records_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")

    def test_update_record_success(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        updated = self.db.update_record("students", 1, "id", name="Petr", age=21)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Petr")
        self.assertEqual(updated["age"], 21)

    def test_update_record_partial(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        updated = self.db.update_record("students", 1, "id", age=25)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Ivan")
        self.assertEqual(updated["age"], 25)

    def test_update_record_not_found(self):
        result = self.db.update_record("students", 999, "id", name="Petr")
        self.assertIsNone(result)

    def test_update_record_unknown_field(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        with self.assertRaises(UnknownColumnError):
            self.db.update_record("students", 1, "id", unknown="value")

    def test_update_record_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.update_record("nonexistent", 1, "id", name="Petr")

    def test_delete_record_success(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Maria", "age": 22})
        deleted = self.db.delete_record("students", 1, "id")
        self.assertIsNotNone(deleted)
        self.assertEqual(deleted["name"], "Ivan")
        self.assertEqual(self.db.count_records("students"), 1)

    def test_delete_record_not_found(self):
        result = self.db.delete_record("students", 999, "id")
        self.assertIsNone(result)

    def test_delete_record_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.delete_record("nonexistent", 1, "id")

    def test_get_all_records(self):
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("students", {"id": 2, "name": "Maria", "age": 22})
        records = self.db.get_all_records("students")
        self.assertEqual(len(records), 2)

    def test_get_all_records_empty(self):
        records = self.db.get_all_records("students")
        self.assertEqual(len(records), 0)

    def test_get_all_records_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_all_records("nonexistent")

    def test_count_records(self):
        self.assertEqual(self.db.count_records("students"), 0)
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.assertEqual(self.db.count_records("students"), 1)

    def test_count_records_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.count_records("nonexistent")

    def test_clear_all(self):
        self.db.create_table("teachers", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("teachers", {"id": 1, "name": "Smith"})
        self.db.clear_all()
        self.assertFalse(self.db.table_exists("students"))
        self.assertFalse(self.db.table_exists("teachers"))

    def test_multiple_tables_isolation(self):
        self.db.create_table("teachers", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})
        self.db.insert_record("teachers", {"id": 1, "name": "Smith"})
        students = self.db.get_all_records("students")
        teachers = self.db.get_all_records("teachers")
        self.assertEqual(len(students), 1)
        self.assertEqual(len(teachers), 1)
        self.assertEqual(students[0]["name"], "Ivan")
        self.assertEqual(teachers[0]["name"], "Smith")


if __name__ == "__main__":
    unittest.main()