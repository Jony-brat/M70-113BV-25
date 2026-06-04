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


class DatabaseError(Exception):
    """Базовый класс для ошибок базы данных."""
    pass


class TableAlreadyExistsError(DatabaseError):
    """Ошибка, возникающая при попытке создать уже существующую таблицу."""
    pass


class TableNotFoundError(DatabaseError):
    """Ошибка, возникающая при обращении к несуществующей таблице."""
    pass


class MissingColumnError(DatabaseError):
    """Ошибка, возникающая при отсутствии обязательного поля в записи."""
    pass


class UnknownColumnError(DatabaseError):
    """Ошибка, возникающая при использовании поля, которого нет в схеме таблицы."""
    pass


class InvalidStorageDataError(DatabaseError):
    """Ошибка, возникающая при чтении повреждённых данных из файла."""
    pass