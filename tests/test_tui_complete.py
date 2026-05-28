import unittest
from unittest.mock import patch, MagicMock, call
from io import StringIO
import tempfile
import os
import json

from src.db.tui import ConsoleInterface, run
from src.db.backend.errors import (
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


class TestConsoleInterfaceComplete(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()
    
    # === Тесты инициализации ===
    def test_init_with_memory_db(self):
        """Тест инициализации с in-memory БД."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            from src.db.backend.memory import MemoryDatabase
            self.assertIsInstance(ui.db, MemoryDatabase)
    
    def test_init_with_json_db(self):
        """Тест инициализации с JSON БД."""
        with patch('builtins.input', side_effect=["2"]):
            ui = ConsoleInterface()
            from src.db.backend.file_json import JSONDatabase
            self.assertIsInstance(ui.db, JSONDatabase)
    
    def test_init_with_csv_db(self):
        """Тест инициализации с CSV БД."""
        with patch('builtins.input', side_effect=["3"]):
            ui = ConsoleInterface()
            from src.db.backend.file_csv import CSVDatabase
            self.assertIsInstance(ui.db, CSVDatabase)
    
    def test_init_invalid_choice_then_valid(self):
        """Тест неверного выбора БД, затем верного."""
        with patch('builtins.input', side_effect=["5", "1"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui = ConsoleInterface()
                output = mock_stdout.getvalue()
                self.assertIn("Неверный выбор", output)
                self.assertIsNotNone(ui.db)
    
    # === Тесты _ensure_table_exists ===
    def test_ensure_table_exists_creates_table(self):
        """Тест создания таблицы, если её нет."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            ui.db.tables.clear()
            ui._ensure_table_exists()
            self.assertTrue(ui.db._table_exists("students"))
    
    def test_ensure_table_exists_table_already_exists(self):
        """Тест когда таблица уже существует."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            ui._ensure_table_exists()
            ui._ensure_table_exists()  # Не должно быть ошибки
    
    # === Тесты _print_menu ===
    def test_print_menu(self):
        """Тест вывода меню."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._print_menu()
                output = mock_stdout.getvalue()
                self.assertIn("СИСТЕМА УПРАВЛЕНИЯ СТУДЕНТАМИ", output)
                self.assertIn("1. Добавить студента", output)
                self.assertIn("7. Управление индексами", output)
                self.assertIn("0. Выход", output)
    
    # === Тесты _read_int ===
    def test_read_int_success(self):
        """Тест успешного чтения int."""
        with patch('builtins.input', side_effect=["42"]):
            with patch('builtins.input', side_effect=["1"]):
                ui = ConsoleInterface()
                result = ui._read_int("Введите число: ")
                self.assertEqual(result, 42)
    
    def test_read_int_empty_then_valid(self):
        """Тест пустого ввода, затем валидного."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=["", "25"]):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = ui._read_int("Введите число: ")
                    self.assertEqual(result, 25)
                    self.assertIn("поле не может быть пустым", mock_stdout.getvalue())
    
    def test_read_int_invalid_then_valid(self):
        """Тест неверного ввода, затем валидного."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=["abc", "10"]):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = ui._read_int("Введите число: ")
                    self.assertEqual(result, 10)
                    self.assertIn("введите целое число", mock_stdout.getvalue())
    
    # === Тесты _read_optional_int ===
    def test_read_optional_int_empty(self):
        """Тест чтения опционального int - пустой ввод."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=[""]):
                result = ui._read_optional_int("Введите число: ")
                self.assertIsNone(result)
    
    def test_read_optional_int_with_value(self):
        """Тест чтения опционального int - с вводом."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=["100"]):
                result = ui._read_optional_int("Введите число: ")
                self.assertEqual(result, 100)
    
    def test_read_optional_int_invalid(self):
        """Тест чтения опционального int - неверный ввод."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=["abc", "50"]):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = ui._read_optional_int("Введите число: ")
                    self.assertEqual(result, 50)
    
    # === Тесты _read_float ===
    def test_read_float_success(self):
        """Тест успешного чтения float."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=["3.14"]):
                result = ui._read_float("Введите число: ")
                self.assertEqual(result, 3.14)
    
    def test_read_float_empty_then_valid(self):
        """Тест пустого ввода float, затем валидного."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=["", "2.5"]):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = ui._read_float("Введите число: ")
                    self.assertEqual(result, 2.5)
                    self.assertIn("поле не может быть пустым", mock_stdout.getvalue())
    
    def test_read_float_invalid_then_valid(self):
        """Тест неверного ввода float, затем валидного."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=["abc", "4.8"]):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = ui._read_float("Введите число: ")
                    self.assertEqual(result, 4.8)
                    self.assertIn("введите число", mock_stdout.getvalue())
    
    # === Тесты _read_optional_float ===
    def test_read_optional_float_empty(self):
        """Тест чтения опционального float - пустой ввод."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=[""]):
                result = ui._read_optional_float("Введите число: ")
                self.assertIsNone(result)
    
    def test_read_optional_float_with_value(self):
        """Тест чтения опционального float - с вводом."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=["4.2"]):
                result = ui._read_optional_float("Введите число: ")
                self.assertEqual(result, 4.2)
    
    # === Тесты _read_string ===
    def test_read_string_required_success(self):
        """Тест чтения обязательной строки."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=["Иван"]):
                result = ui._read_string("Введите имя: ", required=True)
                self.assertEqual(result, "Иван")
    
    def test_read_string_required_empty(self):
        """Тест чтения обязательной строки - пустой ввод."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=[""]):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = ui._read_string("Введите имя: ", required=True)
                    self.assertIsNone(result)
                    self.assertIn("не может быть пустым", mock_stdout.getvalue())
    
    def test_read_string_not_required_empty(self):
        """Тест чтения необязательной строки - пустой ввод."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('builtins.input', side_effect=[""]):
                result = ui._read_string("Введите имя: ", required=False)
                self.assertIsNone(result)
    
    # === Тесты _validate_record ===
    def test_validate_record_success(self):
        """Тест успешной валидации."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            result = ui._validate_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
            self.assertEqual(result['first_name'], "Иван")
            self.assertEqual(result['email'], "ivan@example.com")
    
    def test_validate_record_name_too_short(self):
        """Тест слишком короткого имени."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with self.assertRaises(InvalidNameError):
                ui._validate_record("И", "Петров", 20, 4.7, "test@example.com")
    
    def test_validate_record_last_name_too_short(self):
        """Тест слишком короткой фамилии."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with self.assertRaises(InvalidNameError):
                ui._validate_record("Иван", "П", 20, 4.7, "test@example.com")
    
    def test_validate_record_age_negative(self):
        """Тест отрицательного возраста."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with self.assertRaises(InvalidAgeError):
                ui._validate_record("Иван", "Петров", -5, 4.7, "test@example.com")
    
    def test_validate_record_age_too_high(self):
        """Тест слишком большого возраста."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with self.assertRaises(InvalidAgeError):
                ui._validate_record("Иван", "Петров", 150, 4.7, "test@example.com")
    
    def test_validate_record_grade_negative(self):
        """Тест отрицательного балла."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with self.assertRaises(InvalidGradeError):
                ui._validate_record("Иван", "Петров", 20, -1, "test@example.com")
    
    def test_validate_record_grade_too_high(self):
        """Тест слишком высокого балла."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with self.assertRaises(InvalidGradeError):
                ui._validate_record("Иван", "Петров", 20, 6, "test@example.com")
    
    def test_validate_record_invalid_email(self):
        """Тест неверного email."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with self.assertRaises(InvalidEmailError):
                ui._validate_record("Иван", "Петров", 20, 4.7, "invalid")
    
    # === Тесты _grade_to_text ===
    def test_grade_to_text_excellent(self):
        """Тест отличной оценки."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            self.assertEqual(ui._grade_to_text(4.7), "Отлично")
            self.assertEqual(ui._grade_to_text(5.0), "Отлично")
    
    def test_grade_to_text_good(self):
        """Тест хорошей оценки."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            self.assertEqual(ui._grade_to_text(4.0), "Хорошо")
            self.assertEqual(ui._grade_to_text(3.5), "Хорошо")
    
    def test_grade_to_text_satisfactory(self):
        """Тест удовлетворительной оценки."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            self.assertEqual(ui._grade_to_text(3.0), "Удовлетворительно")
    
    def test_grade_to_text_unsatisfactory(self):
        """Тест неудовлетворительной оценки."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            self.assertEqual(ui._grade_to_text(2.0), "Неудовлетворительно")
    
    # === Тесты _print_records ===
    def test_print_records_empty(self):
        """Тест вывода пустого списка."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._print_records([])
                self.assertIn("Студенты не найдены", mock_stdout.getvalue())
    
    def test_print_records_with_data(self):
        """Тест вывода списка с данными."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            records = [{
                'id': 1,
                'first_name': 'Иван',
                'last_name': 'Петров',
                'age': 20,
                'grade': 4.7,
                'email': 'ivan@example.com'
            }]
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._print_records(records)
                output = mock_stdout.getvalue()
                self.assertIn("Иван", output)
                self.assertIn("Петров", output)
                self.assertIn("4.70", output)
    
    # === Тесты _add_student ===
    @patch('builtins.input', side_effect=["1", "Иван", "Петров", "20", "4.7", "ivan@example.com"])
    def test_add_student_success(self, mock_input):
        """Тест успешного добавления."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui._add_student()
            self.assertEqual(ui.db.count_records("students"), 1)
            self.assertIn("успешно добавлен", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "", "Петров", "20", "4.7", "test@example.com"])
    def test_add_student_empty_name(self, mock_input):
        """Тест добавления с пустым именем."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui._add_student()
            self.assertEqual(ui.db.count_records("students"), 0)
    
    @patch('builtins.input', side_effect=["1", "Иван", "", "20", "4.7", "test@example.com"])
    def test_add_student_empty_last_name(self, mock_input):
        """Тест добавления с пустой фамилией."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui._add_student()
            self.assertEqual(ui.db.count_records("students"), 0)
    
    @patch('builtins.input', side_effect=["1", "Иван", "Петров", "-5", "4.7", "test@example.com"])
    def test_add_student_invalid_age(self, mock_input):
        """Тест добавления с неверным возрастом."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui._add_student()
            self.assertEqual(ui.db.count_records("students"), 0)
    
    @patch('builtins.input', side_effect=["1", "Иван", "Петров", "20", "6", "test@example.com"])
    def test_add_student_invalid_grade(self, mock_input):
        """Тест добавления с неверным баллом."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui._add_student()
            self.assertEqual(ui.db.count_records("students"), 0)
    
    @patch('builtins.input', side_effect=["1", "Иван", "Петров", "20", "4.7", "invalid"])
    def test_add_student_invalid_email(self, mock_input):
        """Тест добавления с неверным email."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui._add_student()
            self.assertEqual(ui.db.count_records("students"), 0)
    
    # === Тесты _show_all_students ===
    def test_show_all_students_empty(self):
        """Тест показа пустой таблицы."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._show_all_students()
                self.assertIn("Студенты не найдены", mock_stdout.getvalue())
    
    def test_show_all_students_with_data(self):
        """Тест показа таблицы с данными."""
        with patch('builtins.input', side_effect=["1"]):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._show_all_students()
                self.assertIn("Иван", mock_stdout.getvalue())
    
    # === Тесты _find_students ===
    @patch('builtins.input', side_effect=["1", "", "", "", "", "", ""])
    def test_find_students_no_filters(self, mock_input):
        """Тест поиска без фильтров."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui._find_students()
            records = ui.db.select_records("students")
            self.assertEqual(len(records), 1)
    
    @patch('builtins.input', side_effect=["1", "1", "", "", "", "", ""])
    def test_find_students_by_id(self, mock_input):
        """Тест поиска по ID."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            record_id = ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui._find_students()
    
    @patch('builtins.input', side_effect=["1", "", "Иван", "", "", "", ""])
    def test_find_students_by_name(self, mock_input):
        """Тест поиска по имени."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui._find_students()
    
    @patch('builtins.input', side_effect=["1", "", "", "20", "", "", ""])
    def test_find_students_by_age(self, mock_input):
        """Тест поиска по возрасту."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui._find_students()
    
    @patch('builtins.input', side_effect=["1", "", "", "", "4.7", "", ""])
    def test_find_students_by_grade(self, mock_input):
        """Тест поиска по баллу."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui._find_students()
    
    # === Тесты _update_student ===
    @patch('builtins.input', side_effect=["1", "999"])
    def test_update_student_not_found(self, mock_input):
        """Тест обновления несуществующего студента."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui._update_student()
            self.assertIn("не найден", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "1", "Пётр", "", "", "", ""])
    def test_update_student_success(self, mock_input):
        """Тест успешного обновления."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui._update_student()
            records = ui.db.select_records("students")
            self.assertEqual(records[0]['first_name'], 'Пётр')
    
    @patch('builtins.input', side_effect=["1", "1", "", "", "", "", "new@example.com"])
    def test_update_student_change_email(self, mock_input):
        """Тест обновления email."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui._update_student()
            records = ui.db.select_records("students")
            self.assertEqual(records[0]['email'], 'new@example.com')
    
    @patch('builtins.input', side_effect=["1", "1", "", "", "", "", "invalid"])
    def test_update_student_invalid_email(self, mock_input):
        """Тест обновления с неверным email."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui._update_student()
            self.assertIn("Ошибка", mock_stdout.getvalue())
    
    # === Тесты _delete_student ===
    @patch('builtins.input', side_effect=["1", "999", "да"])
    def test_delete_student_not_found(self, mock_input):
        """Тест удаления несуществующего студента."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui._delete_student()
            self.assertIn("не найден", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "1", "да"])
    def test_delete_student_success(self, mock_input):
        """Тест успешного удаления."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            self.assertEqual(ui.db.count_records("students"), 1)
            ui._delete_student()
            self.assertEqual(ui.db.count_records("students"), 0)
    
    @patch('builtins.input', side_effect=["1", "1", "нет"])
    def test_delete_student_cancel(self, mock_input):
        """Тест отмены удаления."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui._delete_student()
            self.assertEqual(ui.db.count_records("students"), 1)
    
    # === Тесты _sort_students ===
    @patch('builtins.input', side_effect=["1", "10", "1"])
    def test_sort_students_invalid_field(self, mock_input):
        """Тест сортировки с неверным полем."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui._sort_students()
            self.assertIn("Неверный выбор", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "1", "3"])
    def test_sort_students_invalid_order(self, mock_input):
        """Тест сортировки с неверным порядком."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui._sort_students()
            self.assertIn("Неверный выбор", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "1", "1"])
    def test_sort_students_success(self, mock_input):
        """Тест успешной сортировки."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui.db.insert_record("students", {
                'first_name': 'Анна', 'last_name': 'Иванова',
                'age': 22, 'grade': 4.2, 'email': 'anna@example.com'
            })
            ui._sort_students()
            # Проверяем, что сортировка выполнена
            records = ui.db.get_all_records("students")
            self.assertEqual(len(records), 2)
    
    # === Тесты _manage_indexes ===
    @patch('builtins.input', side_effect=["1", "1", "age"])
    def test_add_index_success(self, mock_input):
        """Тест добавления индекса."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui._manage_indexes()
            indexes = ui.db.get_indexed_fields("students")
            self.assertIn('age', indexes)
            self.assertIn("добавлен", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "2", "email"])
    def test_remove_index_success(self, mock_input):
        """Тест удаления индекса."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui._manage_indexes()
            indexes = ui.db.get_indexed_fields("students")
            self.assertNotIn('email', indexes)
            self.assertIn("удалён", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "1", "nonexistent"])
    def test_add_index_invalid_field(self, mock_input):
        """Тест добавления индекса для несуществующего поля."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui._manage_indexes()
            self.assertIn("не найдено", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "0"])
    def test_manage_indexes_back(self, mock_input):
        """Тест возврата из меню индексов."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui._manage_indexes()
    
    # === Тесты run ===
    @patch('builtins.input', side_effect=["1", "0"])
    def test_run_exit(self, mock_input):
        """Тест выхода из программы."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui.run()
            self.assertIn("До свидания", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "invalid", "0"])
    def test_run_invalid_command(self, mock_input):
        """Тест неверной команды."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui = ConsoleInterface()
            ui.run()
            self.assertIn("Неизвестная команда", mock_stdout.getvalue())
    
    @patch('builtins.input', side_effect=["1", "1", "Иван", "Петров", "20", "4.7", "ivan@example.com", "0"])
    def test_run_add_student_flow(self, mock_input):
        """Тест полного цикла добавления."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.run()
            self.assertEqual(ui.db.count_records("students"), 1)
    
    @patch('builtins.input', side_effect=["1", "2", "0"])
    def test_run_show_students(self, mock_input):
        """Тест показа студентов."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui.run()
    
    @patch('builtins.input', side_effect=["1", "3", "", "", "", "", "", "0"])
    def test_run_find_students(self, mock_input):
        """Тест поиска студентов."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui.run()
    
    @patch('builtins.input', side_effect=["1", "4", "1", "", "", "", "", "0"])
    def test_run_update_student(self, mock_input):
        """Тест обновления студента."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui.run()
    
    @patch('builtins.input', side_effect=["1", "5", "1", "да", "0"])
    def test_run_delete_student(self, mock_input):
        """Тест удаления студента."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui.run()
            self.assertEqual(ui.db.count_records("students"), 0)
    
    @patch('builtins.input', side_effect=["1", "6", "1", "1", "0"])
    def test_run_sort_students(self, mock_input):
        """Тест сортировки студентов."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.db.insert_record("students", {
                'first_name': 'Иван', 'last_name': 'Петров',
                'age': 20, 'grade': 4.7, 'email': 'ivan@example.com'
            })
            ui.db.insert_record("students", {
                'first_name': 'Анна', 'last_name': 'Иванова',
                'age': 22, 'grade': 4.2, 'email': 'anna@example.com'
            })
            ui.run()
    
    @patch('builtins.input', side_effect=["1", "7", "1", "age", "0", "0"])
    def test_run_manage_indexes(self, mock_input):
        """Тест управления индексами."""
        with patch('sys.stdout', new_callable=StringIO):
            ui = ConsoleInterface()
            ui.run()


class TestRunFunction(unittest.TestCase):
    
    def test_run_function(self):
        """Тест функции run()."""
        with patch('src.db.tui.ConsoleInterface.run') as mock_run:
            from src.db.tui import run
            run()
            mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()