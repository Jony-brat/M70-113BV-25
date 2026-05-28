from typing import Any

from .backend import MemoryDatabase, JSONDatabase, CSVDatabase
from .backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    RecordNotFoundError,
    InvalidNameError,
    InvalidAgeError,
    InvalidGradeError,
    InvalidEmailError,
    DuplicateEmailError,
    MissingColumnError,
    UnknownColumnError,
)


class ConsoleInterface:
  
    COLUMNS = ('first_name', 'last_name', 'age', 'grade', 'email')
    
    def __init__(self) -> None:
        self.db = self._select_database()
        self._ensure_table_exists()
    
    def _select_database(self):
        print("\n" + "=" * 60)
        print("          ВЫБОР ТИПА БАЗЫ ДАННЫХ")
        print("=" * 60)
        print("1. In-memory (данные не сохраняются)")
        print("2. Файловая (JSON) - данные сохраняются в JSON файлы")
        print("3. Файловая (CSV) - данные сохраняются в CSV файлы")
        print("-" * 60)
        
        while True:
            choice = input("Выберите тип БД (1-3): ").strip()
            if choice == "1":
                print("\nВыбрана in-memory база данных.")
                return MemoryDatabase()
            elif choice == "2":
                print("\nВыбрана файловая база данных (JSON).")
                return JSONDatabase()
            elif choice == "3":
                print("\nВыбрана файловая база данных (CSV).")
                return CSVDatabase()
            else:
                print("Неверный выбор. Пожалуйста, выберите 1, 2 или 3.")
    
    def _ensure_table_exists(self) -> None:
        try:
            self.db.select_records("students")
        except TableNotFoundError:
            self.db.create_table("students", self.COLUMNS, indexed_fields=['email', 'last_name'])
            print("Создана новая таблица 'students'.")
    
    def _print_menu(self) -> None:
        print("\n" + "=" * 60)
        print("          СИСТЕМА УПРАВЛЕНИЯ СТУДЕНТАМИ")
        print("=" * 60)
        print("1. Добавить студента")
        print("2. Показать всех студентов")
        print("3. Найти студентов по фильтру")
        print("4. Обновить информацию о студенте")
        print("5. Удалить студента")
        print("6. Сортировать студентов")
        print("7. Управление индексами")
        print("0. Выход")
        print("-" * 60)
    
    def _read_int(self, prompt: str) -> int:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                print("Ошибка: поле не может быть пустым.")
                continue
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")
    
    def _read_optional_int(self, prompt: str) -> int | None:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число.")
            return None
    
    def _read_float(self, prompt: str) -> float:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                print("Ошибка: поле не может быть пустым.")
                continue
            try:
                return float(raw)
            except ValueError:
                print("Ошибка: введите число (0-5).")
    
    def _read_optional_float(self, prompt: str) -> float | None:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            return float(raw)
        except ValueError:
            print("Ошибка: введите число.")
            return None
    
    def _read_string(self, prompt: str, required: bool = True) -> str | None:
        value = input(prompt).strip()
        if required and not value:
            print("Ошибка: поле не может быть пустым.")
            return None
        return value if value else None

    def _validate_record(self, first_name: str, last_name: str, age: int, grade: float, email: str) -> dict:
        if not first_name or len(first_name) < 2:
            raise InvalidNameError("Имя должно содержать минимум 2 символа.")
        if not last_name or len(last_name) < 2:
            raise InvalidNameError("Фамилия должна содержать минимум 2 символа.")
        if age < 0 or age > 120:
            raise InvalidAgeError("Возраст должен быть от 0 до 120 лет.")
        if grade < 0 or grade > 5:
            raise InvalidGradeError("Средний балл должен быть от 0 до 5.")
        if not email or "@" not in email or "." not in email:
            raise InvalidEmailError("Введите корректный email.")
        
        return {
            "first_name": first_name.strip().capitalize(),
            "last_name": last_name.strip().capitalize(),
            "age": age,
            "grade": grade,
            "email": email.strip().lower()
        }
    
    def _grade_to_text(self, grade: float) -> str:
        if grade >= 4.5:
            return "Отлично"
        elif grade >= 3.5:
            return "Хорошо"
        elif grade >= 2.5:
            return "Удовлетворительно"
        return "Неудовлетворительно"
    
    def _print_records(self, records: list[dict[str, Any]]) -> None:
        if not records:
            print("\nСтуденты не найдены.")
            return
        
        print("\n" + "=" * 120)
        print(f"{'ID':<5} {'Имя':<15} {'Фамилия':<15} {'Возраст':<8} {'Ср.балл':<10} {'Оценка':<15} {'Email':<35}")
        print("=" * 120)
        
        for record in records:
            email = record.get('email', '')[:32] + "..." if len(record.get('email', '')) > 35 else record.get('email', '')
            print(f"{record.get('id', '?'):<5} {record.get('first_name', ''):<15} {record.get('last_name', ''):<15} "
                  f"{record.get('age', '?'):<8} {record.get('grade', 0):<10.2f} {self._grade_to_text(record.get('grade', 0)):<15} {email:<35}")
        print("=" * 120)
        print(f"Всего студентов: {len(records)}")
    
    def _add_student(self) -> None:
        print("\nДОБАВЛЕНИЕ СТУДЕНТА")
        print("-" * 40)
        
        first_name = self._read_string("Имя: ")
        if not first_name:
            return
        last_name = self._read_string("Фамилия: ")
        if not last_name:
            return
        age = self._read_int("Возраст: ")
        grade = self._read_float("Средний балл (0-5): ")
        email = self._read_string("Email: ")
        if not email:
            return
        
        try:
            record = self._validate_record(first_name, last_name, age, grade, email)
            record_id = self.db.insert_record("students", record)
            print(f"\nСтудент успешно добавлен! ID: {record_id}")
        except (InvalidNameError, InvalidAgeError, InvalidGradeError, 
                InvalidEmailError, DuplicateEmailError, MissingColumnError) as e:
            print(f"\nОшибка: {e}")
    
    def _show_all_students(self) -> None:
        print("\nВСЕ СТУДЕНТЫ")
        try:
            records = self.db.get_all_records("students")
            self._print_records(records)
        except TableNotFoundError as e:
            print(f"\nОшибка: {e}")
    
    def _find_students(self) -> None:
        print("\nПОИСК СТУДЕНТОВ")
        print("(оставьте поле пустым для пропуска)")
        print("-" * 40)
        
        filters = {}
        
        student_id = self._read_optional_int("ID: ")
        if student_id is not None:
            filters['id'] = student_id
        
        first_name = self._read_string("Имя: ", required=False)
        if first_name:
            filters['first_name'] = first_name.strip().capitalize()
        
        last_name = self._read_string("Фамилия: ", required=False)
        if last_name:
            filters['last_name'] = last_name.strip().capitalize()
        
        age = self._read_optional_int("Возраст: ")
        if age is not None:
            filters['age'] = age
        
        grade = self._read_optional_float("Средний балл: ")
        if grade is not None:
            filters['grade'] = grade
        
        email = self._read_string("Email: ", required=False)
        if email:
            filters['email'] = email.strip().lower()
        
        try:
            records = self.db.select_records("students", **filters)
            self._print_records(records)
        except (TableNotFoundError, UnknownColumnError) as e:
            print(f"\nОшибка: {e}")
    
    def _update_student(self) -> None:
        print("\nОБНОВЛЕНИЕ СТУДЕНТА")
        print("-" * 40)
        
        student_id = self._read_int("ID студента: ")
        
        try:
            existing = self.db.select_records("students", id=student_id)
            if not existing:
                print(f"\nСтудент с ID {student_id} не найден.")
                return
            
            print(f"\nТекущая информация: {existing[0]}")
            print("\n(оставьте поле пустым для пропуска)")
            print("-" * 40)
            
            updates = {}
            
            first_name = self._read_string("Новое имя: ", required=False)
            if first_name:
                updates['first_name'] = first_name.strip().capitalize()
            
            last_name = self._read_string("Новая фамилия: ", required=False)
            if last_name:
                updates['last_name'] = last_name.strip().capitalize()
            
            age_input = input("Новый возраст: ").strip()
            if age_input:
                updates['age'] = int(age_input)
            
            grade_input = input("Новый средний балл: ").strip()
            if grade_input:
                updates['grade'] = float(grade_input)
            
            email = self._read_string("Новый email: ", required=False)
            if email:
                updates['email'] = email.strip().lower()
            
            if updates:
                updated = self.db.update_record("students", student_id, **updates)
                print(f"\nСтудент обновлён: {updated}")
            else:
                print("\nНет изменений.")
                
        except (TableNotFoundError, RecordNotFoundError, InvalidNameError,
                InvalidAgeError, InvalidGradeError, InvalidEmailError,
                DuplicateEmailError, MissingColumnError, UnknownColumnError) as e:
            print(f"\nОшибка: {e}")
    
    def _delete_student(self) -> None:
        print("\nУДАЛЕНИЕ СТУДЕНТА")
        print("-" * 40)
        
        student_id = self._read_int("ID студента: ")
        
        try:
            existing = self.db.select_records("students", id=student_id)
            if not existing:
                print(f"\nСтудент с ID {student_id} не найден.")
                return
            
            print(f"\nСтудент для удаления: {existing[0]}")
            confirm = input("\nВы уверены? (да/нет): ").strip().lower()
            
            if confirm in ("да", "yes", "y", "д"):
                deleted = self.db.delete_record("students", student_id)
                print(f"\nСтудент удалён: {deleted.get('first_name')} {deleted.get('last_name')}")
            else:
                print("\nУдаление отменено.")
                
        except (TableNotFoundError, RecordNotFoundError) as e:
            print(f"\nОшибка: {e}")
    
    def _sort_students(self) -> None:
        print("\nСОРТИРОВКА СТУДЕНТОВ")
        print("-" * 40)
        print("Поля для сортировки:")
        print("1. ID")
        print("2. Имя")
        print("3. Фамилия")
        print("4. Возраст")
        print("5. Средний балл")
        print("6. Email")
        
        field_map = {
            1: 'id', 2: 'first_name', 3: 'last_name',
            4: 'age', 5: 'grade', 6: 'email'
        }
        
        field_choice = self._read_int("Выберите поле (1-6): ")
        if field_choice not in field_map:
            print("\nНеверный выбор.")
            return
        
        field = field_map[field_choice]
        
        print("\n1. По возрастанию")
        print("2. По убыванию")
        order_choice = self._read_int("Выберите порядок (1-2): ")
        reverse = (order_choice == 2)
        
        try:
            records = self.db.sort_records("students", field, reverse)
            self._print_records(records)
        except (TableNotFoundError, UnknownColumnError) as e:
            print(f"\nОшибка: {e}")
    
    def _manage_indexes(self) -> None:
        print("\nУПРАВЛЕНИЕ ИНДЕКСАМИ")
        print("-" * 40)
        
        try:
            indexed = self.db.get_indexed_fields("students")
            print(f"\nТекущие индексы: {indexed if indexed else 'нет'}")
            
            print("\n1. Добавить индекс")
            print("2. Удалить индекс")
            print("0. Назад")
            
            choice = self._read_int("Выберите действие (0-2): ")
            
            if choice == 1:
                print(f"\nДоступные поля: {self.COLUMNS}")
                field = self._read_string("Имя поля для индексации: ")
                if field and field in self.COLUMNS:
                    self.db.add_index("students", field)
                    print(f"Индекс для поля '{field}' добавлен.")
                else:
                    print(f"Поле '{field}' не найдено.")
            
            elif choice == 2:
                field = self._read_string("Имя поля для удаления индекса: ")
                if field:
                    self.db.remove_index("students", field)
                    print(f"Индекс для поля '{field}' удалён.")
                    
        except (TableNotFoundError, UnknownColumnError) as e:
            print(f"\nОшибка: {e}")
    
    def run(self) -> None:
        print("\n" + "=" * 60)
        print("ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ УПРАВЛЕНИЯ СТУДЕНТАМИ")
        print("=" * 60)
        
        while True:
            self._print_menu()
            action = input("\nВыберите действие (0-7): ").strip()
            
            if action == "1":
                self._add_student()
            elif action == "2":
                self._show_all_students()
            elif action == "3":
                self._find_students()
            elif action == "4":
                self._update_student()
            elif action == "5":
                self._delete_student()
            elif action == "6":
                self._sort_students()
            elif action == "7":
                self._manage_indexes()
            elif action == "0":
                print("\nДо свидания!")
                break
            else:
                print("\nНеизвестная команда.")
            
            input("\nНажмите Enter для продолжения...")


def run() -> None:
    app = ConsoleInterface()
    app.run()