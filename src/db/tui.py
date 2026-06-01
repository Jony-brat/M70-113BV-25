from .backend.database import Database
from .backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    RecordNotFoundError,
    InvalidNameError,
    InvalidAgeError,
    InvalidGradeError,
    InvalidEmailError,
    DuplicateEmailError,
)


class ConsoleInterface:
    
    def __init__(self):
        self.db = Database()
        self.current_table = None
        self._init_sample_tables()
    
    def _init_sample_tables(self):
        if not self.db.table_exists("students"):
            self.db.create_table("students")
            try:
                self.db.insert_record("students",
                    first_name="Иван",
                    last_name="Петров",
                    age=20,
                    grade=4.7,
                    email="ivan@example.com"
                )
                self.db.insert_record("students",
                    first_name="Мария",
                    last_name="Иванова",
                    age=22,
                    grade=4.2,
                    email="maria@example.com"
                )
            except:
                pass
        
        if not self.db.table_exists("teachers"):
            self.db.create_table("teachers")
    
    def _print_main_menu(self):
        print("\n" + "=" * 60)
        print("          СИСТЕМА УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ")
        print("=" * 60)
        print("1. Управление таблицами")
        print("2. Работа с данными")
        print("3. Показать информацию")
        print("0. Выход")
        print("-" * 60)
    
    def _print_table_menu(self):
        print("\n" + "=" * 60)
        print("          УПРАВЛЕНИЕ ТАБЛИЦАМИ")
        print("=" * 60)
        print("1. Создать таблицу")
        print("2. Удалить таблицу")
        print("3. Выбрать таблицу для работы")
        print("4. Показать все таблицы")
        print("0. Назад")
        print("-" * 60)
    
    def _print_data_menu(self):
        print("\n" + "=" * 60)
        print("          РАБОТА С ДАННЫМИ")
        print("=" * 60)
        if self.current_table:
            print(f"Текущая таблица: {self.current_table}")
        else:
            print("Таблица не выбрана")
        print("-" * 60)
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("0. Назад")
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
    
    def _grade_to_text(self, grade: float) -> str:
        if grade >= 4.5:
            return "Отлично"
        elif grade >= 3.5:
            return "Хорошо"
        elif grade >= 2.5:
            return "Удовлетворительно"
        return "Неудовлетворительно"
    
    def _print_records(self, records: list[dict]):
        if not records:
            print("\nЗаписи не найдены.")
            return
        
        print("\n" + "=" * 120)
        print(f"{'ID':<5} {'Имя':<15} {'Фамилия':<15} {'Возраст':<8} {'Ср.балл':<10} {'Оценка':<15} {'Email':<35}")
        print("=" * 120)
        
        for record in records:
            email = record.get('email', '')[:32] + "..." if len(record.get('email', '')) > 35 else record.get('email', '')
            grade = record.get('grade', 0)
            print(f"{record.get('id', '?'):<5} {record.get('first_name', ''):<15} {record.get('last_name', ''):<15} "
                  f"{record.get('age', '?'):<8} {grade:<10.2f} {self._grade_to_text(grade):<15} {email:<35}")
        print("=" * 120)
        print(f"Всего записей: {len(records)}")
    
    def _manage_tables(self):
        while True:
            self._print_table_menu()
            choice = input("\nВыберите действие (0-4): ").strip()
            
            if choice == "1":
                self._create_table()
            elif choice == "2":
                self._drop_table()
            elif choice == "3":
                self._select_table()
            elif choice == "4":
                self._list_tables()
            elif choice == "0":
                break
            else:
                print("\nНеизвестная команда.")
            
            input("\nНажмите Enter для продолжения...")
    
    def _create_table(self):
        print("\nСОЗДАНИЕ ТАБЛИЦЫ")
        print("-" * 40)
        
        table_name = self._read_string("Имя таблицы: ")
        if not table_name:
            return
        
        try:
            self.db.create_table(table_name)
            print(f"\nТаблица '{table_name}' успешно создана!")
        except TableAlreadyExistsError as e:
            print(f"\nОшибка: {e}")
    
    def _drop_table(self):
        print("\nУДАЛЕНИЕ ТАБЛИЦЫ")
        print("-" * 40)
        
        table_name = self._read_string("Имя таблицы для удаления: ")
        if not table_name:
            return
        
        try:
            self.db.drop_table(table_name)
            if self.current_table == table_name:
                self.current_table = None
            print(f"\nТаблица '{table_name}' успешно удалена!")
        except TableNotFoundError as e:
            print(f"\nОшибка: {e}")
    
    def _select_table(self):
        print("\nВЫБОР ТАБЛИЦЫ")
        print("-" * 40)
        
        tables = self.db.list_tables()
        if not tables:
            print("\nНет доступных таблиц. Сначала создайте таблицу.")
            return
        
        print("\nДоступные таблицы:")
        for i, name in enumerate(tables, 1):
            print(f"   {i}. {name}")
        
        try:
            choice = self._read_int("Выберите таблицу (номер): ")
            if 1 <= choice <= len(tables):
                self.current_table = tables[choice - 1]
                print(f"\nТекущая таблица: {self.current_table}")
            else:
                print("\nНеверный номер.")
        except ValueError:
            print("\nОшибка ввода.")
    
    def _list_tables(self):
        print("\nСПИСОК ТАБЛИЦ")
        print("-" * 40)
        
        tables = self.db.list_tables()
        if not tables:
            print("Нет созданных таблиц.")
            return
        
        for name in tables:
            count = self.db.count_records(name)
            print(f"   {name} (записей: {count})")
    
    def _add_record(self):
        if not self.current_table:
            print("\nСначала выберите таблицу (меню 1 -> 3)")
            return
        
        print(f"\nДОБАВЛЕНИЕ ЗАПИСИ В ТАБЛИЦУ '{self.current_table}'")
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
            record = self.db.insert_record(
                self.current_table,
                first_name=first_name,
                last_name=last_name,
                age=age,
                grade=grade,
                email=email
            )
            print(f"\nЗапись успешно добавлена! ID: {record['id']}")
        except (InvalidNameError, InvalidAgeError, InvalidGradeError, InvalidEmailError, DuplicateEmailError) as e:
            print(f"\nОшибка: {e}")
    
    def _show_all_records(self):
        if not self.current_table:
            print("\nСначала выберите таблицу (меню 1 -> 3)")
            return
        
        print(f"\nВСЕ ЗАПИСИ ТАБЛИЦЫ '{self.current_table}'")
        
        try:
            records = self.db.get_all_records(self.current_table)
            self._print_records(records)
        except TableNotFoundError as e:
            print(f"\nОшибка: {e}")
    
    def _find_records(self):
        if not self.current_table:
            print("\nСначала выберите таблицу (меню 1 -> 3)")
            return
        
        print(f"\nПОИСК ЗАПИСЕЙ В ТАБЛИЦЕ '{self.current_table}'")
        print("(оставьте поле пустым для пропуска)")
        print("-" * 40)
        
        filters = {}
        
        student_id = self._read_optional_int("ID: ")
        if student_id is not None:
            filters['id'] = student_id
        
        first_name = self._read_string("Имя: ", required=False)
        if first_name:
            filters['first_name'] = first_name
        
        last_name = self._read_string("Фамилия: ", required=False)
        if last_name:
            filters['last_name'] = last_name
        
        age = self._read_optional_int("Возраст: ")
        if age is not None:
            filters['age'] = age
        
        grade = self._read_optional_float("Средний балл: ")
        if grade is not None:
            filters['grade'] = grade
        
        email = self._read_string("Email: ", required=False)
        if email:
            filters['email'] = email
        
        try:
            records = self.db.select_records(self.current_table, **filters)
            self._print_records(records)
        except TableNotFoundError as e:
            print(f"\nОшибка: {e}")
    
    def _update_record(self):
        if not self.current_table:
            print("\nСначала выберите таблицу (меню 1 -> 3)")
            return
        
        print(f"\nОБНОВЛЕНИЕ ЗАПИСИ В ТАБЛИЦЕ '{self.current_table}'")
        print("-" * 40)
        
        record_id = self._read_int("ID записи: ")
        
        try:
            existing = self.db.select_records(self.current_table, id=record_id)
            if not existing:
                print(f"\nЗапись с ID {record_id} не найдена.")
                return
            
            print(f"\nТекущая информация:")
            print(f"   {existing[0]['first_name']} {existing[0]['last_name']}, {existing[0]['age']} лет")
            print(f"   Средний балл: {existing[0]['grade']:.2f}")
            print(f"   Email: {existing[0]['email']}")
            
            print("\n(оставьте поле пустым для пропуска)")
            print("-" * 40)
            
            updates = {}
            
            first_name = self._read_string("Новое имя: ", required=False)
            if first_name:
                updates['first_name'] = first_name
            
            last_name = self._read_string("Новая фамилия: ", required=False)
            if last_name:
                updates['last_name'] = last_name
            
            age = self._read_optional_int("Новый возраст: ")
            if age is not None:
                updates['age'] = age
            
            grade = self._read_optional_float("Новый средний балл: ")
            if grade is not None:
                updates['grade'] = grade
            
            email = self._read_string("Новый email: ", required=False)
            if email:
                updates['email'] = email
            
            if updates:
                updated = self.db.update_record(self.current_table, record_id, **updates)
                print(f"\nЗапись успешно обновлена!")
            else:
                print("\nНет изменений.")
                
        except (TableNotFoundError, RecordNotFoundError, InvalidNameError,
                InvalidAgeError, InvalidGradeError, InvalidEmailError, DuplicateEmailError) as e:
            print(f"\nОшибка: {e}")
    
    def _delete_record(self):
        if not self.current_table:
            print("\nСначала выберите таблицу (меню 1 -> 3)")
            return
        
        print(f"\nУДАЛЕНИЕ ЗАПИСИ ИЗ ТАБЛИЦЫ '{self.current_table}'")
        print("-" * 40)
        
        record_id = self._read_int("ID записи: ")
        
        try:
            existing = self.db.select_records(self.current_table, id=record_id)
            if not existing:
                print(f"\nЗапись с ID {record_id} не найдена.")
                return
            
            print(f"\nЗапись для удаления:")
            print(f"   {existing[0]['first_name']} {existing[0]['last_name']}, {existing[0]['age']} лет")
            print(f"   Средний балл: {existing[0]['grade']:.2f}")
            print(f"   Email: {existing[0]['email']}")
            
            confirm = input("\nВы уверены? (да/нет): ").strip().lower()
            
            if confirm in ("да", "yes", "y", "д"):
                deleted = self.db.delete_record(self.current_table, record_id)
                print(f"\nЗапись успешно удалена: {deleted['first_name']} {deleted['last_name']}")
            else:
                print("\nУдаление отменено.")
                
        except (TableNotFoundError, RecordNotFoundError) as e:
            print(f"\nОшибка: {e}")
    
    def _work_with_data(self):
        if not self.current_table:
            print("\nСначала выберите таблицу (меню 1 -> 3)")
            input("\nНажмите Enter для продолжения...")
            return
        
        while True:
            self._print_data_menu()
            choice = input("\nВыберите действие (0-5): ").strip()
            
            if choice == "1":
                self._add_record()
            elif choice == "2":
                self._show_all_records()
            elif choice == "3":
                self._find_records()
            elif choice == "4":
                self._update_record()
            elif choice == "5":
                self._delete_record()
            elif choice == "0":
                break
            else:
                print("\nНеизвестная команда.")
            
            input("\nНажмите Enter для продолжения...")
    
    def _show_info(self):
        print("\n" + "=" * 60)
        print("          ИНФОРМАЦИЯ О СИСТЕМЕ")
        print("=" * 60)
        print(f"Всего таблиц: {len(self.db.list_tables())}")
        
        if self.current_table:
            count = self.db.count_records(self.current_table)
            print(f"Текущая таблица: {self.current_table} (записей: {count})")
        else:
            print("Таблица не выбрана")
        
        print("\nДоступные таблицы:")
        for name in self.db.list_tables():
            count = self.db.count_records(name)
            print(f"   {name} (записей: {count})")
        print("=" * 60)
    
    def run(self):
        print("\n" + "=" * 60)
        print("ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ")
        print("=" * 60)
        print("\nСистема поддерживает несколько таблиц.")
        print("   Сначала создайте таблицу (меню 1 -> 1)")
        print("   Затем выберите её для работы (меню 1 -> 3)")
        print("   После этого работайте с данными (меню 2)")
        
        while True:
            self._print_main_menu()
            action = input("\nВыберите действие (0-3): ").strip()
            
            if action == "1":
                self._manage_tables()
            elif action == "2":
                self._work_with_data()
            elif action == "3":
                self._show_info()
            elif action == "0":
                print("\nДо свидания!")
                break
            else:
                print("\nНеизвестная команда.")
            
            input("\nНажмите Enter для продолжения...")


def run() -> None:
    app = ConsoleInterface()
    app.run()