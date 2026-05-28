class DatabaseError(Exception):
    """Базовый класс для ошибок базы данных."""
    pass


class TableAlreadyExistsError(DatabaseError):
    """Ошибка, возникающая при попытке создать уже существующую таблицу."""
    pass


class TableNotFoundError(DatabaseError):
    """Ошибка, возникающая при обращении к несуществующей таблице."""
    pass


class RecordNotFoundError(DatabaseError):
    """Ошибка, возникающая при обращении к несуществующей записи."""
    pass


class MissingColumnError(DatabaseError):
    """Ошибка, возникающая при отсутствии обязательного поля в записи."""
    pass


class UnknownColumnError(DatabaseError):
    """Ошибка, возникающая при использовании поля, которого нет в схеме."""
    pass


class InvalidStorageDataError(DatabaseError):
    """Ошибка, возникающая при чтении повреждённых данных из файла."""
    pass


class InvalidRecordError(DatabaseError):
    """Ошибка, возникающая при некорректной записи."""
    pass


class InvalidAgeError(DatabaseError):
    """Ошибка, возникающая при некорректном возрасте."""
    pass


class InvalidGradeError(DatabaseError):
    """Ошибка, возникающая при некорректном среднем балле."""
    pass


class InvalidNameError(DatabaseError):
    """Ошибка, возникающая при некорректном имени или фамилии."""
    pass


class InvalidEmailError(DatabaseError):
    """Ошибка, возникающая при некорректном email."""
    pass


class DuplicateEmailError(DatabaseError):
    """Ошибка, возникающая при дублировании email."""
    pass