import unittest
from src.db.backend.errors import (
    DatabaseError,
    TableAlreadyExistsError,
    TableNotFoundError,
    RecordNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
    InvalidRecordError,
    InvalidAgeError,
    InvalidGradeError,
    InvalidNameError,
    InvalidEmailError,
    DuplicateEmailError,
)


class TestErrors(unittest.TestCase):
    
    def test_database_error(self):
        """Тест DatabaseError."""
        with self.assertRaises(DatabaseError):
            raise DatabaseError("Database error")
        
        error = DatabaseError("Test message")
        self.assertEqual(str(error), "Test message")
    
    def test_table_already_exists_error(self):
        """Тест TableAlreadyExistsError."""
        with self.assertRaises(TableAlreadyExistsError):
            raise TableAlreadyExistsError("Table already exists")
        
        error = TableAlreadyExistsError("Table 'students' already exists")
        self.assertEqual(str(error), "Table 'students' already exists")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_table_not_found_error(self):
        """Тест TableNotFoundError."""
        with self.assertRaises(TableNotFoundError):
            raise TableNotFoundError("Table not found")
        
        error = TableNotFoundError("Table 'unknown' not found")
        self.assertEqual(str(error), "Table 'unknown' not found")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_record_not_found_error(self):
        """Тест RecordNotFoundError."""
        with self.assertRaises(RecordNotFoundError):
            raise RecordNotFoundError("Record not found")
        
        error = RecordNotFoundError("Record with id=1 not found")
        self.assertEqual(str(error), "Record with id=1 not found")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_missing_column_error(self):
        """Тест MissingColumnError."""
        with self.assertRaises(MissingColumnError):
            raise MissingColumnError("Missing column")
        
        error = MissingColumnError("Field 'age' is required")
        self.assertEqual(str(error), "Field 'age' is required")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_unknown_column_error(self):
        """Тест UnknownColumnError."""
        with self.assertRaises(UnknownColumnError):
            raise UnknownColumnError("Unknown column")
        
        error = UnknownColumnError("Field 'unknown' not defined")
        self.assertEqual(str(error), "Field 'unknown' not defined")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_invalid_storage_data_error(self):
        """Тест InvalidStorageDataError."""
        with self.assertRaises(InvalidStorageDataError):
            raise InvalidStorageDataError("Invalid storage data")
        
        error = InvalidStorageDataError("Corrupted JSON file")
        self.assertEqual(str(error), "Corrupted JSON file")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_invalid_record_error(self):
        """Тест InvalidRecordError."""
        with self.assertRaises(InvalidRecordError):
            raise InvalidRecordError("Invalid record")
        
        error = InvalidRecordError("Record validation failed")
        self.assertEqual(str(error), "Record validation failed")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_invalid_age_error(self):
        """Тест InvalidAgeError."""
        with self.assertRaises(InvalidAgeError):
            raise InvalidAgeError("Invalid age")
        
        error = InvalidAgeError("Age must be between 0 and 120")
        self.assertEqual(str(error), "Age must be between 0 and 120")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_invalid_grade_error(self):
        """Тест InvalidGradeError."""
        with self.assertRaises(InvalidGradeError):
            raise InvalidGradeError("Invalid grade")
        
        error = InvalidGradeError("Grade must be between 0 and 5")
        self.assertEqual(str(error), "Grade must be between 0 and 5")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_invalid_name_error(self):
        """Тест InvalidNameError."""
        with self.assertRaises(InvalidNameError):
            raise InvalidNameError("Invalid name")
        
        error = InvalidNameError("Name must not be empty")
        self.assertEqual(str(error), "Name must not be empty")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_invalid_email_error(self):
        """Тест InvalidEmailError."""
        with self.assertRaises(InvalidEmailError):
            raise InvalidEmailError("Invalid email")
        
        error = InvalidEmailError("Email must contain @ and .")
        self.assertEqual(str(error), "Email must contain @ and .")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_duplicate_email_error(self):
        """Тест DuplicateEmailError."""
        with self.assertRaises(DuplicateEmailError):
            raise DuplicateEmailError("Duplicate email")
        
        error = DuplicateEmailError("Email already exists")
        self.assertEqual(str(error), "Email already exists")
        self.assertTrue(isinstance(error, DatabaseError))
    
    def test_all_exceptions_inherit_from_database_error(self):
        exceptions = [
            TableAlreadyExistsError,
            TableNotFoundError,
            RecordNotFoundError,
            MissingColumnError,
            UnknownColumnError,
            InvalidStorageDataError,
            InvalidRecordError,
            InvalidAgeError,
            InvalidGradeError,
            InvalidNameError,
            InvalidEmailError,
            DuplicateEmailError,
        ]
        
        for exc in exceptions:
            self.assertTrue(issubclass(exc, DatabaseError), f"{exc.__name__} не наследуется от DatabaseError")
if __name__ == "__main__":
    unittest.main()