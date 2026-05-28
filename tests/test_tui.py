import unittest
from unittest.mock import patch, MagicMock, call
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

    # === Тесты для _print_menu ===
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_menu(self, mock_stdout):
        """Тест вывода меню."""
        self.ui._print_menu()
        output = mock_stdout.getvalue()
        self.assertIn("СИСТЕМА УПРАВЛЕНИЯ СТУДЕНТАМИ", output)
        self.assertIn("1. Добавить студента", output)
        self.assertIn("2. Показать всех студентов", output)
        self.assertIn("3. Найти студентов по фильтру", output)
        self.assertIn("4. Обновить информацию о студенте", output)
        self.assertIn("5. Удалить студента", output)
        self.assertIn("6. Сортировать студентов", output)
        self.assertIn("0. Выход", output)

    # === Тесты для _read_int ===
    @patch('builtins.input', side_effect=["42"])
    def test_read_int_success(self, mock_input):
        """Тест успешного чтения целого числа."""
        result = self.ui._read_int("Введите число: ")
        self.assertEqual(result, 42)

    @patch('builtins.input', side_effect=["", "25"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_int_empty_then_valid(self, mock_stdout, mock_input):
        """Тест чтения целого числа: пустой ввод, затем валидный."""
        result = self.ui._read_int("Введите число: ")
        self.assertEqual(result, 25)
        self.assertIn("Ошибка: поле не может быть пустым", mock_stdout.getvalue())

    @patch('builtins.input', side_effect=["abc", "xyz", "10"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_int_invalid_then_valid(self, mock_stdout, mock_input):
        """Тест чтения целого числа: неверный ввод, затем валидный."""
        result = self.ui._read_int("Введите число: ")
        self.assertEqual(result, 10)
        output = mock_stdout.getvalue()
        self.assertEqual(output.count("Ошибка: введите целое число"), 2)

    # === Тесты для _read_optional_int ===
    @patch('builtins.input', side_effect=[""])
    def test_read_optional_int_empty(self, mock_input):
        """Тест чтения необязательного целого числа (пустой ввод)."""
        result = self.ui._read_optional_int("Введите число: ")
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=["100"])
    def test_read_optional_int_with_value(self, mock_input):
        """Тест чтения необязательного целого числа (с вводом)."""
        result = self.ui._read_optional_int("Введите число: ")
        self.assertEqual(result, 100)

    @patch('builtins.input', side_effect=["abc", "50"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_optional_int_invalid(self, mock_stdout, mock_input):
        """Тест чтения необязательного целого числа (неверный ввод)."""
        result = self.ui._read_optional_int("Введите число: ")
        self.assertEqual(result, 50)

    # === Тесты для _read_float ===
    @patch('builtins.input', side_effect=["3.14"])
    def test_read_float_success(self, mock_input):
        """Тест успешного чтения вещественного числа."""
        result = self.ui._read_float("Введите число: ")
        self.assertEqual(result, 3.14)

    @patch('builtins.input', side_effect=["", "2.5"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_float_empty_then_valid(self, mock_stdout, mock_input):
        """Тест чтения вещественного числа: пустой ввод, затем валидный."""
        result = self.ui._read_float("Введите число: ")
        self.assertEqual(result, 2.5)
        self.assertIn("Ошибка: поле не может быть пустым", mock_stdout.getvalue())

    @patch('builtins.input', side_effect=["abc", "not a number", "4.8"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_float_invalid_then_valid(self, mock_stdout, mock_input):
        """Тест чтения вещественного числа: неверный ввод, затем валидный."""
        result = self.ui._read_float("Введите число: ")
        self.assertEqual(result, 4.8)
        output = mock_stdout.getvalue()
        self.assertEqual(output.count("Ошибка: введите число"), 2)

    # === Тесты для _read_optional_float ===
    @patch('builtins.input', side_effect=[""])
    def test_read_optional_float_empty(self, mock_input):
        """Тест чтения необязательного вещественного числа (пустой ввод)."""
        result = self.ui._read_optional_float("Введите число: ")
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=["4.2"])
    def test_read_optional_float_with_value(self, mock_input):
        """Тест чтения необязательного вещественного числа (с вводом)."""
        result = self.ui._read_optional_float("Введите число: ")
        self.assertEqual(result, 4.2)

    @patch('builtins.input', side_effect=["abc", "3.7"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_optional_float_invalid(self, mock_stdout, mock_input):
        """Тест чтения необязательного вещественного числа (неверный ввод)."""
        result = self.ui._read_optional_float("Введите число: ")
        self.assertEqual(result, 3.7)

    # === Тесты для _read_string ===
    @patch('builtins.input', side_effect=["Иван"])
    def test_read_string_required_success(self, mock_input):
        """Тест чтения обязательной строки."""
        result = self.ui._read_string("Введите имя: ", required=True)
        self.assertEqual(result, "Иван")

    @patch('builtins.input', side_effect=["", "Петр"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_string_required_empty_then_valid(self, mock_stdout, mock_input):
        """Тест чтения обязательной строки: пустой ввод, затем валидный."""
        result = self.ui._read_string("Введите имя: ", required=True)
        self.assertEqual(result, "Петр")
        self.assertIn("Ошибка: поле не может быть пустым", mock_stdout.getvalue())

    @patch('builtins.input', side_effect=[""])
    def test_read_string_not_required_empty(self, mock_input):
        """Тест чтения необязательной строки (пустой ввод)."""
        result = self.ui._read_string("Введите имя: ", required=False)
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=["Мария"])
    def test_read_string_not_required_with_value(self, mock_input):
        """Тест чтения необязательной строки (с вводом)."""
        result = self.ui._read_string("Введите имя: ", required=False)
        self.assertEqual(result, "Мария")

    # === Тесты для _grade_to_text ===
    def test_grade_to_text_excellent(self):
        """Тест преобразования отличной оценки."""
        self.assertEqual(self.ui._grade_to_text(5.0), "Отлично")
        self.assertEqual(self.ui._grade_to_text(4.7), "Отлично")
        self.assertEqual(self.ui._grade_to_text(4.5), "Отлично")

    def test_grade_to_text_good(self):
        """Тест преобразования хорошей оценки."""
        self.assertEqual(self.ui._grade_to_text(4.4), "Хорошо")
        self.assertEqual(self.ui._grade_to_text(4.0), "Хорошо")
        self.assertEqual(self.ui._grade_to_text(3.5), "Хорошо")

    def test_grade_to_text_satisfactory(self):
        """Тест преобразования удовлетворительной оценки."""
        self.assertEqual(self.ui._grade_to_text(3.4), "Удовлетворительно")
        self.assertEqual(self.ui._grade_to_text(3.0), "Удовлетворительно")
        self.assertEqual(self.ui._grade_to_text(2.5), "Удовлетворительно")

    def test_grade_to_text_unsatisfactory(self):
        """Тест преобразования неудовлетворительной оценки."""
        self.assertEqual(self.ui._grade_to_text(2.4), "Неудовлетворительно")
        self.assertEqual(self.ui._grade_to_text(2.0), "Неудовлетворительно")
        self.assertEqual(self.ui._grade_to_text(0.0), "Неудовлетворительно")

    # === Тесты для _print_records ===
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_records_empty(self, mock_stdout):
        """Тест вывода пустого списка записей."""
        self.ui._print_records([])
        output = mock_stdout.getvalue()
        self.assertIn("Студенты не найдены", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_records_with_data(self, mock_stdout):
        """Тест вывода списка записей с данными."""
        record = (1, "Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._print_records([record])
        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)
        self.assertIn("Петров", output)
        self.assertIn("4.70", output)
        self.assertIn("Отлично", output)
        self.assertIn("ivan@example.com", output)

    # === Тесты для _add_student ===
    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "4.7", "ivan@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_success(self, mock_stdout, mock_input):
        """Тест успешного добавления студента."""
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 1)
        output = mock_stdout.getvalue()
        self.assertIn("Студент успешно добавлен", output)
        self.assertIn("Иван Петров", output)

    @patch('builtins.input', side_effect=["", "Петров", "20", "4.7", "test@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_empty_name(self, mock_stdout, mock_input):
        """Тест добавления студента с пустым именем."""
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 0)
        output = mock_stdout.getvalue()
        self.assertIn("Ошибка", output)

    @patch('builtins.input', side_effect=["Иван", "", "20", "4.7", "test@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_empty_last_name(self, mock_stdout, mock_input):
        """Тест добавления студента с пустой фамилией."""
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('builtins.input', side_effect=["Иван", "Петров", "-5", "4.7", "test@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_invalid_age(self, mock_stdout, mock_input):
        """Тест добавления студента с некорректным возрастом."""
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "6", "test@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_invalid_grade(self, mock_stdout, mock_input):
        """Тест добавления студента с некорректным баллом."""
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "4.7", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_empty_email(self, mock_stdout, mock_input):
        """Тест добавления студента с пустым email."""
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "4.7", "invalid"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_invalid_email(self, mock_stdout, mock_input):
        """Тест добавления студента с некорректным email."""
        self.ui._add_student()
        self.assertEqual(self.ui.db.count_records(), 0)

    @patch('builtins.input', side_effect=["Иван", "Петров", "20", "4.7", "test@example.com"])
    def test_add_student_duplicate_email(self, mock_input):
        """Тест добавления студента с дублирующимся email."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "test@example.com")
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.ui._add_student()
            self.assertEqual(self.ui.db.count_records(), 1)
            output = mock_stdout.getvalue()
            self.assertIn("Ошибка", output)

    # === Тесты для _show_all_students ===
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_all_students_empty(self, mock_stdout):
        """Тест показа всех студентов (пустая таблица)."""
        self.ui._show_all_students()
        output = mock_stdout.getvalue()
        self.assertIn("Студенты не найдены", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_show_all_students_with_data(self, mock_stdout):
        """Тест показа всех студентов (с данными)."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui._show_all_students()
        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)
        self.assertIn("Петров", output)
        self.assertIn("Мария", output)
        self.assertIn("Иванова", output)
        self.assertIn("Всего студентов: 2", output)

    # === Тесты для _find_students_by_filter ===
    @patch('builtins.input', side_effect=["", "", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_students_by_filter_no_filters(self, mock_stdout, mock_input):
        """Тест поиска студентов без фильтров."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._find_students_by_filter()
        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)

    @patch('builtins.input', side_effect=["1", "", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_students_by_filter_by_id(self, mock_stdout, mock_input):
        """Тест поиска студентов по ID."""
        record = self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        # Меняем сид эффект для правильного ID
        with patch('builtins.input', side_effect=[str(record[0]), "", "", "", "", ""]):
            self.ui._find_students_by_filter()
            output = mock_stdout.getvalue()
            self.assertIn("Иван", output)

    @patch('builtins.input', side_effect=["", "Иван", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_students_by_filter_by_name(self, mock_stdout, mock_input):
        """Тест поиска студентов по имени."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui._find_students_by_filter()
        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)
        self.assertNotIn("Мария", output)

    @patch('builtins.input', side_effect=["", "", "Петров", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_students_by_filter_by_last_name(self, mock_stdout, mock_input):
        """Тест поиска студентов по фамилии."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui._find_students_by_filter()
        output = mock_stdout.getvalue()
        self.assertIn("Петров", output)
        self.assertNotIn("Иванова", output)

    @patch('builtins.input', side_effect=["", "", "", "20", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_students_by_filter_by_age(self, mock_stdout, mock_input):
        """Тест поиска студентов по возрасту."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui._find_students_by_filter()
        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)
        self.assertNotIn("Мария", output)

    @patch('builtins.input', side_effect=["", "", "", "", "4.7", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_students_by_filter_by_grade(self, mock_stdout, mock_input):
        """Тест поиска студентов по среднему баллу."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui._find_students_by_filter()
        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)
        self.assertNotIn("Мария", output)

    @patch('builtins.input', side_effect=["", "", "", "", "", "ivan@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_students_by_filter_by_email(self, mock_stdout, mock_input):
        """Тест поиска студентов по email."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui._find_students_by_filter()
        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)
        self.assertNotIn("Мария", output)

    # === Тесты для _update_student ===
    @patch('builtins.input', side_effect=["999"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_not_found(self, mock_stdout, mock_input):
        """Тест обновления несуществующего студента."""
        self.ui._update_student()
        output = mock_stdout.getvalue()
        self.assertIn("не найден", output)

    @patch('builtins.input', side_effect=["1", "", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_no_changes(self, mock_stdout, mock_input):
        """Тест обновления студента без изменений."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._update_student()
        output = mock_stdout.getvalue()
        self.assertIn("успешно обновлена", output)

    @patch('builtins.input', side_effect=["1", "Петр", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_change_name(self, mock_stdout, mock_input):
        """Тест обновления имени студента."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._update_student()
        records = self.ui.db.select_record()
        self.assertEqual(records[0][1], "Петр")

    @patch('builtins.input', side_effect=["1", "", "Сидоров", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_change_last_name(self, mock_stdout, mock_input):
        """Тест обновления фамилии студента."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._update_student()
        records = self.ui.db.select_record()
        self.assertEqual(records[0][2], "Сидоров")

    @patch('builtins.input', side_effect=["1", "", "", "21", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_change_age(self, mock_stdout, mock_input):
        """Тест обновления возраста студента."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._update_student()
        records = self.ui.db.select_record()
        self.assertEqual(records[0][3], 21)

    @patch('builtins.input', side_effect=["1", "", "", "", "4.9", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_change_grade(self, mock_stdout, mock_input):
        """Тест обновления среднего балла студента."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._update_student()
        records = self.ui.db.select_record()
        self.assertEqual(records[0][4], 4.9)

    @patch('builtins.input', side_effect=["1", "", "", "", "", "new@example.com"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_change_email(self, mock_stdout, mock_input):
        """Тест обновления email студента."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._update_student()
        records = self.ui.db.select_record()
        self.assertEqual(records[0][5], "new@example.com")

    @patch('builtins.input', side_effect=["1", "", "", "", "", "invalid"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_student_invalid_email(self, mock_stdout, mock_input):
        """Тест обновления с некорректным email."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._update_student()
        output = mock_stdout.getvalue()
        self.assertIn("Ошибка", output)

    # === Тесты для _delete_student ===
    @patch('builtins.input', side_effect=["999", "да"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_delete_student_not_found(self, mock_stdout, mock_input):
        """Тест удаления несуществующего студента."""
        self.ui._delete_student()
        output = mock_stdout.getvalue()
        self.assertIn("не найден", output)

    @patch('builtins.input', side_effect=["1", "да"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_delete_student_success(self, mock_stdout, mock_input):
        """Тест успешного удаления студента."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.assertEqual(self.ui.db.count_records(), 1)
        self.ui._delete_student()
        self.assertEqual(self.ui.db.count_records(), 0)
        output = mock_stdout.getvalue()
        self.assertIn("успешно удалён", output)

    @patch('builtins.input', side_effect=["1", "нет"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_delete_student_cancel(self, mock_stdout, mock_input):
        """Тест отмены удаления студента."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.assertEqual(self.ui.db.count_records(), 1)
        self.ui._delete_student()
        self.assertEqual(self.ui.db.count_records(), 1)
        output = mock_stdout.getvalue()
        self.assertIn("Удаление отменено", output)

    # === Тесты для _sort_students ===
    @patch('builtins.input', side_effect=["10"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_invalid_field(self, mock_stdout, mock_input):
        """Тест сортировки с неверным выбором поля."""
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Неверный выбор поля", output)

    @patch('builtins.input', side_effect=["1", "3"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_invalid_order(self, mock_stdout, mock_input):
        """Тест сортировки с неверным выбором порядка."""
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Неверный выбор порядка", output)

    @patch('builtins.input', side_effect=["1", "1", "нет"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_by_id_ascending(self, mock_stdout, mock_input):
        """Тест сортировки по ID по возрастанию."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui.db.create_record("Петр", "Сидоров", 19, 3.5, "petr@example.com")
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Отсортированные студенты", output)

    @patch('builtins.input', side_effect=["2", "2", "нет"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_by_name_descending(self, mock_stdout, mock_input):
        """Тест сортировки по имени по убыванию."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Анна", "Иванова", 22, 4.2, "anna@example.com")
        self.ui.db.create_record("Петр", "Сидоров", 19, 3.5, "petr@example.com")
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Отсортированные студенты", output)

    @patch('builtins.input', side_effect=["3", "1", "нет"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_by_last_name_ascending(self, mock_stdout, mock_input):
        """Тест сортировки по фамилии по возрастанию."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Антонова", 22, 4.2, "maria@example.com")
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Отсортированные студенты", output)

    @patch('builtins.input', side_effect=["4", "2", "нет"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_by_age_descending(self, mock_stdout, mock_input):
        """Тест сортировки по возрасту по убыванию."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Отсортированные студенты", output)

    @patch('builtins.input', side_effect=["5", "2", "нет"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_by_grade_descending(self, mock_stdout, mock_input):
        """Тест сортировки по баллу по убыванию."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Отсортированные студенты", output)

    @patch('builtins.input', side_effect=["6", "1", "нет"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_by_email_ascending(self, mock_stdout, mock_input):
        """Тест сортировки по email по возрастанию."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Отсортированные студенты", output)

    @patch('builtins.input', side_effect=["1", "1", "да", "20", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_with_filter(self, mock_stdout, mock_input):
        """Тест сортировки с фильтрацией."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.ui.db.create_record("Петр", "Сидоров", 20, 3.5, "petr@example.com")
        self.ui._sort_students()
        output = mock_stdout.getvalue()
        self.assertIn("Отсортированные студенты", output)

    @patch('builtins.input', side_effect=["1", "1", "да", "invalid", "", "", "", ""])
    @patch('sys.stdout', new_callable=StringIO)
    def test_sort_students_with_invalid_filter(self, mock_stdout, mock_input):
        """Тест сортировки с некорректным фильтром."""
        self.ui.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.ui._sort_students()
        # Должен отработать без ошибок

    # === Тест для метода run ===
    @patch('builtins.input', side_effect=["0"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_exit(self, mock_stdout, mock_input):
        """Тест выхода из программы."""
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("До свидания", output)

    @patch('builtins.input', side_effect=["invalid", "0"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_invalid_command(self, mock_stdout, mock_input):
        """Тест ввода неверной команды."""
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("Неизвестная команда", output)

    @patch('builtins.input', side_effect=["1", "Иван", "Петров", "20", "4.7", "ivan@example.com", "0"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_full_flow_add_and_exit(self, mock_stdout, mock_input):
        """Тест полного цикла: добавление и выход."""
        self.ui.run()
        self.assertEqual(self.ui.db.count_records(), 1)

    @patch('builtins.input', side_effect=["2", "0"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_show_empty(self, mock_stdout, mock_input):
        """Тест показа пустой таблицы."""
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("Студенты не найдены", output)


class TestRunFunction(unittest.TestCase):
    """Тесты для функции run() из tui.py."""

    @patch('src.db.tui.ConsoleInterface.run')
    def test_run_function(self, mock_run):
        """Тест вызова функции run()."""
        run()
        mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()