from typing import Any
from .errors import TableAlreadyExistsError, TableNotFoundError, RecordNotFoundError
from .table import Table


class Database:
    
    def __init__(self):
        self._tables: dict[str, Table] = {}
    
    def create_table(self, table_name: str) -> Table:
        if table_name in self._tables:
            raise TableAlreadyExistsError(f"Таблица '{table_name}' уже существует.")
        
        table = Table(table_name)
        self._tables[table_name] = table
        return table
    
    def drop_table(self, table_name: str) -> None:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        
        del self._tables[table_name]
    
    def get_table(self, table_name: str) -> Table:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        
        return self._tables[table_name]
    
    def list_tables(self) -> list[str]:
        return list(self._tables.keys())
    
    def table_exists(self, table_name: str) -> bool:
        return table_name in self._tables
    
    def insert_record(self, table_name: str, **record_data: Any) -> dict[str, Any]:
        table = self.get_table(table_name)
        return table.create_record(**record_data)
    
    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        table = self.get_table(table_name)
        return table.select_records(**filters)
    
    def update_record(self, table_name: str, record_id: int, **updates: Any) -> dict[str, Any]:
        table = self.get_table(table_name)
        return table.update_record(record_id, **updates)
    
    def delete_record(self, table_name: str, record_id: int) -> dict[str, Any]:
        table = self.get_table(table_name)
        return table.delete_record(record_id)
    
    def get_all_records(self, table_name: str) -> list[dict[str, Any]]:
        table = self.get_table(table_name)
        return table.get_all_records()
    
    def count_records(self, table_name: str) -> int:
        table = self.get_table(table_name)
        return table.count_records()
    
    def clear_table(self, table_name: str) -> None:
        table = self.get_table(table_name)
        table.clear()