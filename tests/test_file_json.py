import unittest
import tempfile
import json
from pathlib import Path
from src.db.backend.file_json import JSONDatabase
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    InvalidStorageDataError,
)


class TestJSONDatabase(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = JSONDatabase(self.temp_dir.name)
        self.columns = ('first_name', 'last_name', 'age', 'grade', 'email')
        self.db.create_table("students", self.columns, indexed_fields=['email'])
    
    def tearDown(self):
        self.temp_dir.cleanup()
    

    def test_create_table_creates_file(self):
        table_path = Path(self.temp_dir.name) / "new_table.json"
        self.assertFalse(table_path.exists())
        
        self.db.create_table("new_table", ('name', 'value'))
        self.assertTrue(table_path.exists())
    
    def test_create_table_already_exists(self):
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", self.columns)

    def test_insert_record_saves_to_file(self):
        record = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'age': 20,
            'grade': 4.7,
            'email': 'ivan@example.com'
        }
        record_id = self.db.insert_record("students", record)
        

        table_path = Path(self.temp_dir.name) / "students.json"
        with open(table_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(len(data['records']), 1)
        self.assertEqual(data['records'][0]['first_name'], 'Иван')
    

    def test_data_persists_between_instances(self):

        record = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'age': 20,
            'grade': 4.7,
            'email': 'ivan@example.com'
        }
        self.db.insert_record("students", record)

        new_db = JSONDatabase(self.temp_dir.name)
        records = new_db.select_records("students")
        
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['first_name'], 'Иван')
    
    def test_data_persists_after_reload(self):
        record = {
            'first_name': 'Мария',
            'last_name': 'Иванова',
            'age': 22,
            'grade': 4.2,
            'email': 'maria@example.com'
        }
        self.db.insert_record("students", record)
        

        self.db = JSONDatabase(self.temp_dir.name)
        records = self.db.select_records("students")
        
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['first_name'], 'Мария')
    

    def test_select_records_with_filters(self):
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        self.db.insert_record("students", {
            'first_name': 'Мария', 'last_name': 'Иванова',
            'age': 22, 'grade': 4.2, 'email': 'maria@example.com'
        })
        
        records = self.db.select_records("students", last_name='Петров')
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['first_name'], 'Иван')
    

    def test_update_record_saves_to_file(self):
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        self.db.update_record("students", record_id, first_name='Пётр')
        

        new_db = JSONDatabase(self.temp_dir.name)
        records = new_db.select_records("students")
        self.assertEqual(records[0]['first_name'], 'Пётр')
    

    def test_delete_record_removes_from_file(self):
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        self.db.delete_record("students", record_id)
        
        new_db = JSONDatabase(self.temp_dir.name)
        records = new_db.select_records("students")
        self.assertEqual(len(records), 0)
    
    def test_load_corrupted_json(self):

        table_path = Path(self.temp_dir.name) / "corrupted.json"
        with open(table_path, 'w', encoding='utf-8') as f:
            f.write("{invalid json")
        

        class CorruptedJSONDatabase(JSONDatabase):
            def _table_exists(self, table_name):
                return table_name == "corrupted"
        
        db = CorruptedJSONDatabase(self.temp_dir.name)
        with self.assertRaises(InvalidStorageDataError):
            db._load_table("corrupted")
    
    def test_load_nonexistent_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")
    

    def test_indexes_persist(self):

        self.db.add_index("students", 'age')

        new_db = JSONDatabase(self.temp_dir.name)
        indexes = new_db.get_indexed_fields("students")
        
        self.assertIn('age', indexes)
    

    def test_multiple_operations_sequence(self):

        ids = []
        for i, name in enumerate(['Иван', 'Мария', 'Петр']):
            record_id = self.db.insert_record("students", {
                'first_name': name,
                'last_name': f'{name}ов',
                'age': 20 + i,
                'grade': 4.0 + i * 0.3,
                'email': f'{name.lower()}@example.com'
            })
            ids.append(record_id)
        
        self.db.update_record("students", ids[1], grade=5.0)

        self.db.delete_record("students", ids[0])
        

        records = self.db.select_records("students")
        self.assertEqual(len(records), 2)

        new_db = JSONDatabase(self.temp_dir.name)
        records = new_db.select_records("students")
        self.assertEqual(len(records), 2)
    

    def test_sort_records(self):
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
    

    def test_get_all_records(self):
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        records = self.db.get_all_records("students")
        self.assertEqual(len(records), 1)
    

    def test_count_records(self):
        self.assertEqual(self.db.count_records("students"), 0)
        
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        self.assertEqual(self.db.count_records("students"), 1)
    

    def test_table_exists(self):
        self.assertTrue(self.db._table_exists("students"))
        self.assertFalse(self.db._table_exists("nonexistent"))
    

    def test_get_table_path(self):
        path = self.db._get_table_path("test")
        self.assertEqual(path.name, "test.json")
        self.assertEqual(str(path.parent), self.temp_dir.name)


if __name__ == "__main__":
    unittest.main()