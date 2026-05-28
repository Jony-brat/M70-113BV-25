import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    RecordNotFoundError,
    MissingColumnError,
    UnknownColumnError,
)


class TestMemoryDatabase(unittest.TestCase):
    
    def setUp(self):
        self.db = MemoryDatabase()
        self.columns = ('first_name', 'last_name', 'age', 'grade', 'email')
        self.db.create_table("students", self.columns, indexed_fields=['email'])
    
    def tearDown(self):
        self.db = None
    

    def test_create_table_success(self):
        self.db.create_table("new_table", ('name', 'value'))
        self.assertTrue(self.db._table_exists("new_table"))
    
    def test_create_table_already_exists(self):
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", self.columns)
    

    def test_insert_record_success(self):
        record = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'age': 20,
            'grade': 4.7,
            'email': 'ivan@example.com'
        }
        record_id = self.db.insert_record("students", record)
        self.assertEqual(record_id, 1)
        self.assertEqual(self.db.count_records("students"), 1)
    
    def test_insert_record_missing_column(self):
        record = {'first_name': 'Иван', 'last_name': 'Петров'}
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("students", record)
    
    def test_insert_record_extra_column(self):
        record = {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com',
            'extra': 'value'
        }
        with self.assertRaises(UnknownColumnError):
            self.db.insert_record("students", record)
    
    def test_insert_record_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record("unknown", {'name': 'test'})
    

    def test_select_records_no_filters(self):
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        self.db.insert_record("students", {
            'first_name': 'Мария', 'last_name': 'Иванова',
            'age': 22, 'grade': 4.2, 'email': 'maria@example.com'
        })
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 2)
    
    def test_select_records_with_filter(self):
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        records = self.db.select_records("students", first_name='Иван')
        self.assertEqual(len(records), 1)
    
    def test_select_records_with_unknown_filter(self):
        with self.assertRaises(UnknownColumnError):
            self.db.select_records("students", unknown_field='value')
    
    def test_select_records_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("unknown")
    

    def test_update_record_success(self):
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        updated = self.db.update_record("students", record_id, first_name='Пётр', age=21)
        self.assertEqual(updated['first_name'], 'Пётр')
        self.assertEqual(updated['age'], 21)
    
    def test_update_record_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.db.update_record("students", 999, first_name='Пётр')
    
    def test_update_record_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.update_record("unknown", 1, name='test')
    
    def test_update_record_unknown_field(self):
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        with self.assertRaises(UnknownColumnError):
            self.db.update_record("students", record_id, unknown_field='value')

    def test_delete_record_success(self):
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        deleted = self.db.delete_record("students", record_id)
        self.assertEqual(deleted['first_name'], 'Иван')
        self.assertEqual(self.db.count_records("students"), 0)
    
    def test_delete_record_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.db.delete_record("students", 999)
    
    def test_delete_record_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.delete_record("unknown", 1)
    
    def test_get_all_records(self):
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        records = self.db.get_all_records("students")
        self.assertEqual(len(records), 1)
    
    def test_get_all_records_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_all_records("unknown")
    

    def test_count_records(self):
        self.assertEqual(self.db.count_records("students"), 0)
        
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        self.assertEqual(self.db.count_records("students"), 1)
    
    def test_count_records_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.count_records("unknown")
    

    def test_sort_records_by_id(self):
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        self.db.insert_record("students", {
            'first_name': 'Анна', 'last_name': 'Иванова',
            'age': 22, 'grade': 4.2, 'email': 'anna@example.com'
        })
        
        sorted_records = self.db.sort_records("students", 'first_name')
        self.assertEqual(sorted_records[0]['first_name'], 'Анна')
    
    def test_sort_records_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.sort_records("unknown", 'name')
    

    def test_add_index(self):
        self.db.add_index("students", 'age')
        indexes = self.db.get_indexed_fields("students")
        self.assertIn('age', indexes)
    
    def test_remove_index(self):
        self.db.remove_index("students", 'email')
        indexes = self.db.get_indexed_fields("students")
        self.assertNotIn('email', indexes)
    
    def test_get_indexed_fields(self):
        indexes = self.db.get_indexed_fields("students")
        self.assertIn('email', indexes)
    
    def test_add_index_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.add_index("unknown", 'field')
    
    def test_remove_index_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.remove_index("unknown", 'field')

    def test_table_exists_true(self):
        self.assertTrue(self.db._table_exists("students"))
    
    def test_table_exists_false(self):
        self.assertFalse(self.db._table_exists("unknown"))

    def test_load_table_success(self):
        table = self.db._load_table("students")
        self.assertIsNotNone(table)
    
    def test_load_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db._load_table("unknown")
    

    def test_save_table(self):
        table = self.db._load_table("students")
        self.db._save_table("students", table)
        self.assertTrue(self.db._table_exists("students"))


if __name__ == "__main__":
    unittest.main()