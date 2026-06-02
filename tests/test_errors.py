import unittest
from src.db.backend.errors import (
    StudentTableError,
    InvalidAgeError,
    InvalidGradeError,
    InvalidNameError,
    InvalidEmailError,
    DuplicateEmailError,
    RecordNotFoundError,
    DatabaseError,
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)


class TestErrors(unittest.TestCase):
    def test_student_table_error(self):
        error = StudentTableError("Test message")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test message")

    def test_invalid_age_error(self):
        error = InvalidAgeError("Age is invalid")
        self.assertIsInstance(error, StudentTableError)
        self.assertEqual(str(error), "Age is invalid")

    def test_invalid_grade_error(self):
        error = InvalidGradeError("Grade is invalid")
        self.assertIsInstance(error, StudentTableError)
        self.assertEqual(str(error), "Grade is invalid")

    def test_invalid_name_error(self):
        error = InvalidNameError("Name is invalid")
        self.assertIsInstance(error, StudentTableError)
        self.assertEqual(str(error), "Name is invalid")

    def test_invalid_email_error(self):
        error = InvalidEmailError("Email is invalid")
        self.assertIsInstance(error, StudentTableError)
        self.assertEqual(str(error), "Email is invalid")

    def test_duplicate_email_error(self):
        error = DuplicateEmailError("Email already exists")
        self.assertIsInstance(error, StudentTableError)
        self.assertEqual(str(error), "Email already exists")

    def test_record_not_found_error(self):
        error = RecordNotFoundError("Record not found")
        self.assertIsInstance(error, StudentTableError)
        self.assertEqual(str(error), "Record not found")

    def test_database_error(self):
        error = DatabaseError("Database error")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Database error")

    def test_table_already_exists_error(self):
        error = TableAlreadyExistsError("Table exists")
        self.assertIsInstance(error, DatabaseError)
        self.assertEqual(str(error), "Table exists")

    def test_table_not_found_error(self):
        error = TableNotFoundError("Table not found")
        self.assertIsInstance(error, DatabaseError)
        self.assertEqual(str(error), "Table not found")

    def test_missing_column_error(self):
        error = MissingColumnError("Column missing")
        self.assertIsInstance(error, DatabaseError)
        self.assertEqual(str(error), "Column missing")

    def test_unknown_column_error(self):
        error = UnknownColumnError("Unknown column")
        self.assertIsInstance(error, DatabaseError)
        self.assertEqual(str(error), "Unknown column")

    def test_invalid_storage_data_error(self):
        error = InvalidStorageDataError("Invalid storage data")
        self.assertIsInstance(error, DatabaseError)
        self.assertEqual(str(error), "Invalid storage data")


if __name__ == "__main__":
    unittest.main()