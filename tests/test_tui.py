import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from src.db.tui import ConsoleInterface, run
from src.db.backend.errors import (
    InvalidNameError,
    InvalidAgeError,
    InvalidGradeError,
    InvalidEmailError,
    DuplicateEmailError,
    RecordNotFoundError,
)


class TestConsoleInterface(unittest.TestCase):
    def setUp(self):
        self.ui = ConsoleInterface()
        self.ui.db.clear()

    def test_initialization(self):
        self.assertIsInstance(self.ui, ConsoleInterface)
        self.assertIsNotNone(self.ui.db)
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_menu(self, mock_stdout):
        self.ui._print_menu()
        output = mock_stdout.getvalue()
        self.assertIn("СИСТЕМА УПРАВЛЕНИЯ СТУДЕНТАМИ", output)
        self.assertIn("1. Добавить студента", output)

    @patch('builtins.input', side_effect=["42"])
    def test_read_int_success(self, mock_input):
        result = self.ui._read_int("Введите число: ")
        self.assertEqual(result, 42)

    @patch('builtins.input', side_effect=["", "25"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_int_empty_then_valid(self, mock_stdout, mock_input):
        result = self.ui._read_int("Введите число: ")
        self.assertEqual(result, 25)

    @patch('builtins.input', side_effect=["abc", "xyz", "10"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_int_invalid_then_valid(self, mock_stdout, mock_input):
        result = self.ui._read_int("Введите число: ")
        self.assertEqual(result, 10)

    @patch('builtins.input', side_effect=[""])
    def test_read_optional_int_empty(self, mock_input):
        result = self.ui._read_optional_int("Введите число: ")
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=["100"])
    def test_read_optional_int_with_value(self, mock_input):
        result = self.ui._read_optional_int("Введите число: ")
        self.assertEqual(result, 100)

    @patch('builtins.input', side_effect=["abc", "50"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_optional_int_invalid(self, mock_stdout, mock_input):
        result = self.ui._read_optional_int("Введите число: ")
        self.assertEqual(result, 50)

    @patch('builtins.input', side_effect=["3.14"])
    def test_read_float_success(self, mock_input):
        result = self.ui._read_float("Введите число: ")
        self.assertEqual(result, 3.14)

    @patch('builtins.input', side_effect=["", "2.5"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_float_empty_then_valid(self, mock_stdout, mock_input):
        result = self.ui._read_float("Введите число: ")
        self.assertEqual(result, 2.5)

    @patch('builtins.input', side_effect=["abc", "not a number", "4.8"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_float_invalid_then_valid(self, mock_stdout, mock_input):
        result = self.ui._read_float("Введите число: ")
        self.assertEqual(result, 4.8)

    @patch('builtins.input', side_effect=[""])
    def test_read_optional_float_empty(self, mock_input):
        result = self.ui._read_optional_float("Введите число: ")
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=["4.2"])
    def test_read_optional_float_with_value(self, mock_input):
        result = self.ui._read_optional_float("Введите число: ")
        self.assertEqual(result, 4.2)

    @patch('builtins.input', side_effect=["abc", "3.7"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_optional_float_invalid(self, mock_stdout, mock_input):
        result = self.ui._read_optional_float("Введите число: ")
        self.assertEqual(result, 3.7)

    @patch('builtins.input', side_effect=["Иван"])
    def test_read_string_required_success(self, mock_input):
        result = self.ui._read_string("Введите имя: ", required=True)
        self.assertEqual(result, "Иван")

    @patch('builtins.input', side_effect=["", "Петр"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_string_required_empty_then_valid(self, mock_stdout, mock_input):
        result = self.ui._read_string("Введите имя: ", required=True)
        self.assertEqual(result, "Петр")

    @patch('builtins.input', side_effect=[""])
    def test_read_string_not_required_empty(self, mock_input):
        result = self.ui._read_string("Введите имя: ", required=False)
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=["Мария"])
    def test_read_string_not_required_with_value(self, mock_input):
        result = self.ui._read_string("Введите имя: ", required=False)
        self.assertEqual(result, "Мария")

    def test_grade_to_text_excellent(self):
        self.assertEqual(self.ui._grade_to_text(5.0), "Отлично")

    def test_grade_to_text_good(self):
        self.assertEqual(self.ui._grade_to_text(4.4), "Хорошо")

    def test_grade_to_text_satisfactory(self):
        self.assertEqual(self.ui._grade_to_text(3.4), "Удовлетворительно")

    def test_grade_to_text_unsatisfactory(self):
        self.assertEqual(self.ui._grade_to_text(2.4), "Неудовлетворительно")

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_records_empty(self, mock_stdout):
        self.ui._print_records([])
        output = mock_stdout.getvalue()
        self.assertIn("Студенты не найдены", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_records_with_data(self, mock_stdout):
        record = (1, "Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._print_records([record])
        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)

    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "4.7", "ivan@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_success(self, mock_stdout, mock_input):
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 1)

    @patch('builtins.input', side_effect=["", "Иван", "Петров", "20", "4.7", "test@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_empty_name_then_valid(self, mock_stdout, mock_input):
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 1)

    @patch('builtins.input', side_effect=["Иван", "", "Петров", "20", "4.7", "test@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_empty_last_name_then_valid(self, mock_stdout, mock_input):
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 1)

    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "4.7", "", "test@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_empty_email_then_valid(self, mock_stdout, mock_input):
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 1)

    @patch('builtins.input', side_effect=["Иван", "Петров", "-5", "4.7", "test@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_invalid_age(self, mock_stdout, mock_input):
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "6", "test@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_invalid_grade(self, mock_stdout, mock_input):
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "4.7", "invalid"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_invalid_email(self, mock_stdout, mock_input):
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "4.7", "test@example.com"])
    def test_add_student_duplicate_email(self, mock_input):
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "test@example.com")
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.ui._add_student()
            self.assertEqual(self.ui.db.count_records(), 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_show_all_students_empty(self, mock_stdout):
        self.ui._show_all_students()
        output = mock_stdout.getvalue()
        self.assertIn("Студенты не найдены", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_show_all_students_with_data(self, mock_stdout):
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._show_all_students()
        output = mock_stdout.getvalue()
        self.assertIn("Всего студентов: 1", output)

    @patch('builtins.input', side_effect=["", "", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_students_by_filter_no_filters(self, mock_stdout, mock_input):
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._find_students_by_filter()
        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)

    @patch('builtins.input', side_effect=["999", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_not_found(self, mock_stdout, mock_input):
        self.ui._update_student()
        output = mock_stdout.getvalue()
        self.assertIn("не найден", output)

    @patch('builtins.input', side_effect=["1", "", "", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_no_changes(self, mock_stdout, mock_input):
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._update_student()
        output = mock_stdout.getvalue()
        self.assertIn("Ни одно поле не было изменено", output)

    @patch('builtins.input', side_effect=["1", "Петр", "", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_change_name(self, mock_stdout, mock_input):
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._update_student()
        records = self.ui.db.select_record()
        self.assertEqual(records[0][1], "Петр")

    @patch('builtins.input', side_effect=["999", "да"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_delete_student_not_found(self, mock_stdout, mock_input):
        self.ui._delete_student()
        output = mock_stdout.getvalue()
        self.assertIn("не найден", output)

    @patch('builtins.input', side_effect=["1", "да"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_delete_student_success(self, mock_stdout, mock_input):
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._delete_student()
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('builtins.input', side_effect=["10"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_invalid_field(self, mock_stdout, mock_input):
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Неверный выбор поля", output)

    @patch('builtins.input', side_effect=["1", "3"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_invalid_order(self, mock_stdout, mock_input):
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Неверный выбор порядка", output)

    @patch('builtins.input', side_effect=["1", "1", "нет", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_by_id_ascending(self, mock_stdout, mock_input):
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Отсортированные студенты", output)

    @patch('builtins.input', side_effect=["1", "1", "да", "20", "", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_with_filter(self, mock_stdout, mock_input):
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Отсортированные студенты", output)

    @patch('builtins.input', side_effect=["1", "1", "да", "invalid", "20", "", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_with_invalid_filter(self, mock_stdout, mock_input):
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._sort_students()

    @patch('builtins.input', side_effect=["0"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_exit(self, mock_stdout, mock_input):
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("До свидания", output)

    @patch('builtins.input', side_effect=["invalid", "", "0"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_invalid_command(self, mock_stdout, mock_input):
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("Неизвестная команда", output)

    @patch('builtins.input', side_effect=["1", "Иван", "Петров", "20", "4.7", "ivan@example.com", "", "0"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_full_flow_add_and_exit(self, mock_stdout, mock_input):
        self.ui.run()
        self.assertEqual(self.ui.db.count_records(), 1)

    @patch('builtins.input', side_effect=["2", "", "0"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_show_empty(self, mock_stdout, mock_input):
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("Студенты не найдены", output)


class TestRunFunction(unittest.TestCase):
    @patch('src.db.tui.ConsoleInterface.run')
    def test_run_function(self, mock_run):
        run()
        mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()