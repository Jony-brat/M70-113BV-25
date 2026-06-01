from .backend.memory import StudentTable
from .backend.errors import (
    InvalidAgeError,
    InvalidGradeError,
    InvalidNameError,
    InvalidEmailError,
    DuplicateEmailError,
    RecordNotFoundError,
)


class ConsoleInterface:
    def __init__(self) -> None:
        self.db = StudentTable()

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

    def _print_records(self, records: list) -> None:
        if not records:
            print("\nСтуденты не найдены.")
            return

        print("\n" + "=" * 110)
        print(f"{'ID':<5} {'Имя':<15} {'Фамилия':<15} {'Возраст':<8} {'Ср. балл':<10} {'Оценка':<15} {'Email':<30}")
        print("=" * 110)

        for record in records:
            email_display = record[5][:27] + "..." if len(record[5]) > 30 else record[5]
            print(f"{record[0]:<5} {record[1]:<15} {record[2]:<15} {record[3]:<8} {record[4]:<10.2f} {self._grade_to_text(record[4]):<15} {email_display:<30}")
        print("=" * 110)
        print(f"Всего студентов: {len(records)}")

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
            record = self.db.create_record(first_name, last_name, age, grade, email)
            print("\nСтудент успешно добавлен!")
            print(f"   ID: {record[0]}")
            print(f"   {record[1]} {record[2]}, {record[3]} лет")
            print(f"   Средний балл: {record[4]:.2f} ({self._grade_to_text(record[4])})")
            print(f"   Email: {record[5]}")
        except (InvalidNameError, InvalidAgeError, InvalidGradeError, InvalidEmailError, DuplicateEmailError) as exc:
            print(f"\nОшибка: {exc}")

    def _show_all_students(self) -> None:
        print("\nВСЕ СТУДЕНТЫ")
        self._print_records(self.db.get_all_records())

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

        records = self.db.select_record(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            grade=grade,
            email=email,
        )

        self._print_records(records)

    def _update_student(self) -> None:
        print("\nОБНОВЛЕНИЕ ИНФОРМАЦИИ О СТУДЕНТЕ")
        print("-" * 40)

        try:
            student_id = self._read_int("Введите ID студента для обновления: ")
            existing = self.db.select_record(student_id=student_id)
            if not existing:
                print(f"\nСтудент с ID {student_id} не найден.")
                return

            print(f"\nТекущая информация:")
            print(f"   ID: {existing[0][0]}")
            print(f"   Имя: {existing[0][1]}")
            print(f"   Фамилия: {existing[0][2]}")
            print(f"   Возраст: {existing[0][3]} лет")
            print(f"   Средний балл: {existing[0][4]:.2f}")
            print(f"   Email: {existing[0][5]}")

            print("\n(оставьте поле пустым, чтобы не менять)")
            print("-" * 40)

            first_name = self._read_string("Новое имя: ", required=False)
            last_name = self._read_string("Новая фамилия: ", required=False)
            age = self._read_optional_int("Новый возраст: ")
            grade = self._read_optional_float("Новый средний балл: ")
            email = self._read_string("Новый email: ", required=False)

            if all(param is None for param in [first_name, last_name, age, grade, email]):
                print("\nНи одно поле не было изменено. Обновление отменено.")
                return

            updated = self.db.update_record(
                student_id, 
                first_name, 
                last_name, 
                age, 
                grade, 
                email
            )
            print("\nИнформация о студенте успешно обновлена!")
            print(f"   {updated[1]} {updated[2]}, {updated[3]} лет")
            print(f"   Средний балл: {updated[4]:.2f} ({self._grade_to_text(updated[4])})")
            print(f"   Email: {updated[5]}")
            
        except (InvalidNameError, InvalidAgeError, InvalidGradeError, 
                InvalidEmailError, DuplicateEmailError) as exc:
            print(f"\nОшибка валидации: {exc}")
        except RecordNotFoundError as exc:
            print(f"\n{exc}")
        except ValueError as exc:
            print(f"\nОшибка ввода данных: {exc}")
        except Exception as exc:
            print(f"\nНепредвиденная ошибка при обновлении: {exc}")
            import traceback
            traceback.print_exc()

    def _delete_student(self) -> None:
        print("\nУДАЛЕНИЕ СТУДЕНТА")
        print("-" * 40)

        try:
            student_id = self._read_int("Введите ID студента для удаления: ")
            existing = self.db.select_record(student_id=student_id)
            if not existing:
                print(f"\nСтудент с ID {student_id} не найден.")
                return

            print(f"\nСтудент для удаления:")
            print(f"   {existing[0][1]} {existing[0][2]}, {existing[0][3]} лет")
            print(f"   Средний балл: {existing[0][4]:.2f}")
            print(f"   Email: {existing[0][5]}")

            confirm = input("\nВы уверены, что хотите удалить этого студента? (да/нет): ").strip().lower()

            if confirm in ("да", "yes", "y", "д"):
                deleted = self.db.delete_record(student_id)
                print(f"\nСтудент успешно удалён: {deleted[1]} {deleted[2]}")
            else:
                print("\nУдаление отменено.")
                
        except RecordNotFoundError as exc:
            print(f"\n{exc}")
        except Exception as exc:
            print(f"\nНепредвиденная ошибка при удалении: {exc}")
            import traceback
            traceback.print_exc()

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
            1: 'id',
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
        
        filter_params = None
        if filter_choice in ("да", "yes", "y", "д"):
            print("\nВведите фильтры (оставьте пустым для пропуска):")
            student_id = self._read_optional_int("ID: ")
            first_name = self._read_string("Имя: ", required=False)
            last_name = self._read_string("Фамилия: ", required=False)
            age = self._read_optional_int("Возраст: ")
            grade = self._read_optional_float("Средний балл: ")
            email = self._read_string("Email: ", required=False)
            
            filter_params = {
                k: v for k, v in {
                    'student_id': student_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'age': age,
                    'grade': grade,
                    'email': email,
                }.items() if v is not None
            }

        try:
            sorted_records = self.db.sort_records(field, reverse, filter_params)
            print(f"\nОтсортированные студенты (по полю '{field}', {'по убыванию' if reverse else 'по возрастанию'}):")
            self._print_records(sorted_records)
        except ValueError as exc:
            print(f"\nОшибка при сортировке: {exc}")
        except Exception as exc:
            print(f"\nНепредвиденная ошибка при сортировке: {exc}")
            import traceback
            traceback.print_exc()

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