import csv
from pathlib import Path
from typing import Any

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class CSVDatabase(Database):
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
                reader = csv.DictReader(file)
                records = list(reader)
                
                for record in records:
                    if 'id' in record:
                        record['id'] = int(record['id'])
                    if 'age' in record:
                        record['age'] = int(record['age']) if record['age'] else 0
                    if 'grade' in record:
                        record['grade'] = float(record['grade']) if record['grade'] else 0.0
                
                if not records:
                    meta_path = self._get_meta_path(table_name)
                    if meta_path.exists():
                        with meta_path.open("r", encoding="utf-8") as meta_file:
                            import json
                            meta = json.load(meta_file)
                            columns = tuple(meta.get("columns", []))
                            indexed_fields = meta.get("indexed_fields", [])
                            next_id = meta.get("next_id", 1)
                    else:
                        columns = ()
                        indexed_fields = []
                        next_id = 1
                else:
                    columns = tuple(reader.fieldnames) if reader.fieldnames else ()
                    meta_path = self._get_meta_path(table_name)
                    if meta_path.exists():
                        with meta_path.open("r", encoding="utf-8") as meta_file:
                            import json
                            meta = json.load(meta_file)
                            indexed_fields = meta.get("indexed_fields", [])
                            next_id = meta.get("next_id", 1)
                    else:
                        indexed_fields = []
                        next_id = max((r.get('id', 0) for r in records), default=0) + 1
                
                table = Table(columns, None, indexed_fields)
                table._next_id = next_id
                for record in records:
                    table._records.append(record)
                    for field_name, index in table._indices.items():
                        if field_name in record:
                            index.add_record(record['id'], record[field_name])
                
                return table
                
        except Exception as error:
            raise InvalidStorageDataError(
                f"Ошибка чтения CSV файла: {error}"
            ) from error
    
    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        meta_path = self._get_meta_path(table_name)
        
        if table.records:
            with table_path.open("w", encoding="utf-8", newline='') as file:
                fieldnames = list(table.columns) + ['id']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for record in table.get_all_records():
                    writer.writerow(record)
        else:
            with table_path.open("w", encoding="utf-8", newline='') as file:
                fieldnames = list(table.columns) + ['id']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
        
        import json
        with meta_path.open("w", encoding="utf-8") as meta_file:
            json.dump({
                "columns": list(table.columns),
                "indexed_fields": table.get_indexed_fields(),
                "next_id": table._next_id
            }, meta_file, ensure_ascii=False, indent=2)
    
    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"
    
    def _get_meta_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.meta.json"
    
    @property
    def records(self):
        return self._records if hasattr(self, '_records') else []