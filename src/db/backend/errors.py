class StudentTableError(Exception):
    """Базовый класс для ошибок, связанных с таблицей Student."""
    pass


class InvalidAgeError(StudentTableError):
    """Ошибка, возникающая при попытке создать запись с некорректным возрастом."""
    pass


class InvalidGradeError(StudentTableError):
    """Ошибка, возникающая при попытке создать запись с некорректным средним баллом."""
    pass


class InvalidNameError(StudentTableError):
    """Ошибка, возникающая при попытке создать запись с некорректным именем или фамилией."""
    pass


class InvalidEmailError(StudentTableError):
    """Ошибка, возникающая при попытке создать запись с некорректным email."""
    pass


class DuplicateEmailError(StudentTableError):
    """Ошибка, возникающая при попытке создать запись с уже существующим email."""
    pass


class RecordNotFoundError(StudentTableError):
    """Ошибка, возникающая при обращении к несуществующей записи."""
    pass