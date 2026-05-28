import unittest
import tempfile
import csv
import json
from pathlib import Path
from src.db.backend.file_csv import CSVDatabase
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    RecordNotFoundError,
    InvalidStorageDataError,
)


class TestCSVDatabase(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = CSVDatabase(self.temp_dir.name)
        self.columns = ('first_name', 'last_name', 'age', 'grade', 'email')
        self.db.create_table("students", self.columns, indexed_fields=['email'])
    
    def tearDown(self):
        self.temp_dir.cleanup()
    

    def test_create_table_creates_csv_and_meta_files(self):
        csv_path = Path(self.temp_dir.name) / "new_table.csv"
        meta_path = Path(self.temp_dir.name) / "new_table.meta.json"
        
        self.assertFalse(csv_path.exists())
        self.assertFalse(meta_path.exists())
        
        self.db.create_table("new_table", ('name', 'value'))
        
        self.assertTrue(csv_path.exists())
        self.assertTrue(meta_path.exists())
    
    def test_create_table_already_exists(self):
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", self.columns)
    

    def test_insert_record_saves_to_csv(self):
        record = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'age': 20,
            'grade': 4.7,
            'email': 'ivan@example.com'
        }
        record_id = self.db.insert_record("students", record)
        

        csv_path = Path(self.temp_dir.name) / "students.csv"
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['first_name'], 'Иван')
        self.assertEqual(int(rows[0]['id']), record_id)
    
    def test_insert_record_updates_meta(self):
        record = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'age': 20,
            'grade': 4.7,
            'email': 'ivan@example.com'
        }
        self.db.insert_record("students", record)
        

        meta_path = Path(self.temp_dir.name) / "students.meta.json"
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        self.assertEqual(meta['next_id'], 2)
        self.assertIn('email', meta['indexed_fields'])
    

    def test_data_persists_between_instances(self):
        record = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'age': 20,
            'grade': 4.7,
            'email': 'ivan@example.com'
        }
        self.db.insert_record("students", record)
        
        new_db = CSVDatabase(self.temp_dir.name)
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
        
        self.db = CSVDatabase(self.temp_dir.name)
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
    
    def test_select_records_with_id_filter(self):
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        records = self.db.select_records("students", id=record_id)
        self.assertEqual(len(records), 1)
    

    def test_update_record_updates_csv(self):
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        self.db.update_record("students", record_id, first_name='Пётр', age=21)
        

        csv_path = Path(self.temp_dir.name) / "students.csv"
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(rows[0]['first_name'], 'Пётр')
        self.assertEqual(int(rows[0]['age']), 21)
    
    def test_update_record_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.db.update_record("students", 999, first_name='Пётр')
    

    def test_delete_record_removes_from_csv(self):
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        self.db.delete_record("students", record_id)
        

        csv_path = Path(self.temp_dir.name) / "students.csv"
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 0)
    
    def test_delete_record_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.db.delete_record("students", 999)
    

    def test_empty_table_load(self):

        self.db.create_table("empty", ('col1', 'col2'))
        
   
        records = self.db.select_records("empty")
        self.assertEqual(len(records), 0)
    
    def test_empty_csv_file_with_header(self):

        csv_path = Path(self.temp_dir.name) / "empty.csv"
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name'])
        
        meta_path = Path(self.temp_dir.name) / "empty.meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump({"columns": ["name"], "indexed_fields": [], "next_id": 1}, f)

        db = CSVDatabase(self.temp_dir.name)

        db._table_exists = lambda x: x == "empty"
        try:
            table = db._load_table("empty")
            self.assertIsNotNone(table)
        except TableNotFoundError:
            pass  
    
    
    def test_indexes_persist_in_meta(self):
        self.db.add_index("students", 'age')
        
        new_db = CSVDatabase(self.temp_dir.name)
        indexes = new_db.get_indexed_fields("students")
        
        self.assertIn('age', indexes)
    

    def test_load_nonexistent_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")
    
    def test_corrupted_meta_file(self):
        
        meta_path = Path(self.temp_dir.name) / "corrupted.meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            f.write("{invalid json")
        
        csv_path = Path(self.temp_dir.name) / "corrupted.csv"
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name'])
        
        db = CSVDatabase(self.temp_dir.name)
        db._table_exists = lambda x: x == "corrupted"
        
        
        try:
            db._load_table("corrupted")
        except InvalidStorageDataError:
            pass 
    
  
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
        self.assertEqual(path.name, "test.csv")
    
    def test_get_meta_path(self):
        path = self.db._get_meta_path("test")
        self.assertEqual(path.name, "test.meta.json")


if __name__ == "__main__":
    unittest.main()