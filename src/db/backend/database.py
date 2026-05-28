from abc import ABC, abstractmethod
from typing import Any
from .table import Table


class Database(ABC):    
    def create_table(self, table_name: str, columns: tuple[str, ...], indexed_fields: list[str] | None = None) -> None:
        if self._table_exists(table_name):
            raise ValueError(f"Таблица '{table_name}' уже существует.") 
        self._save_table(table_name, Table(columns, indexed_fields=indexed_fields))
    
    def insert_record(self, table_name: str, record: dict[str, Any]) -> int:
        table = self._load_table(table_name)
        record_id = table.insert_record(record)
        self._save_table(table_name, table)
        return record_id
    
    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.select_records(**filters)
    
    def update_record(self, table_name: str, record_id: int, **updates: Any) -> dict[str, Any]:
        table = self._load_table(table_name)
        updated = table.update_record(record_id, **updates)
        self._save_table(table_name, table)
        return updated
    
    def delete_record(self, table_name: str, record_id: int) -> dict[str, Any]:
        table = self._load_table(table_name)
        deleted = table.delete_record(record_id)
        self._save_table(table_name, table)
        return deleted
    
    def get_all_records(self, table_name: str) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.get_all_records()
    
    def count_records(self, table_name: str) -> int:
        table = self._load_table(table_name)
        return table.count_records()
    
    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.sort_records(field, reverse)
    
    def add_index(self, table_name: str, field_name: str) -> None:
        table = self._load_table(table_name)
        table.add_index(field_name)
        self._save_table(table_name, table)
    
    def remove_index(self, table_name: str, field_name: str) -> None:
        table = self._load_table(table_name)
        table.remove_index(field_name)
        self._save_table(table_name, table)
    
    def get_indexed_fields(self, table_name: str) -> list[str]:
        table = self._load_table(table_name)
        return table.get_indexed_fields()
    
    @abstractmethod
    def _table_exists(self, table_name: str) -> bool:
        pass
    
    @abstractmethod
    def _load_table(self, table_name: str) -> Table:
        pass
    
    @abstractmethod
    def _save_table(self, table_name: str, table: Table) -> None:
        pass