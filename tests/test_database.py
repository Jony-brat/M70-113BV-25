import unittest
from abc import ABC
from src.db.backend.database import Database
from src.db.backend.table import Table
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    RecordNotFoundError,
    UnknownColumnError,
)


class ConcreteDatabase(Database):
    def __init__(self):
        self.tables = {}
    
    def _table_exists(self, table_name: str) -> bool:
        return table_name in self.tables
    
    def _load_table(self, table_name: str) -> Table:
        if table_name not in self.tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        return self.tables[table_name]
    
    def _save_table(self, table_name: str, table: Table) -> None:
        self.tables[table_name] = table


class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        self.db = ConcreteDatabase()
        self.columns = ('first_name', 'last_name', 'age', 'grade', 'email')
    
    def test_is_abstract(self):
        """Проверка, что Database - абстрактный класс."""
        self.assertTrue(issubclass(Database, ABC))
    
    def test_create_table_success(self):
        """Тест успешного создания таблицы."""
        self.db.create_table("students", self.columns, indexed_fields=['email'])
        self.assertTrue(self.db._table_exists("students"))
    
    def test_create_table_already_exists(self):
        """Тест создания существующей таблицы."""
        self.db.create_table("students", self.columns)
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", self.columns)
    
    def test_create_table_without_indexes(self):
        """Тест создания таблицы без индексов."""
        self.db.create_table("test", ('name',))
        table = self.db._load_table("test")
        self.assertEqual(table.get_indexed_fields(), [])
    
    def test_insert_record_success(self):
        """Тест успешной вставки записи."""
        self.db.create_table("students", self.columns)
        record = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'age': 20,
            'grade': 4.7,
            'email': 'ivan@example.com'
        }
        record_id = self.db.insert_record("students", record)
        self.assertEqual(record_id, 1)
    
    def test_insert_record_table_not_found(self):
        """Тест вставки в несуществующую таблицу."""
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record("unknown", {'name': 'test'})
    
    def test_select_records_success(self):
        """Тест успешной выборки записей."""
        self.db.create_table("students", self.columns)
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
    
    def test_select_records_with_filters(self):
        """Тест выборки с фильтрами."""
        self.db.create_table("students", self.columns)
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        records = self.db.select_records("students", first_name='Иван')
        self.assertEqual(len(records), 1)
    
    def test_select_records_table_not_found(self):
        """Тест выборки из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("unknown")
    
    def test_update_record_success(self):
        """Тест успешного обновления записи."""
        self.db.create_table("students", self.columns)
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        updated = self.db.update_record("students", record_id, first_name='Пётр')
        self.assertEqual(updated['first_name'], 'Пётр')
    
    def test_update_record_table_not_found(self):
        """Тест обновления в несуществующей таблице."""
        with self.assertRaises(TableNotFoundError):
            self.db.update_record("unknown", 1, name='test')
    
    def test_update_record_not_found(self):
        """Тест обновления несуществующей записи."""
        self.db.create_table("students", self.columns)
        with self.assertRaises(RecordNotFoundError):
            self.db.update_record("students", 999, name='test')
    
    def test_delete_record_success(self):
        """Тест успешного удаления записи."""
        self.db.create_table("students", self.columns)
        record_id = self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        deleted = self.db.delete_record("students", record_id)
        self.assertEqual(deleted['first_name'], 'Иван')
        self.assertEqual(self.db.count_records("students"), 0)
    
    def test_delete_record_table_not_found(self):
        """Тест удаления из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.delete_record("unknown", 1)
    
    def test_delete_record_not_found(self):
        """Тест удаления несуществующей записи."""
        self.db.create_table("students", self.columns)
        with self.assertRaises(RecordNotFoundError):
            self.db.delete_record("students", 999)
    
    def test_get_all_records_success(self):
        """Тест получения всех записей."""
        self.db.create_table("students", self.columns)
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        
        records = self.db.get_all_records("students")
        self.assertEqual(len(records), 1)
    
    def test_get_all_records_table_not_found(self):
        """Тест получения всех записей из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.get_all_records("unknown")
    
    def test_count_records_success(self):
        """Тест подсчёта записей."""
        self.db.create_table("students", self.columns)
        self.assertEqual(self.db.count_records("students"), 0)
        
        self.db.insert_record("students", {
            'first_name': 'Иван', 'last_name': 'Петров',
            'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
        })
        self.assertEqual(self.db.count_records("students"), 1)
    
    def test_count_records_table_not_found(self):
        """Тест подсчёта записей в несуществующей таблице."""
        with self.assertRaises(TableNotFoundError):
            self.db.count_records("unknown")
    
    def test_sort_records_success(self):
        """Тест сортировки записей."""
        self.db.create_table("students", self.columns)
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
        """Тест сортировки в несуществующей таблице."""
        with self.assertRaises(TableNotFoundError):
            self.db.sort_records("unknown", 'name')
    
    def test_sort_records_unknown_field(self):
        """Тест сортировки по неизвестному полю."""
        self.db.create_table("students", self.columns)
        with self.assertRaises(UnknownColumnError):
            self.db.sort_records("students", 'unknown_field')
    
    def test_add_index_success(self):
        """Тест добавления индекса."""
        self.db.create_table("students", self.columns)
        self.db.add_index("students", 'age')
        indexes = self.db.get_indexed_fields("students")
        self.assertIn('age', indexes)
    
    def test_add_index_table_not_found(self):
        """Тест добавления индекса в несуществующей таблице."""
        with self.assertRaises(TableNotFoundError):
            self.db.add_index("unknown", 'field')
    
    def test_add_index_unknown_field(self):
        """Тест добавления индекса для неизвестного поля."""
        self.db.create_table("students", self.columns)
        with self.assertRaises(UnknownColumnError):
            self.db.add_index("students", 'unknown_field')
    
    def test_remove_index_success(self):
        """Тест удаления индекса."""
        self.db.create_table("students", self.columns, indexed_fields=['email'])
        self.db.remove_index("students", 'email')
        indexes = self.db.get_indexed_fields("students")
        self.assertNotIn('email', indexes)
    
    def test_remove_index_table_not_found(self):
        """Тест удаления индекса в несуществующей таблице."""
        with self.assertRaises(TableNotFoundError):
            self.db.remove_index("unknown", 'field')
    
    def test_get_indexed_fields_success(self):
        """Тест получения списка индексированных полей."""
        self.db.create_table("students", self.columns, indexed_fields=['email', 'last_name'])
        indexes = self.db.get_indexed_fields("students")
        self.assertIn('email', indexes)
        self.assertIn('last_name', indexes)
    
    def test_get_indexed_fields_table_not_found(self):
        """Тест получения индексов из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.get_indexed_fields("unknown")


if __name__ == "__main__":
    unittest.main()