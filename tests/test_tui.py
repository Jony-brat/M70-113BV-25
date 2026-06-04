import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

from src.db.tui import ConsoleInterface, run, main
from src.db.backend.memory import MemoryDatabase
from src.db.backend.file import FileDatabase
from src.db.backend.errors import (
    InvalidNameError,
    InvalidAgeError,
    InvalidGradeError,
    InvalidEmailError,
    DuplicateEmailError,
    TableNotFoundError,
    TableAlreadyExistsError,
)


class TestConsoleInterface(unittest.TestCase):
    def create_ui_with_mock_db(self, mock_db):
        with patch('src.db.tui.ConsoleInterface._select_database', return_value=mock_db):
            ui = ConsoleInterface()
            return ui

    def test_initialization(self):
        mock_db = MagicMock()
        with patch('src.db.tui.ConsoleInterface._select_database', return_value=mock_db):
            ui = ConsoleInterface()
            self.assertEqual(ui.db, mock_db)

    def test_select_database_memory(self):
        with patch('builtins.input', side_effect=["1"]):
            with patch('sys.stdout', new_callable=StringIO):
                ui = ConsoleInterface()
                self.assertIsInstance(ui.db, MemoryDatabase)

    def test_select_database_file(self):
        with patch('builtins.input', side_effect=["2"]):
            with patch('sys.stdout', new_callable=StringIO):
                ui = ConsoleInterface()
                self.assertIsInstance(ui.db, FileDatabase)

    def test_select_database_invalid_then_valid(self):
        with patch('builtins.input', side_effect=["3", "1"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui = ConsoleInterface()
                self.assertIsInstance(ui.db, MemoryDatabase)
                output = mock_stdout.getvalue()
                self.assertIn("Ошибка: введите 1 или 2", output)

    def test_init_students_table_calls_create_table(self):
        mock_db = MagicMock()
        with patch('src.db.tui.ConsoleInterface._select_database', return_value=mock_db):
            ui = ConsoleInterface()
            mock_db.create_table.assert_called_once()

    def test_init_students_table_handles_exception(self):
        mock_db = MagicMock()
        mock_db.create_table.side_effect = TableAlreadyExistsError("Table exists")
        with patch('src.db.tui.ConsoleInterface._select_database', return_value=mock_db):
            ui = ConsoleInterface()
            mock_db.create_table.assert_called_once()

    def test_print_menu(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui._print_menu()
            output = mock_stdout.getvalue()
            self.assertIn("СИСТЕМА УПРАВЛЕНИЯ СТУДЕНТАМИ", output)

    def test_read_int_success(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["42"]):
            result = ui._read_int("Enter: ")
            self.assertEqual(result, 42)

    def test_read_int_empty_then_valid(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["", "25"]):
            with patch('sys.stdout', new_callable=StringIO):
                result = ui._read_int("Enter: ")
                self.assertEqual(result, 25)

    def test_read_int_invalid_then_valid(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["abc", "xyz", "10"]):
            result = ui._read_int("Enter: ")
            self.assertEqual(result, 10)

    def test_read_optional_int_empty(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=[""]):
            result = ui._read_optional_int("Enter: ")
            self.assertIsNone(result)

    def test_read_optional_int_with_value(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["100"]):
            result = ui._read_optional_int("Enter: ")
            self.assertEqual(result, 100)

    def test_read_optional_int_invalid(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["abc", "50"]):
            result = ui._read_optional_int("Enter: ")
            self.assertEqual(result, 50)

    def test_read_float_success(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["3.14"]):
            result = ui._read_float("Enter: ")
            self.assertEqual(result, 3.14)

    def test_read_float_empty_then_valid(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["", "2.5"]):
            result = ui._read_float("Enter: ")
            self.assertEqual(result, 2.5)

    def test_read_float_invalid_then_valid(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["abc", "4.8"]):
            result = ui._read_float("Enter: ")
            self.assertEqual(result, 4.8)

    def test_read_optional_float_empty(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=[""]):
            result = ui._read_optional_float("Enter: ")
            self.assertIsNone(result)

    def test_read_optional_float_with_value(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["4.2"]):
            result = ui._read_optional_float("Enter: ")
            self.assertEqual(result, 4.2)

    def test_read_optional_float_invalid(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["abc", "3.7"]):
            result = ui._read_optional_float("Enter: ")
            self.assertEqual(result, 3.7)

    def test_read_string_required_success(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["Иван"]):
            result = ui._read_string("Enter: ", required=True)
            self.assertEqual(result, "Иван")

    def test_read_string_required_empty_then_valid(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["", "Петр"]):
            result = ui._read_string("Enter: ", required=True)
            self.assertEqual(result, "Петр")

    def test_read_string_not_required_empty(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=[""]):
            result = ui._read_string("Enter: ", required=False)
            self.assertIsNone(result)

    def test_read_string_not_required_with_value(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["Мария"]):
            result = ui._read_string("Enter: ", required=False)
            self.assertEqual(result, "Мария")

    def test_grade_to_text(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        self.assertEqual(ui._grade_to_text(5.0), "Отлично")
        self.assertEqual(ui._grade_to_text(4.5), "Отлично")
        self.assertEqual(ui._grade_to_text(4.4), "Хорошо")
        self.assertEqual(ui._grade_to_text(3.5), "Хорошо")
        self.assertEqual(ui._grade_to_text(3.4), "Удовлетворительно")
        self.assertEqual(ui._grade_to_text(2.5), "Удовлетворительно")
        self.assertEqual(ui._grade_to_text(2.4), "Неудовлетворительно")

    def test_print_records_empty(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui._print_records([])
            self.assertIn("Студенты не найдены", mock_stdout.getvalue())

    def test_print_records_with_data(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        record = {"student_id": 1, "first_name": "Иван", "last_name": "Петров", "age": 20, "grade": 4.7, "email": "ivan@example.com"}
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui._print_records([record])
            output = mock_stdout.getvalue()
            self.assertIn("Иван", output)

    def test_get_next_id_empty(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        self.assertEqual(ui._get_next_id(), 1)

    def test_get_next_id_with_records(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = [{"student_id": 1}, {"student_id": 5}]
        ui = self.create_ui_with_mock_db(mock_db)
        self.assertEqual(ui._get_next_id(), 6)

    def test_validate_name_success(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        result = ui._validate_name("  Иван  ", "Имя")
        self.assertEqual(result, "Иван")

    def test_validate_name_empty(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(InvalidNameError):
            ui._validate_name("", "Имя")

    def test_validate_name_too_short(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(InvalidNameError):
            ui._validate_name("А", "Имя")

    def test_validate_age_success(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        self.assertEqual(ui._validate_age(25), 25)

    def test_validate_age_negative(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(InvalidAgeError):
            ui._validate_age(-5)

    def test_validate_age_too_high(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(InvalidAgeError):
            ui._validate_age(150)

    def test_validate_grade_success(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        self.assertEqual(ui._validate_grade(4.5), 4.5)

    def test_validate_grade_negative(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(InvalidGradeError):
            ui._validate_grade(-1)

    def test_validate_grade_too_high(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(InvalidGradeError):
            ui._validate_grade(6)

    def test_validate_email_success(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        result = ui._validate_email("  Test@Example.com  ")
        self.assertEqual(result, "test@example.com")

    def test_validate_email_empty(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(InvalidEmailError):
            ui._validate_email("")

    def test_validate_email_no_at(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(InvalidEmailError):
            ui._validate_email("testexample.com")

    def test_validate_email_no_dot(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(InvalidEmailError):
            ui._validate_email("test@example")

    def test_validate_email_duplicate(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = [{"student_id": 1, "email": "test@example.com"}]
        ui = self.create_ui_with_mock_db(mock_db)
        with self.assertRaises(DuplicateEmailError):
            ui._validate_email("test@example.com")

    def test_validate_email_duplicate_exclude_self(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = [{"student_id": 1, "email": "test@example.com"}]
        ui = self.create_ui_with_mock_db(mock_db)
        result = ui._validate_email("test@example.com", exclude_id=1)
        self.assertEqual(result, "test@example.com")

    def test_add_student_success(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["Иван", "Петров", "20", "4.7", "ivan@example.com"]
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO):
                ui._add_student()
        mock_db.insert_record.assert_called_once()

    def test_add_student_invalid_age(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["Иван", "Петров", "-5", "4.7", "test@example.com"]
        with patch('builtins.input', side_effect=inputs):
            ui._add_student()
        mock_db.insert_record.assert_not_called()

    def test_add_student_invalid_grade(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["Иван", "Петров", "20", "6", "test@example.com"]
        with patch('builtins.input', side_effect=inputs):
            ui._add_student()
        mock_db.insert_record.assert_not_called()

    def test_add_student_invalid_email(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["Иван", "Петров", "20", "4.7", "invalid"]
        with patch('builtins.input', side_effect=inputs):
            ui._add_student()
        mock_db.insert_record.assert_not_called()

    def test_add_student_duplicate_email(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = [{"student_id": 1, "email": "test@example.com"}]
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["Иван", "Петров", "20", "4.7", "test@example.com"]
        with patch('builtins.input', side_effect=inputs):
            ui._add_student()
        mock_db.insert_record.assert_not_called()

    def test_show_all_students_with_data(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = [{"student_id": 1, "first_name": "Иван", "last_name": "Петров", "age": 20, "grade": 4.7, "email": "ivan@example.com"}]
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui._show_all_students()
            self.assertIn("Иван", mock_stdout.getvalue())

    def test_show_all_students_empty(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ui._show_all_students()
            self.assertIn("Студенты не найдены", mock_stdout.getvalue())

    def test_find_students_by_filter(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["", "", "", "", "", ""]
        with patch('builtins.input', side_effect=inputs):
            ui._find_students_by_filter()
        mock_db.select_records.assert_called_once()

    def test_update_student_not_found(self):
        mock_db = MagicMock()
        mock_db.select_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["999", ""]
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._update_student()
                self.assertIn("не найден", mock_stdout.getvalue())

    def test_update_student_no_changes(self):
        mock_db = MagicMock()
        mock_db.select_records.return_value = [{"student_id": 1, "first_name": "Иван", "last_name": "Петров", "age": 20, "grade": 4.7, "email": "ivan@example.com"}]
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["1", "", "", "", "", "", ""]
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._update_student()
                self.assertIn("Ни одно поле не было изменено", mock_stdout.getvalue())
        mock_db.update_record.assert_not_called()

    def test_update_student_change_name(self):
        mock_db = MagicMock()
        mock_db.select_records.return_value = [{"student_id": 1, "first_name": "Иван", "last_name": "Петров", "age": 20, "grade": 4.7, "email": "ivan@example.com"}]
        mock_db.update_record.return_value = {"student_id": 1, "first_name": "Петр", "last_name": "Петров", "age": 20, "grade": 4.7, "email": "ivan@example.com"}
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["1", "Петр", "", "", "", "", ""]
        with patch('builtins.input', side_effect=inputs):
            ui._update_student()
        mock_db.update_record.assert_called_once()

    def test_delete_student_not_found(self):
        mock_db = MagicMock()
        mock_db.select_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["999", "да"]
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._delete_student()
                self.assertIn("не найден", mock_stdout.getvalue())

    def test_delete_student_success(self):
        mock_db = MagicMock()
        mock_db.select_records.return_value = [{"student_id": 1, "first_name": "Иван", "last_name": "Петров", "age": 20, "grade": 4.7, "email": "ivan@example.com"}]
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["1", "да"]
        with patch('builtins.input', side_effect=inputs):
            ui._delete_student()
        mock_db.delete_record.assert_called_once()

    def test_delete_student_cancel(self):
        mock_db = MagicMock()
        mock_db.select_records.return_value = [{"student_id": 1, "first_name": "Иван", "last_name": "Петров", "age": 20, "grade": 4.7, "email": "ivan@example.com"}]
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["1", "нет"]
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._delete_student()
                self.assertIn("Удаление отменено", mock_stdout.getvalue())
        mock_db.delete_record.assert_not_called()

    def test_sort_students_invalid_field(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["10"]
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._sort_students()
                self.assertIn("Неверный выбор поля", mock_stdout.getvalue())

    def test_sort_students_invalid_order(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["1", "3"]
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui._sort_students()
                self.assertIn("Неверный выбор порядка", mock_stdout.getvalue())

    def test_sort_students_success(self):
        mock_db = MagicMock()
        mock_db.get_all_records.return_value = []
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["1", "1", "нет", ""]
        with patch('builtins.input', side_effect=inputs):
            ui._sort_students()
        mock_db.get_all_records.assert_called()

    def test_run_exit(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui.run()
                self.assertIn("До свидания", mock_stdout.getvalue())

    def test_run_invalid_command(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=["invalid", "", "0"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui.run()
                self.assertIn("Неизвестная команда", mock_stdout.getvalue())

    def test_run_keyboard_interrupt(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ui.run()
                self.assertIn("Программа прервана пользователем", mock_stdout.getvalue())

    def test_run_unexpected_exception(self):
        mock_db = MagicMock()
        ui = self.create_ui_with_mock_db(mock_db)
        inputs = ["1", "", "0"]
        with patch('builtins.input', side_effect=inputs):
            with patch.object(ui, '_add_student', side_effect=Exception("Unexpected")):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    ui.run()
                    self.assertIn("Непредвиденная ошибка", mock_stdout.getvalue())


class TestRunFunction(unittest.TestCase):
    def test_run_function(self):
        with patch('src.db.tui.ConsoleInterface') as MockConsole:
            mock_instance = MockConsole.return_value
            run()
            MockConsole.assert_called_once()
            mock_instance.run.assert_called_once()

    def test_main_function(self):
        with patch('src.db.tui.run') as mock_run:
            main()
            mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()