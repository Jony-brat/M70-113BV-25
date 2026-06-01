from typing import Any
from .errors import (
    InvalidNameError, 
    InvalidAgeError, 
    InvalidGradeError, 
    InvalidEmailError, 
    DuplicateEmailError,
    RecordNotFoundError
)


class Table:
    
    def __init__(self, name: str):
        self.name = name
        self._records: list[dict[str, Any]] = []
        self._next_id: int = 1
    
    def _generate_id(self) -> int:
        current_id = self._next_id
        self._next_id += 1
        return current_id
    
    def _validate_name(self, name: str, field_name: str) -> str:
        if not name or not name.strip():
            raise InvalidNameError(f"{field_name} не может быть пустым.")
        
        cleaned_name = name.strip()
        if len(cleaned_name) < 2:
            raise InvalidNameError(f"{field_name} должно содержать минимум 2 символа.")
        
        return cleaned_name.capitalize()
    
    def _validate_age(self, age: int) -> int:
        if age < 0 or age > 120:
            raise InvalidAgeError("Возраст должен быть от 0 до 120 лет.")
        return age
    
    def _validate_grade(self, grade: float) -> float:
        if grade < 0 or grade > 5:
            raise InvalidGradeError("Средний балл должен быть от 0 до 5.")
        return grade
    
    def _validate_email(self, email: str, exclude_id: int | None = None) -> str:
        if not email or not email.strip():
            raise InvalidEmailError("Email не может быть пустым.")
        
        cleaned_email = email.strip().lower()
        
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise InvalidEmailError("Введите корректный email (должен содержать @ и .)")
        
        for record in self._records:
            if exclude_id is not None and record.get('id') == exclude_id:
                continue
            if record.get('email') == cleaned_email:
                raise DuplicateEmailError(f"Студент с email '{email}' уже существует в таблице '{self.name}'.")
        
        return cleaned_email
    
    def create_record(self, first_name: str, last_name: str, age: int, grade: float, email: str) -> dict[str, Any]:
        first_name_valid = self._validate_name(first_name, "Имя")
        last_name_valid = self._validate_name(last_name, "Фамилия")
        age_valid = self._validate_age(age)
        grade_valid = self._validate_grade(grade)
        email_valid = self._validate_email(email)
        
        record = {
            'id': self._generate_id(),
            'first_name': first_name_valid,
            'last_name': last_name_valid,
            'age': age_valid,
            'grade': grade_valid,
            'email': email_valid
        }
        
        self._records.append(record)
        return record.copy()
    
    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        if not filters:
            return [record.copy() for record in self._records]
        
        result = []
        for record in self._records:
            match = True
            for key, value in filters.items():
                if key not in record:
                    continue
                if isinstance(value, str) and isinstance(record[key], str):
                    if record[key].lower() != value.lower():
                        match = False
                        break
                elif record[key] != value:
                    match = False
                    break
            if match:
                result.append(record.copy())
        
        return result
    
    def update_record(self, record_id: int, **updates: Any) -> dict[str, Any]:
        for i, record in enumerate(self._records):
            if record['id'] == record_id:
                updated_record = record.copy()
                
                if 'first_name' in updates:
                    updated_record['first_name'] = self._validate_name(updates['first_name'], "Имя")
                if 'last_name' in updates:
                    updated_record['last_name'] = self._validate_name(updates['last_name'], "Фамилия")
                if 'age' in updates:
                    updated_record['age'] = self._validate_age(updates['age'])
                if 'grade' in updates:
                    updated_record['grade'] = self._validate_grade(updates['grade'])
                if 'email' in updates:
                    updated_record['email'] = self._validate_email(updates['email'], record_id)
                
                self._records[i] = updated_record
                return updated_record.copy()
        
        raise RecordNotFoundError(f"Запись с id={record_id} не найдена в таблице '{self.name}'.")
    
    def delete_record(self, record_id: int) -> dict[str, Any]:
        for i, record in enumerate(self._records):
            if record['id'] == record_id:
                return self._records.pop(i).copy()
        
        raise RecordNotFoundError(f"Запись с id={record_id} не найдена в таблице '{self.name}'.")
    
    def get_all_records(self) -> list[dict[str, Any]]:
        return [record.copy() for record in self._records]
    
    def count_records(self) -> int:
        return len(self._records)
    
    def clear(self) -> None:
        self._records.clear()
        self._next_id = 1


class StudentTable(Table):
    
    def __init__(self, name: str = "students"):
        super().__init__(name)
    
    def create_record(self, first_name: str, last_name: str, age: int, grade: float, email: str) -> dict[str, Any]:
        return super().create_record(first_name, last_name, age, grade, email)