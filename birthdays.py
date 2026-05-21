from datetime import date
from istorage import (get_all_people, person_exists, add_person_db,
                      delete_person_db, get_people_in_month)

def parse_date(text):
    try:
        day, month = map(int, text.split("."))
        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError
        return day, month
    except:
        raise ValueError("Формат даты должен быть ДД.ММ, например 15.05")

def next_birthday(day, month):
    today = date.today()
    try:
        bday_this_year = date(today.year, month, day)
    except ValueError:
        if day == 29 and month == 2:
            bday_this_year = date(today.year, 2, 28)
        else:
            raise
    if bday_this_year < today:
        try:
            bday_next = date(today.year + 1, month, day)
        except ValueError:
            if day == 29 and month == 2:
                bday_next = date(today.year + 1, 2, 28)
            else:
                raise
        return bday_next
    return bday_this_year

def add_person():
    name = input("Имя человека: ").strip()
    if not name:
        print("Имя не может быть пустым.")
        return
    if person_exists(name):
        print("Человек с таким именем уже существует.")
        return
    date_str = input("Дата рождения (ДД.ММ): ").strip()
    try:
        day, month = parse_date(date_str)
    except ValueError as e:
        print(f"Ошибка: {e}")
        return
    add_person_db(name, day, month)
    print(f"Добавлен: {name}, {day:02d}.{month:02d}")

def view_all_people():
    people = get_all_people()
    if not people:
        print("Список людей пуст.")
        return
    print("Все люди с днями рождения:")
    for i, p in enumerate(people, 1):
        print(f"  {i}. [{p['id']}] {p['name']} – {p['day']:02d}.{p['month']:02d}")

def list_birthdays_in_month(month=None):
    if month is None:
        month = date.today().month
    people = get_people_in_month(month)
    if not people:
        print(f"В месяце {month} дней рождения нет.")
        return
    print(f"Дни рождения в месяце {month}:")
    for p in people:
        print(f"  {p['day']:02d}.{p['month']:02d} – {p['name']}")

def delete_person():
    people = get_all_people()
    if not people:
        print("Список пуст.")
        return
    view_all_people()
    idx = input("Введите ID человека для удаления (или Enter для отмены): ").strip()
    if not idx:
        return
    try:
        pid = int(idx)
        delete_person_db(pid)
        print("Запись удалена.")
    except ValueError:
        print("Некорректный ID.")