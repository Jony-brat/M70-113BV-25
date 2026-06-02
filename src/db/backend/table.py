from typing import Any

from .errors import MissingColumnError, UnknownColumnError


class Table:
    """Таблица с фиксированным набором колонок."""

    def __init__(self, columns: tuple[str, ...], records: list[dict[str, Any]] | None = None) -> None:
        self.columns = columns
        self.records: list[dict[str, Any]] = []

        if records is not None:
            for record in records:
                self.insert_record(record)

    def insert_record(self, record: dict[str, Any]) -> None:
        """Добавляет запись, если она соответствует схеме таблицы."""
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

        self.records.append(record.copy())

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        """Возвращает записи, удовлетворяющие всем переданным фильтрам."""
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(
                f"Поле '{unknown_filters[0]}' не определено в структуре таблицы."
            )

        if not filters:
            return [record.copy() for record in self.records]

        result: list[dict[str, Any]] = []
        for record in self.records:
            if all(record.get(key) == value for key, value in filters.items()):
                result.append(record.copy())

        return result

    def update_record(self, record_id: int, id_field: str, **updates: Any) -> dict[str, Any] | None:
        """Обновляет запись по указанному полю ID."""
        unknown_updates = [key for key in updates if key not in self.columns]
        if unknown_updates:
            raise UnknownColumnError(
                f"Поле '{unknown_updates[0]}' не определено в структуре таблицы."
            )

        if id_field not in self.columns:
            raise UnknownColumnError(
                f"Поле '{id_field}' не определено в структуре таблицы."
            )

        for i, record in enumerate(self.records):
            if record.get(id_field) == record_id:
                updated_record = record.copy()
                updated_record.update(updates)
                missing_columns = [col for col in self.columns if col not in updated_record]
                if missing_columns:
                    raise MissingColumnError(
                        f"Отсутствует поле '{missing_columns[0]}' в записи после обновления."
                    )
                self.records[i] = updated_record
                return updated_record.copy()

        return None

    def delete_record(self, record_id: int, id_field: str) -> dict[str, Any] | None:
        """Удаляет запись по указанному полю ID."""
        if id_field not in self.columns:
            raise UnknownColumnError(
                f"Поле '{id_field}' не определено в структуре таблицы."
            )

        for i, record in enumerate(self.records):
            if record.get(id_field) == record_id:
                return self.records.pop(i).copy()

        return None

    def get_all_records(self) -> list[dict[str, Any]]:
        """Возвращает копию всех записей."""
        return [record.copy() for record in self.records]

    def count_records(self) -> int:
        """Возвращает количество записей."""
        return len(self.records)

    def clear(self) -> None:
        """Очищает все записи."""
        self.records.clear()