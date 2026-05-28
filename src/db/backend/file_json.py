import json
from pathlib import Path
from typing import Any

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class JSONDatabase(Database):    
    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
    
    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()
    
    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        
        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
            ) from error
        
        return Table.from_dict(data)
    
    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        
        with table_path.open("w", encoding="utf-8") as file:
            json.dump(
                table.to_dict(),
                file,
                ensure_ascii=False,
                indent=2,
            )
    
    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"