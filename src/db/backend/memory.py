from typing import Any
from .database import Database
from .table import StudentTable


class MemoryDatabase(Database):
    
    def __init__(self):
        super().__init__()
        if "students" not in self._tables:
            self._tables["students"] = StudentTable("students")
    
    def create_student(self, first_name: str, last_name: str, age: int, grade: float, email: str) -> dict[str, Any]:
        table = self.get_table("students")
        return table.create_record(first_name, last_name, age, grade, email)
    
    def get_all_students(self) -> list[dict[str, Any]]:
        return self.get_all_records("students")
    
    def find_students(self, **filters: Any) -> list[dict[str, Any]]:
        return self.select_records("students", **filters)
    
    def update_student(self, student_id: int, **updates: Any) -> dict[str, Any]:
        return self.update_record("students", student_id, **updates)
    
    def delete_student(self, student_id: int) -> dict[str, Any]:
        return self.delete_record("students", student_id)