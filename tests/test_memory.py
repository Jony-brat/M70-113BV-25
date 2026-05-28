import unittest
from src.db.backend.memory import StudentTable
from src.db.backend.errors import (
    InvalidAgeError,
    InvalidGradeError,
    InvalidNameError,
    InvalidEmailError,
    DuplicateEmailError,
    RecordNotFoundError,
)

class TestStudentTable(unittest.TestCase):
    def setUp(self):
        self.db = StudentTable()
        self.test_students = [
            ("Иван", "Петров", 20, 4.7, "ivan@example.com"),
            ("Мария", "Иванова", 22, 4.2, "maria@example.com"),
            ("Петр", "Сидоров", 19, 3.5, "petr@example.com"),
            ("Анна", "Кузнецова", 21, 4.9, "anna@example.com"),
            ("Сергей", "Смирнов", 23, 3.8, "sergey@example.com"),
        ]

    def tearDown(self):
        self.db.clear()

    def test_initialization(self):
        """Тест инициализации таблицы."""
        self.assertIsInstance(self.db, StudentTable)
        self.assertEqual(self.db.count_records(), 0)

    def test_create_record_success(self):
        """Тест успешного создания записи."""
        record = self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        
        self.assertEqual(record[1], "Иван")
        self.assertEqual(record[2], "Петров")
        self.assertEqual(record[3], 20)
        self.assertEqual(record[4], 4.7)
        self.assertEqual(record[5], "ivan@example.com")
        self.assertEqual(self.db.count_records(), 1)

    def test_create_record_generates_unique_id(self):
        """Тест генерации уникальных ID."""
        record1 = self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        record2 = self.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        
        self.assertNotEqual(record1[0], record2[0])
        self.assertEqual(record2[0], record1[0] + 1)

    def test_create_record_invalid_name(self):
        """Тест валидации имени."""
        with self.assertRaises(InvalidNameError):
            self.db.create_record("", "Петров", 20, 4.7, "test@example.com")
        
        with self.assertRaises(InvalidNameError):
            self.db.create_record("А", "Петров", 20, 4.7, "test@example.com")

    def test_create_record_invalid_last_name(self):
        """Тест валидации фамилии."""
        with self.assertRaises(InvalidNameError):
            self.db.create_record("Иван", "", 20, 4.7, "test@example.com")
        
        with self.assertRaises(InvalidNameError):
            self.db.create_record("Иван", "П", 20, 4.7, "test@example.com")

    def test_create_record_invalid_age(self):
        """Тест валидации возраста."""
        with self.assertRaises(InvalidAgeError):
            self.db.create_record("Иван", "Петров", -5, 4.7, "test@example.com")
        
        with self.assertRaises(InvalidAgeError):
            self.db.create_record("Иван", "Петров", 150, 4.7, "test@example.com")

    def test_create_record_invalid_grade(self):
        """Тест валидации среднего балла."""
        with self.assertRaises(InvalidGradeError):
            self.db.create_record("Иван", "Петров", 20, -1, "test@example.com")
        
        with self.assertRaises(InvalidGradeError):
            self.db.create_record("Иван", "Петров", 20, 6, "test@example.com")

    def test_create_record_invalid_email(self):
        """Тест валидации email."""
        with self.assertRaises(InvalidEmailError):
            self.db.create_record("Иван", "Петров", 20, 4.7, "")
        
        with self.assertRaises(InvalidEmailError):
            self.db.create_record("Иван", "Петров", 20, 4.7, "invalid")
        
        with self.assertRaises(InvalidEmailError):
            self.db.create_record("Иван", "Петров", 20, 4.7, "test@")

    def test_create_record_duplicate_email(self):
        """Тест проверки уникальности email."""
        self.db.create_record("Иван", "Петров", 20, 4.7, "test@example.com")
        
        with self.assertRaises(DuplicateEmailError):
            self.db.create_record("Мария", "Иванова", 22, 4.2, "test@example.com")

    def test_select_record_no_filters(self):
        """Тест выборки без фильтров."""
        for student in self.test_students:
            self.db.create_record(*student)
        
        records = self.db.select_record()
        self.assertEqual(len(records), 5)

    def test_select_record_by_id(self):
        """Тест выборки по ID."""
        created = []
        for student in self.test_students:
            created.append(self.db.create_record(*student))
        
        record = self.db.select_record(student_id=created[0][0])
        self.assertEqual(len(record), 1)
        self.assertEqual(record[0][1], "Иван")

    def test_select_record_by_first_name(self):
        """Тест выборки по имени."""
        for student in self.test_students:
            self.db.create_record(*student)
        
        records = self.db.select_record(first_name="Мария")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][2], "Иванова")

    def test_select_record_by_last_name(self):
        """Тест выборки по фамилии."""
        for student in self.test_students:
            self.db.create_record(*student)
        
        records = self.db.select_record(last_name="Сидоров")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "Петр")

    def test_select_record_by_age(self):
        """Тест выборки по возрасту."""
        for student in self.test_students:
            self.db.create_record(*student)
        
        records = self.db.select_record(age=20)
        self.assertEqual(len(records), 1)

    def test_select_record_by_grade(self):
        """Тест выборки по среднему баллу."""
        for student in self.test_students:
            self.db.create_record(*student)
        
        records = self.db.select_record(grade=4.2)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "Мария")

    def test_select_record_by_email(self):
        """Тест выборки по email."""
        for student in self.test_students:
            self.db.create_record(*student)
        
        records = self.db.select_record(email="petr@example.com")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "Петр")

    def test_select_record_multiple_filters(self):
        """Тест выборки по нескольким фильтрам."""
        for student in self.test_students:
            self.db.create_record(*student)
        
        records = self.db.select_record(first_name="Анна", last_name="Кузнецова")
        self.assertEqual(len(records), 1)

    def test_select_record_no_match(self):
        """Тест выборки без совпадений."""
        for student in self.test_students:
            self.db.create_record(*student)
        
        records = self.db.select_record(age=100)
        self.assertEqual(len(records), 0)

    def test_update_record_success(self):
        """Тест успешного обновления записи."""
        record = self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        
        updated = self.db.update_record(record[0], first_name="Петр", age=21, grade=4.8)
        
        self.assertEqual(updated[1], "Петр")
        self.assertEqual(updated[3], 21)
        self.assertEqual(updated[4], 4.8)
        self.assertEqual(updated[5], "ivan@example.com")

    def test_update_record_not_found(self):
        """Тест обновления несуществующей записи."""
        with self.assertRaises(RecordNotFoundError):
            self.db.update_record(999, first_name="Петр")

    def test_update_record_email_unique(self):
        """Тест уникальности email при обновлении."""
        self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        record2 = self.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        
        with self.assertRaises(DuplicateEmailError):
            self.db.update_record(record2[0], email="ivan@example.com")

    def test_delete_record_success(self):
        """Тест успешного удаления записи."""
        record = self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.assertEqual(self.db.count_records(), 1)
        
        deleted = self.db.delete_record(record[0])
        
        self.assertEqual(deleted[1], "Иван")
        self.assertEqual(self.db.count_records(), 0)

    def test_delete_record_not_found(self):
        """Тест удаления несуществующей записи."""
        with self.assertRaises(RecordNotFoundError):
            self.db.delete_record(999)

    def test_sort_records_by_id_ascending(self):
        """Тест сортировки по ID по возрастанию."""
        self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.db.create_record("Петр", "Сидоров", 19, 3.5, "petr@example.com")
        
        sorted_records = self.db.sort_records('id', reverse=False)
        
        ids = [r[0] for r in sorted_records]
        self.assertEqual(ids, sorted(ids))

    def test_sort_records_by_grade_descending(self):
        """Тест сортировки по баллу по убыванию."""
        self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.db.create_record("Петр", "Сидоров", 19, 3.5, "petr@example.com")
        
        sorted_records = self.db.sort_records('grade', reverse=True)
        
        grades = [r[4] for r in sorted_records]
        self.assertEqual(grades, sorted(grades, reverse=True))

    def test_sort_records_by_first_name(self):
        """Тест сортировки по имени."""
        self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.db.create_record("Анна", "Иванова", 22, 4.2, "anna@example.com")
        self.db.create_record("Петр", "Сидоров", 19, 3.5, "petr@example.com")
        
        sorted_records = self.db.sort_records('first_name', reverse=False)
        
        names = [r[1] for r in sorted_records]
        self.assertEqual(names, ["Анна", "Иван", "Петр"])

    def test_sort_records_with_filter(self):
        """Тест сортировки с применением фильтра."""
        self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.db.create_record("Петр", "Сидоров", 19, 3.5, "petr@example.com")
        
        sorted_records = self.db.sort_records(
            'grade', 
            reverse=True, 
            filter_params={'age': 20}
        )
        
        self.assertEqual(len(sorted_records), 1)
        self.assertEqual(sorted_records[0][1], "Иван")

    def test_get_all_records(self):
        """Тест получения всех записей."""
        for student in self.test_students:
            self.db.create_record(*student)
        
        records = self.db.get_all_records()
        self.assertEqual(len(records), 5)

    def test_count_records(self):
        """Тест подсчёта записей."""
        self.assertEqual(self.db.count_records(), 0)
        
        self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.assertEqual(self.db.count_records(), 1)
        
        self.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        self.assertEqual(self.db.count_records(), 2)

    def test_clear(self):
        """Тест очистки таблицы."""
        self.db.create_record("Иван", "Петров", 20, 4.7, "ivan@example.com")
        self.db.create_record("Мария", "Иванова", 22, 4.2, "maria@example.com")
        
        self.assertEqual(self.db.count_records(), 2)
        
        self.db.clear()
        self.assertEqual(self.db.count_records(), 0)


if __name__ == "__main__":
    unittest.main()