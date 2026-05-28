"""
Модуль in-memory хранилища для базы данных.
Реализует класс StudentTable с CRUD операциями.
"""

from .errors import (
    InvalidAgeError,
    InvalidGradeError,
    InvalidNameError,
    InvalidEmailError,
    DuplicateEmailError,
    RecordNotFoundError,
)

type StudentRecord = tuple[int, str, str, int, float, str]


class StudentTable:
    """Класс для управления таблицей студентов."""

    def __init__(self) -> None:
        """Инициализирует пустую таблицу студентов и счётчик ID."""
        self._students: list[StudentRecord] = []
        self._next_id: int = 1

    def _generate_id(self) -> int:
        """Генерирует следующий уникальный идентификатор."""
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def _validate_name(self, name: str, field_name: str) -> str:
        """
        Валидирует имя или фамилию.
        
        Args:
            name: Имя или фамилия для проверки
            field_name: Название поля для сообщения об ошибке
            
        Returns:
            Очищенная и капитализированная строка
            
        Raises:
            InvalidNameError: Если имя некорректно
        """
        if not name or not name.strip():
            raise InvalidNameError(f"{field_name} не может быть пустым.")
        if len(name.strip()) < 2:
            raise InvalidNameError(f"{field_name} должно содержать минимум 2 символа.")
        return name.strip().capitalize()

    def _validate_age(self, age: int) -> int:
        """
        Валидирует возраст.
        
        Args:
            age: Возраст для проверки
            
        Returns:
            Проверенный возраст
            
        Raises:
            InvalidAgeError: Если возраст некорректен
        """
        if age < 0 or age > 120:
            raise InvalidAgeError("Возраст должен быть от 0 до 120 лет.")
        return age

    def _validate_grade(self, grade: float) -> float:
        """
        Валидирует средний балл.
        
        Args:
            grade: Балл для проверки
            
        Returns:
            Проверенный балл
            
        Raises:
            InvalidGradeError: Если балл некорректен
        """
        if grade < 0 or grade > 5:
            raise InvalidGradeError("Средний балл должен быть от 0 до 5.")
        return grade

    def _validate_email(self, email: str, exclude_id: int | None = None) -> str:
        """
        Валидирует email и проверяет уникальность.
        
        Args:
            email: Email для проверки
            exclude_id: ID записи, которую нужно исключить из проверки уникальности
            
        Returns:
            Очищенный и приведённый к нижнему регистру email
            
        Raises:
            InvalidEmailError: Если email некорректен
            DuplicateEmailError: Если email уже существует
        """
        if not email or not email.strip():
            raise InvalidEmailError("Email не может быть пустым.")

        email_clean = email.strip().lower()

        if "@" not in email_clean or "." not in email_clean:
            raise InvalidEmailError("Введите корректный email (должен содержать @ и .)")

        for record in self._students:
            if exclude_id is not None and record[0] == exclude_id:
                continue
            if record[5] == email_clean:
                raise DuplicateEmailError(f"Студент с email '{email}' уже существует.")

        return email_clean

    def create_record(
        self,
        first_name: str,
        last_name: str,
        age: int,
        grade: float,
        email: str,
    ) -> StudentRecord:
        """
        Добавляет нового студента в таблицу.

        Args:
            first_name: Имя студента
            last_name: Фамилия студента
            age: Возраст студента
            grade: Средний балл
            email: Email студента

        Returns:
            Созданная запись

        Raises:
            InvalidNameError: При некорректном имени или фамилии
            InvalidAgeError: При некорректном возрасте
            InvalidGradeError: При некорректном балле
            InvalidEmailError: При некорректном email
            DuplicateEmailError: При дублировании email
        """
        first_name_valid = self._validate_name(first_name, "Имя")
        last_name_valid = self._validate_name(last_name, "Фамилия")
        age_valid = self._validate_age(age)
        grade_valid = self._validate_grade(grade)
        email_valid = self._validate_email(email)

        new_record: StudentRecord = (
            self._generate_id(),
            first_name_valid,
            last_name_valid,
            age_valid,
            grade_valid,
            email_valid,
        )
        self._students.append(new_record)
        return new_record

    def select_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        age: int | None = None,
        grade: float | None = None,
        email: str | None = None,
    ) -> list[StudentRecord]:
        """
        Выполняет выборку записей с фильтрацией.

        Args:
            student_id: Фильтр по ID
            first_name: Фильтр по имени
            last_name: Фильтр по фамилии
            age: Фильтр по возрасту
            grade: Фильтр по среднему баллу
            email: Фильтр по email

        Returns:
            Список записей, удовлетворяющих фильтрам
        """
        if all(param is None for param in [student_id, first_name, last_name, age, grade, email]):
            return self._students.copy()

        result: list[StudentRecord] = []

        for record in self._students:
            if student_id is not None and record[0] != student_id:
                continue
            if first_name is not None and record[1].lower() != first_name.lower():
                continue
            if last_name is not None and record[2].lower() != last_name.lower():
                continue
            if age is not None and record[3] != age:
                continue
            if grade is not None and record[4] != grade:
                continue
            if email is not None and record[5].lower() != email.lower():
                continue
            result.append(record)

        return result

    def update_record(
        self,
        student_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        age: int | None = None,
        grade: float | None = None,
        email: str | None = None,
    ) -> StudentRecord:
        """
        Обновляет существующую запись по ID.

        Args:
            student_id: ID студента для обновления
            first_name: Новое имя (опционально)
            last_name: Новая фамилия (опционально)
            age: Новый возраст (опционально)
            grade: Новый средний балл (опционально)
            email: Новый email (опционально)

        Returns:
            Обновлённая запись

        Raises:
            RecordNotFoundError: Если запись с указанным ID не найдена
        """
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                updated_record = list(record)

                if first_name is not None:
                    updated_record[1] = self._validate_name(first_name, "Имя")
                if last_name is not None:
                    updated_record[2] = self._validate_name(last_name, "Фамилия")
                if age is not None:
                    updated_record[3] = self._validate_age(age)
                if grade is not None:
                    updated_record[4] = self._validate_grade(grade)
                if email is not None:
                    updated_record[5] = self._validate_email(email, student_id)

                new_record = tuple(updated_record)
                self._students[i] = new_record
                return new_record

        raise RecordNotFoundError(f"Студент с id={student_id} не найден.")

    def delete_record(self, student_id: int) -> StudentRecord:
        """
        Удаляет запись по ID.

        Args:
            student_id: ID студента для удаления

        Returns:
            Удалённая запись

        Raises:
            RecordNotFoundError: Если запись с указанным ID не найдена
        """
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                return self._students.pop(i)

        raise RecordNotFoundError(f"Студент с id={student_id} не найден.")

    def get_all_records(self) -> list[StudentRecord]:
        """Возвращает копию всех записей."""
        return self._students.copy()

    def count_records(self) -> int:
        """Возвращает количество записей в таблице."""
        return len(self._students)

    def clear(self) -> None:
        """Очищает таблицу (для тестирования)."""
        self._students.clear()
        self._next_id = 1