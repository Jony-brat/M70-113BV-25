from typing import Any, Callable
from .errors import MissingColumnError, UnknownColumnError, RecordNotFoundError


class Index:
    def __init__(self, field_name: str):
        self.field_name = field_name
        self._index: dict[Any, list[int]] = {}
    def add_record(self, record_id: int, value: Any) -> None:

        if value not in self._index:
            self._index[value] = []
        self._index[value].append(record_id) 
    def remove_record(self, record_id: int, value: Any) -> None:

        if value in self._index:
            self._index[value] = [rid for rid in self._index[value] if rid != record_id]
            if not self._index[value]:
                del self._index[value]
    
    def find(self, value: Any) -> list[int]:

        return self._index.get(value, []).copy()
    
    def update_record(self, record_id: int, old_value: Any, new_value: Any) -> None:

        self.remove_record(record_id, old_value)
        self.add_record(record_id, new_value)
    
    def clear(self) -> None:

        self._index.clear()


class Table:

    def __init__(
        self, 
        columns: tuple[str, ...], 
        records: list[dict[str, Any]] | None = None,
        indexed_fields: list[str] | None = None
    ) -> None:
        self.columns = columns
        self._records: list[dict[str, Any]] = []
        self._next_id: int = 1
        self._indices: dict[str, Index] = {}
        
        if indexed_fields:
            for field in indexed_fields:
                if field in columns:
                    self._indices[field] = Index(field)
        
        if records is not None:
            for record in records:
                self.insert_record(record)
    
    def _generate_id(self) -> int:
        current_id = self._next_id
        self._next_id += 1
        return current_id
    
    def _update_indices(self, record_id: int, record: dict[str, Any], is_insert: bool = True) -> None:

        for field_name, index in self._indices.items():
            if field_name in record:
                if is_insert:
                    index.add_record(record_id, record[field_name])
                else:
                    pass
    
    def insert_record(self, record: dict[str, Any]) -> int:
    
        missing_columns = [column for column in self.columns if column not in record]
        if missing_columns:
            raise MissingColumnError(
                f"Отсутствует поле '{missing_columns[0]}' в записи."
            )
        
        extra_columns = [column for column in record if column not in self.columns]
        if extra_columns:
            raise UnknownColumnError(
                f"Поле '{extra_columns[0]}' не определено в структуре таблицы."
            )
        

        record_id = self._generate_id()
        new_record = record.copy()
        new_record['id'] = record_id
        
        self._records.append(new_record)
        for field_name, index in self._indices.items():
            if field_name in new_record:
                index.add_record(record_id, new_record[field_name])
        
        return record_id
    
    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        unknown_filters = [key for key in filters if key not in self.columns and key != 'id']
        if unknown_filters:
            raise UnknownColumnError(
                f"Поле '{unknown_filters[0]}' не определено в структуре таблицы."
            )
        

        if not filters:
            return [record.copy() for record in self._records]
        

        indexed_filter = None
        for field in filters:
            if field in self._indices and field != 'id':
                indexed_filter = field
                break
        
        if indexed_filter and indexed_filter in filters:
            index = self._indices[indexed_filter]
            candidate_ids = index.find(filters[indexed_filter])
            candidate_records = [r for r in self._records if r['id'] in candidate_ids]
        else:
            candidate_records = self._records
 
        result: list[dict[str, Any]] = []
        for record in candidate_records:
            if all(record.get(key) == value for key, value in filters.items()):
                result.append(record.copy())
        
        return result
    
    def update_record(self, record_id: int, **updates: Any) -> dict[str, Any]:

        for i, record in enumerate(self._records):
            if record['id'] == record_id:
                old_record = record.copy()
                

                for field, value in updates.items():
                    if field not in self.columns and field != 'id':
                        raise UnknownColumnError(
                            f"Поле '{field}' не определено в структуре таблицы."
                        )

                updated_record = record.copy()
                updated_record.update(updates)
                

                missing_columns = [col for col in self.columns if col not in updated_record]
                if missing_columns:
                    raise MissingColumnError(
                        f"Отсутствует поле '{missing_columns[0]}' после обновления."
                    )
                

                for field_name, index in self._indices.items():
                    if field_name in updates and field_name in old_record:
                        index.update_record(record_id, old_record[field_name], updates[field_name])
                    elif field_name in updates:
                        index.add_record(record_id, updates[field_name])
                
                self._records[i] = updated_record
                return updated_record.copy()
        
        raise RecordNotFoundError(f"Запись с id={record_id} не найдена.")
    
    def delete_record(self, record_id: int) -> dict[str, Any]:

        for i, record in enumerate(self._records):
            if record['id'] == record_id:
                for field_name, index in self._indices.items():
                    if field_name in record:
                        index.remove_record(record_id, record[field_name])
                
                return self._records.pop(i).copy()
        
        raise RecordNotFoundError(f"Запись с id={record_id} не найдена.")
    
    def get_all_records(self) -> list[dict[str, Any]]:

        return [record.copy() for record in self._records]
    
    def count_records(self) -> int:

        return len(self._records)
    
    def sort_records(self, field: str, reverse: bool = False) -> list[dict[str, Any]]:

        if field not in self.columns and field != 'id':
            raise UnknownColumnError(f"Поле '{field}' не определено в структуре таблицы.")
        
        return sorted(self._records, key=lambda x: x.get(field), reverse=reverse)
    
    def add_index(self, field_name: str) -> None:

        if field_name not in self.columns:
            raise UnknownColumnError(f"Поле '{field_name}' не определено в структуре таблицы.")
        
        if field_name in self._indices:
            return  
        
        self._indices[field_name] = Index(field_name)

        for record in self._records:
            if field_name in record:
                self._indices[field_name].add_record(record['id'], record[field_name])
    
    def remove_index(self, field_name: str) -> None:
        if field_name in self._indices:
            del self._indices[field_name]
    
    def get_indexed_fields(self) -> list[str]:
        return list(self._indices.keys())
    
    def to_dict(self) -> dict[str, Any]:

        return {
            "columns": list(self.columns),
            "records": [record.copy() for record in self._records],
            "next_id": self._next_id,
            "indexed_fields": self.get_indexed_fields()
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Table':

        columns = tuple(data["columns"])
        records = data.get("records", [])
        indexed_fields = data.get("indexed_fields", [])
        
        table = cls(columns, None, indexed_fields)
        table._next_id = data.get("next_id", 1)
        
        for record in records:
            table._records.append(record.copy())

            for field_name, index in table._indices.items():
                if field_name in record:
                    index.add_record(record['id'], record[field_name])
        
        return table