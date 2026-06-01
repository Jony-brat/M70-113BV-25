from .backend.memory import (
    create_record,
    select_record,
    update_record,
    delete_record,
)


def _print_menu() -> None:
    print("\n" + "=" * 60)
    print("          СИСТЕМА УПРАВЛЕНИЯ СТУДЕНТАМИ")
    print("=" * 60)
    print("1. Добавить студента")
    print("2. Показать всех студентов")
    print("3. Найти студентов по фильтру")
    print("4. Обновить информацию о студенте")
    print("5. Удалить студента")
    print("0. Выход")
    print("-" * 60)


def _read_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число.")


def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")


def _read_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("Ошибка: введите число (например: 4.5).")


def _read_optional_float(prompt: str) -> float | None:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            return float(raw)
        except ValueError:
            print("Ошибка: введите число или оставьте поле пустым.")


def _read_string(prompt: str, required: bool = True) -> str | None:
    """Читает строку из ввода."""
    value = input(prompt).strip()
    if required and not value:
        print("Ошибка: поле не может быть пустым.")
        return None
    return value if value else None


def _print_records(records: list[tuple[int, str, str, int, float, str]]) -> None:
    if not records:
        print("\nСтуденты не найдены.")
        return

    print("\n" + "=" * 100)
    print(f"{'ID':<5} {'Имя':<15} {'Фамилия':<15} {'Возраст':<8} {'Ср. балл':<10} {'Email':<30}")
    print("=" * 100)

    for record in records:
        email_display = record[5][:27] + "..." if len(record[5]) > 30 else record[5]
        print(f"{record[0]:<5} {record[1]:<15} {record[2]:<15} {record[3]:<8} {record[4]:<10.2f} {email_display:<30}")
    print("=" * 100)
    print(f"Всего студентов: {len(records)}")


def _grade_to_text(grade: float) -> str:
    if grade >= 4.5:
        return "Отлично"
    elif grade >= 3.5:
        return "Хорошо"
    elif grade >= 2.5:
        return "Удовлетворительно"
    else:
        return "Неудовлетворительно"


def _add_student() -> None:
    print("\nДОБАВЛЕНИЕ НОВОГО СТУДЕНТА")
    print("-" * 40)

    first_name = _read_string("Имя: ")
    if not first_name:
        return
    
    last_name = _read_string("Фамилия: ")
    if not last_name:
        return
    
    age = _read_int("Возраст: ")
    grade = _read_float("Средний балл (0-5): ")
    email = _read_string("Email: ")
    if not email:
        return

    try:
        record = create_record(first_name, last_name, age, grade, email)
        print("\nСтудент успешно добавлен!")
        print(f"   ID: {record[0]}")
        print(f"   {record[1]} {record[2]}, {record[3]} лет")
        print(f"   Средний балл: {record[4]:.2f} ({_grade_to_text(record[4])})")
        print(f"   Email: {record[5]}")
    except ValueError as exc:
        print(f"\nОшибка: {exc}")


def _show_all_students() -> None:
    print("\nВСЕ СТУДЕНТЫ")
    _print_records(select_record())


def _find_students_by_filter() -> None:
    print("\nПОИСК СТУДЕНТОВ")
    print("(оставьте поле пустым, чтобы пропустить фильтр)")
    print("-" * 40)

    student_id = _read_optional_int("ID студента: ")
    first_name = input("Имя: ").strip() or None
    last_name = input("Фамилия: ").strip() or None
    age = _read_optional_int("Возраст: ")
    grade = _read_optional_float("Средний балл: ")
    email = input("Email: ").strip() or None

    records = select_record(
        student_id=student_id,
        first_name=first_name,
        last_name=last_name,
        age=age,
        grade=grade,
        email=email,
    )

    _print_records(records)


def _update_student() -> None:
    print("\nОБНОВЛЕНИЕ ИНФОРМАЦИИ О СТУДЕНТЕ")
    print("-" * 40)

    student_id = _read_int("Введите ID студента для обновления: ")
    existing = select_record(student_id=student_id)
    if not existing:
        print(f"\nСтудент с ID {student_id} не найден.")
        return

    print("\nТекущая информация:")
    print(f"   {existing[0][1]} {existing[0][2]}, {existing[0][3]} лет")
    print(f"   Средний балл: {existing[0][4]:.2f}")
    print(f"   Email: {existing[0][5]}")
    
    print("\n(оставьте поле пустым, чтобы не менять)")
    print("-" * 40)

    first_name = input("Новое имя: ").strip() or None
    last_name = input("Новая фамилия: ").strip() or None
    
    age = _read_optional_int("Новый возраст: ")
    
    grade = _read_optional_float("Новый средний балл: ")
    
    email = input("Новый email: ").strip() or None

    try:
        updated = update_record(student_id, first_name, last_name, age, grade, email)
        print("\nИнформация о студенте успешно обновлена!")
        print(f"   {updated[1]} {updated[2]}, {updated[3]} лет")
        print(f"   Средний балл: {updated[4]:.2f} ({_grade_to_text(updated[4])})")
        print(f"   Email: {updated[5]}")
    except ValueError as exc:
        print(f"\nОшибка: {exc}")


def _delete_student() -> None:
    print("\nУДАЛЕНИЕ СТУДЕНТА")
    print("-" * 40)

    student_id = _read_int("Введите ID студента для удаления: ")
    existing = select_record(student_id=student_id)
    if not existing:
        print(f"\nСтудент с ID {student_id} не найден.")
        return

    print("\nСтудент для удаления:")
    print(f"   {existing[0][1]} {existing[0][2]}, {existing[0][3]} лет")
    print(f"   Средний балл: {existing[0][4]:.2f}")
    print(f"   Email: {existing[0][5]}")
    
    confirm = input("\nВы уверены, что хотите удалить этого студента? (да/нет): ").strip().lower()

    if confirm in ("да", "yes", "y", "д"):
        try:
            deleted = delete_record(student_id)
            print(f"\nСтудент успешно удалён: {deleted[1]} {deleted[2]}")
        except ValueError as exc:
            print(f"\nОшибка: {exc}")
    else:
        print("\nУдаление отменено.")


def run() -> None:
    while True:
        _print_menu()
        action = input("\nВыберите действие (0-5): ").strip()

        if action == "1":
            _add_student()
        elif action == "2":
            _show_all_students()
        elif action == "3":
            _find_students_by_filter()
        elif action == "4":
            _update_student()
        elif action == "5":
            _delete_student()
        elif action == "0":
            print("\nДо свидания! Спасибо за использование системы.")
            break
        else:
            print("\nНеизвестная команда. Пожалуйста, выберите действие от 0 до 5.")
        
        input("\nНажмите Enter для продолжения...")