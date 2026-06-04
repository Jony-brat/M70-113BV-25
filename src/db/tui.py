from .backend.database import Database
from .backend.errors import (
    InvalidAgeError,
    InvalidGradeError,
    InvalidNameError,
    InvalidEmailError,
    DuplicateEmailError,
    RecordNotFoundError,
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)
from .backend.file import FileDatabase
from .backend.memory import MemoryDatabase


class ConsoleInterface:
    def __init__(self) -> None:
        self.db = self._select_database()
        self._init_students_table()

    def _select_database(self) -> Database:
        print("\n" + "=" * 60)
        print("ВЫБОР ТИПА БАЗЫ ДАННЫХ")
        print("=" * 60)
        print("1. In-memory (данные не сохраняются)")
        print("2. File (данные сохраняются в JSON файлы)")
        print("-" * 60)

        while True:
            choice = input("Ваш выбор (1-2): ").strip()
            if choice == "1":
                print("\nВыбрана in-memory база данных.")
                return MemoryDatabase()
            elif choice == "2":
                print("\nВыбрана файловая база данных. Данные будут сохранены в папке 'data'.")
                return FileDatabase()
            else:
                print("Ошибка: введите 1 или 2.")

    def _init_students_table(self) -> None:
        columns = ("student_id", "first_name", "last_name", "age", "grade", "email")
        try:
            self.db.create_table("students", columns)
        except TableAlreadyExistsError:
            pass

    def _print_menu(self) -> None:
        print("\n" + "=" * 60)
        print("СИСТЕМА УПРАВЛЕНИЯ СТУДЕНТАМИ")
        print("=" * 60)
        print("1. Добавить студента")
        print("2. Показать всех студентов")
        print("3. Найти студентов по фильтру")
        print("4. Обновить информацию о студенте")
        print("5. Удалить студента")
        print("6. Сортировать студентов")
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
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _read_float(self, prompt: str) -> float:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                print("Ошибка: поле не может быть пустым.")
                continue
            try:
                return float(raw)
            except ValueError:
                print("Ошибка: введите число (например: 4.5).")

    def _read_optional_float(self, prompt: str) -> float | None:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return float(raw)
            except ValueError:
                print("Ошибка: введите число или оставьте поле пустым.")

    def _read_string(self, prompt: str, required: bool = True) -> str | None:
        while True:
            value = input(prompt).strip()
            if required and not value:
                print("Ошибка: поле не может быть пустым.")
                continue
            return value if value else None

    def _grade_to_text(self, grade: float) -> str:
        if grade >= 4.5:
            return "Отлично"
        elif grade >= 3.5:
            return "Хорошо"
        elif grade >= 2.5:
            return "Удовлетворительно"
        else:
            return "Неудовлетворительно"

    def _print_records(self, records: list[dict]) -> None:
        if not records:
            print("\nСтуденты не найдены.")
            return

        print("\n" + "=" * 110)
        print(f"{'ID':<5} {'Имя':<15} {'Фамилия':<15} {'Возраст':<8} {'Ср. балл':<10} {'Оценка':<15} {'Email':<30}")
        print("=" * 110)

        for record in records:
            email_display = record['email'][:27] + "..." if len(record['email']) > 30 else record['email']
            print(f"{record['student_id']:<5} {record['first_name']:<15} {record['last_name']:<15} {record['age']:<8} {record['grade']:<10.2f} {self._grade_to_text(record['grade']):<15} {email_display:<30}")
        print("=" * 110)
        print(f"Всего студентов: {len(records)}")

    def _get_next_id(self) -> int:
        records = self.db.get_all_records("students")
        if not records:
            return 1
        return max(r['student_id'] for r in records) + 1

    def _validate_name(self, name: str, field_name: str) -> str:
        if not name or not name.strip():
            raise InvalidNameError(f"{field_name} не может быть пустым.")
        if len(name.strip()) < 2:
            raise InvalidNameError(f"{field_name} должно содержать минимум 2 символа.")
        return name.strip().capitalize()

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

        email_clean = email.strip().lower()

        if "@" not in email_clean or "." not in email_clean:
            raise InvalidEmailError("Введите корректный email (должен содержать @ и .)")

        records = self.db.get_all_records("students")
        for record in records:
            if exclude_id is not None and record['student_id'] == exclude_id:
                continue
            if record['email'] == email_clean:
                raise DuplicateEmailError(f"Студент с email '{email}' уже существует.")

        return email_clean

    def _add_student(self) -> None:
        print("\nДОБАВЛЕНИЕ НОВОГО СТУДЕНТА")
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
            first_name_valid = self._validate_name(first_name, "Имя")
            last_name_valid = self._validate_name(last_name, "Фамилия")
            age_valid = self._validate_age(age)
            grade_valid = self._validate_grade(grade)
            email_valid = self._validate_email(email)

            student_id = self._get_next_id()

            record = {
                "student_id": student_id,
                "first_name": first_name_valid,
                "last_name": last_name_valid,
                "age": age_valid,
                "grade": grade_valid,
                "email": email_valid,
            }

            self.db.insert_record("students", record)

            print(f"\nСтудент успешно добавлен!")
            print(f"   ID: {student_id}")
            print(f"   {first_name_valid} {last_name_valid}, {age_valid} лет")
            print(f"   Средний балл: {grade_valid:.2f} ({self._grade_to_text(grade_valid)})")
            print(f"   Email: {email_valid}")
        except (InvalidNameError, InvalidAgeError, InvalidGradeError, InvalidEmailError, DuplicateEmailError) as exc:
            print(f"\nОшибка: {exc}")

    def _show_all_students(self) -> None:
        print("\nВСЕ СТУДЕНТЫ")
        try:
            records = self.db.get_all_records("students")
            self._print_records(records)
        except TableNotFoundError:
            print("\nТаблица студентов не найдена.")

    def _find_students_by_filter(self) -> None:
        print("\nПОИСК СТУДЕНТОВ")
        print("(оставьте поле пустым, чтобы пропустить фильтр)")
        print("-" * 40)

        student_id = self._read_optional_int("ID студента: ")
        first_name = self._read_string("Имя: ", required=False)
        last_name = self._read_string("Фамилия: ", required=False)
        age = self._read_optional_int("Возраст: ")
        grade = self._read_optional_float("Средний балл: ")
        email = self._read_string("Email: ", required=False)

        filters = {}
        if student_id is not None:
            filters["student_id"] = student_id
        if first_name is not None:
            filters["first_name"] = first_name.strip().capitalize()
        if last_name is not None:
            filters["last_name"] = last_name.strip().capitalize()
        if age is not None:
            filters["age"] = age
        if grade is not None:
            filters["grade"] = grade
        if email is not None:
            filters["email"] = email.strip().lower()

        try:
            records = self.db.select_records("students", **filters)
            self._print_records(records)
        except TableNotFoundError:
            print("\nТаблица студентов не найдена.")
        except UnknownColumnError as exc:
            print(f"\nОшибка: {exc}")

    def _update_student(self) -> None:
        print("\nОБНОВЛЕНИЕ ИНФОРМАЦИИ О СТУДЕНТЕ")
        print("-" * 40)

        student_id = self._read_int("Введите ID студента для обновления: ")

        try:
            existing = self.db.select_records("students", student_id=student_id)
            if not existing:
                print(f"\nСтудент с ID {student_id} не найден.")
                return

            print(f"\nТекущая информация:")
            print(f"   ID: {existing[0]['student_id']}")
            print(f"   Имя: {existing[0]['first_name']}")
            print(f"   Фамилия: {existing[0]['last_name']}")
            print(f"   Возраст: {existing[0]['age']} лет")
            print(f"   Средний балл: {existing[0]['grade']:.2f}")
            print(f"   Email: {existing[0]['email']}")

            print("\n(оставьте поле пустым, чтобы не менять)")
            print("-" * 40)

            first_name = self._read_string("Новое имя: ", required=False)
            last_name = self._read_string("Новая фамилия: ", required=False)
            age = self._read_optional_int("Новый возраст: ")
            grade = self._read_optional_float("Новый средний балл: ")
            email = self._read_string("Новый email: ", required=False)

            updates = {}
            if first_name is not None:
                updates["first_name"] = self._validate_name(first_name, "Имя")
            if last_name is not None:
                updates["last_name"] = self._validate_name(last_name, "Фамилия")
            if age is not None:
                updates["age"] = self._validate_age(age)
            if grade is not None:
                updates["grade"] = self._validate_grade(grade)
            if email is not None:
                updates["email"] = self._validate_email(email, student_id)

            if not updates:
                print("\nНи одно поле не было изменено. Обновление отменено.")
                return

            updated = self.db.update_record("students", student_id, "student_id", **updates)

            if updated:
                print(f"\nИнформация о студенте успешно обновлена!")
                print(f"   {updated['first_name']} {updated['last_name']}, {updated['age']} лет")
                print(f"   Средний балл: {updated['grade']:.2f} ({self._grade_to_text(updated['grade'])})")
                print(f"   Email: {updated['email']}")
            else:
                print(f"\nСтудент с ID {student_id} не найден.")
        except TableNotFoundError:
            print("\nТаблица студентов не найдена.")
        except (InvalidNameError, InvalidAgeError, InvalidGradeError, InvalidEmailError, DuplicateEmailError) as exc:
            print(f"\nОшибка: {exc}")

    def _delete_student(self) -> None:
        print("\nУДАЛЕНИЕ СТУДЕНТА")
        print("-" * 40)

        student_id = self._read_int("Введите ID студента для удаления: ")

        try:
            existing = self.db.select_records("students", student_id=student_id)
            if not existing:
                print(f"\nСтудент с ID {student_id} не найден.")
                return

            print(f"\nСтудент для удаления:")
            print(f"   {existing[0]['first_name']} {existing[0]['last_name']}, {existing[0]['age']} лет")
            print(f"   Средний балл: {existing[0]['grade']:.2f}")
            print(f"   Email: {existing[0]['email']}")

            confirm = input("\nВы уверены, что хотите удалить этого студента? (да/нет): ").strip().lower()

            if confirm in ("да", "yes", "y", "д"):
                deleted = self.db.delete_record("students", student_id, "student_id")
                if deleted:
                    print(f"\nСтудент успешно удалён: {deleted['first_name']} {deleted['last_name']}")
                else:
                    print(f"\nСтудент с ID {student_id} не найден.")
            else:
                print("\nУдаление отменено.")
        except TableNotFoundError:
            print("\nТаблица студентов не найдена.")

    def _sort_students(self) -> None:
        print("\nСОРТИРОВКА СТУДЕНТОВ")
        print("-" * 40)
        print("Выберите поле для сортировки:")
        print("1. ID")
        print("2. Имя")
        print("3. Фамилия")
        print("4. Возраст")
        print("5. Средний балл")
        print("6. Email")

        field_choice = self._read_int("Ваш выбор (1-6): ")

        field_map = {
            1: 'student_id',
            2: 'first_name',
            3: 'last_name',
            4: 'age',
            5: 'grade',
            6: 'email',
        }

        if field_choice not in field_map:
            print("\nНеверный выбор поля.")
            return

        field = field_map[field_choice]

        print("\nВыберите порядок сортировки:")
        print("1. По возрастанию")
        print("2. По убыванию")

        order_choice = self._read_int("Ваш выбор (1-2): ")

        if order_choice not in (1, 2):
            print("\nНеверный выбор порядка.")
            return

        reverse = (order_choice == 2)

        print("\nХотите применить фильтр перед сортировкой?")
        filter_choice = input("(да/нет): ").strip().lower()

        try:
            records = self.db.get_all_records("students")

            filter_params = None
            if filter_choice in ("да", "yes", "y", "д"):
                print("\nВведите фильтры (оставьте пустым для пропуска):")
                student_id = self._read_optional_int("ID: ")
                first_name = self._read_string("Имя: ", required=False)
                last_name = self._read_string("Фамилия: ", required=False)
                age = self._read_optional_int("Возраст: ")
                grade = self._read_optional_float("Средний балл: ")
                email = self._read_string("Email: ", required=False)

                records = self.db.get_all_records("students")

                if student_id is not None:
                    records = [r for r in records if r['student_id'] == student_id]
                if first_name is not None:
                    records = [r for r in records if r['first_name'].lower() == first_name.lower()]
                if last_name is not None:
                    records = [r for r in records if r['last_name'].lower() == last_name.lower()]
                if age is not None:
                    records = [r for r in records if r['age'] == age]
                if grade is not None:
                    records = [r for r in records if r['grade'] == grade]
                if email is not None:
                    records = [r for r in records if r['email'].lower() == email.lower()]

            def get_key(record):
                value = record[field]
                if isinstance(value, str):
                    return value.lower()
                return value

            sorted_records = sorted(records, key=get_key, reverse=reverse)

            print(f"\nОтсортированные студенты (по полю '{field}', {'по убыванию' if reverse else 'по возрастанию'}):")
            self._print_records(sorted_records)
        except TableNotFoundError:
            print("\nТаблица студентов не найдена.")
        except ValueError as exc:
            print(f"\nОшибка при сортировке: {exc}")

    def run(self) -> None:
        while True:
            try:
                self._print_menu()
                action = input("\nВыберите действие (0-6): ").strip()

                if action == "1":
                    self._add_student()
                elif action == "2":
                    self._show_all_students()
                elif action == "3":
                    self._find_students_by_filter()
                elif action == "4":
                    self._update_student()
                elif action == "5":
                    self._delete_student()
                elif action == "6":
                    self._sort_students()
                elif action == "0":
                    print("\nДо свидания! Спасибо за использование системы.")
                    break
                else:
                    print("\nНеизвестная команда. Пожалуйста, выберите действие от 0 до 6.")
            except KeyboardInterrupt:
                print("\n\nПрограмма прервана пользователем. До свидания!")
                break
            except Exception as exc:
                print(f"\nНепредвиденная ошибка: {exc}")
                import traceback
                traceback.print_exc()
                print("\nПопробуйте продолжить работу...")

            input("\nНажмите Enter для продолжения...")


def run() -> None:
    app = ConsoleInterface()
    app.run()


def main() -> None:
    run()