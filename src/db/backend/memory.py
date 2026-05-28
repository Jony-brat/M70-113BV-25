type StudentRecord = tuple[int, str, str, int, float, str]

Students: list[StudentRecord] = []

_next_id: int = 1

def _generate_id() -> int:
    global _next_id
    current_id = _next_id
    _next_id += 1
    return current_id

def create_record(
    first_name: str,
    last_name: str,
    age: int,
    grade: float,
    email: str
) -> StudentRecord:

    if not first_name or not first_name.strip():
        raise ValueError("Имя не может быть пустым.")
    
    if len(first_name.strip()) < 2:
        raise ValueError("Имя должно содержать минимум 2 символа.")


    if not last_name or not last_name.strip():
        raise ValueError("Фамилия не может быть пустой.")
    
    if len(last_name.strip()) < 2:
        raise ValueError("Фамилия должна содержать минимум 2 символа.")


    if age < 0 or age > 120:
        raise ValueError("Возраст должен быть от 0 до 120 лет.")


    if grade < 0 or grade > 5:
        raise ValueError("Средний балл должен быть от 0 до 5.")


    if not email or not email.strip():
        raise ValueError("Email не может быть пустым.")
    
    if "@" not in email or "." not in email:
        raise ValueError("Введите корректный email (должен содержать @ и .)")


    if any(record[5].lower() == email.strip().lower() for record in Students):
        raise ValueError(f"Студент с email '{email}' уже существует.")


    new_record: StudentRecord = (
        _generate_id(),
        first_name.strip().capitalize(),
        last_name.strip().capitalize(),
        age,
        grade,
        email.strip().lower(),
    )


    Students.append(new_record)

    return new_record


def select_record(
    student_id: int | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    age: int | None = None,
    grade: float | None = None,
    email: str | None = None,
) -> list[StudentRecord]:

    if (
        student_id is None
        and first_name is None
        and last_name is None
        and age is None
        and grade is None
        and email is None
    ):
        return Students.copy()

    result: list[StudentRecord] = []

    for record in Students:
        if student_id is not None and record[0] != student_id:
            continue
        if first_name is not None and record[1].lower() != first_name.lower():
            continue
        if last_name is not None and record[2].lower() != last_name.lower():
            continue
        if age is not None and record[3] != age:
            continue
        if grade is not None and record[4] != grade:
            continue
        if email is not None and record[5].lower() != email.lower():
            continue
        result.append(record)

    return result


def update_record(
    student_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    age: int | None = None,
    grade: float | None = None,
    email: str | None = None,
) -> StudentRecord:

    for i, record in enumerate(Students):
        if record[0] == student_id:
            
            updated_record = list(record)

            if first_name is not None:
                if not first_name.strip():
                    raise ValueError("Имя не может быть пустым.")
                if len(first_name.strip()) < 2:
                    raise ValueError("Имя должно содержать минимум 2 символа.")
                updated_record[1] = first_name.strip().capitalize()

            if last_name is not None:
                if not last_name.strip():
                    raise ValueError("Фамилия не может быть пустой.")
                if len(last_name.strip()) < 2:
                    raise ValueError("Фамилия должна содержать минимум 2 символа.")
                updated_record[2] = last_name.strip().capitalize()

            if age is not None:
                if age < 0 or age > 120:
                    raise ValueError("Возраст должен быть от 0 до 120 лет.")
                updated_record[3] = age

            if grade is not None:
                if grade < 0 or grade > 5:
                    raise ValueError("Средний балл должен быть от 0 до 5.")
                updated_record[4] = grade

            if email is not None:
                if not email.strip():
                    raise ValueError("Email не может быть пустым.")
                if "@" not in email or "." not in email:
                    raise ValueError("Введите корректный email (должен содержать @ и .)")
                
                for j, other_record in enumerate(Students):
                    if j != i and other_record[5].lower() == email.strip().lower():
                        raise ValueError(f"Студент с email '{email}' уже существует.")
                updated_record[5] = email.strip().lower()

            new_record = tuple(updated_record)
            Students[i] = new_record
            return new_record

    raise ValueError(f"Студент с id={student_id} не найден.")


def delete_record(student_id: int) -> StudentRecord:
    for i, record in enumerate(Students):
        if record[0] == student_id:
            deleted_record = Students.pop(i)
            return deleted_record

    raise ValueError(f"Студент с id={student_id} не найден.")