class DatabaseError(Exception):
    pass


class TableAlreadyExistsError(DatabaseError):
    pass


class TableNotFoundError(DatabaseError):
    pass


class RecordNotFoundError(DatabaseError):
    pass


class InvalidRecordError(DatabaseError):
    pass


class InvalidAgeError(DatabaseError):
    pass


class InvalidGradeError(DatabaseError):
    pass


class InvalidNameError(DatabaseError):
    pass


class InvalidEmailError(DatabaseError):
    pass


class DuplicateEmailError(DatabaseError):
    pass