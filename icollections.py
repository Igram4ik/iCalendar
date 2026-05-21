from datetime import date, datetime
from istorage import (get_all_people, create_collection_db, get_collections,
                      get_collection, add_contribution_db, get_debtors)
from birthdays import next_birthday

def create_collection():
    people = get_all_people()
    if not people:
        print("Сначала добавьте хотя бы одного человека с днём рождения.")
        return
    print("Доступные именинники:")
    for i, p in enumerate(people, 1):
        print(f"  {i}. [{p['id']}] {p['name']} – {p['day']:02d}.{p['month']:02d}")
    choice = input("Выберите номер именинника: ").strip()
    try:
        idx = int(choice) - 1
        honoree = people[idx]
    except (ValueError, IndexError):
        print("Неверный выбор.")
        return
    description = input("Описание подарка (название): ").strip()
    if not description:
        print("Описание не может быть пустым.")
        return
    total_str = input("Общая сумма сбора (руб.): ").strip()
    try:
        total = float(total_str)
        if total <= 0:
            raise ValueError
    except:
        print("Сумма должна быть положительным числом.")
        return
    participants_raw = input("Список участников (имена через запятую): ").strip()
    if not participants_raw:
        print("Нужно указать хотя бы одного участника.")
        return
    participants_names = [name.strip() for name in participants_raw.split(",") if name.strip()]
    if not participants_names:
        print("Нет корректных имён.")
        return
    share = round(total / len(participants_names), 2)
    deadline_dt = next_birthday(honoree["day"], honoree["month"])
    deadline_str = deadline_dt.strftime("%d.%m.%Y")
    participants = [{"name": name, "obligation": share} for name in participants_names]
    new_id = create_collection_db(
        honoree["name"], description, total, deadline_str, participants
    )
    print(f"Сбор #{new_id} создан. Подарок: {description}, сумма {total:.2f} руб., дедлайн {deadline_str}.")
    print(f"Каждый участник должен внести по {share:.2f} руб.")

def make_contribution():
    collections = get_collections()
    if not collections:
        print("Нет активных сборов.")
        return
    print("Активные сборы:")
    for c in collections:
        print(f"  #{c['id']} – {c['description']} (для {c['honoree']}), дедлайн {c['deadline']}")
    cid_str = input("Введите ID сбора: ").strip()
    try:
        cid = int(cid_str)
    except ValueError:
        print("Некорректный ID.")
        return
    coll = get_collection(cid)
    if coll is None:
        print("Сбор не найден.")
        return
    print("Участники:")
    for p in coll["participants"]:
        debt = round(float(p["obligation"]) - float(p["paid"]), 2)
        print(f"  {p['name']}: должен {float(p['obligation']):.2f}, внёс {float(p['paid']):.2f}, долг {debt:.2f}")
    name = input("Имя участника, вносящего деньги: ").strip()
    participant = next((p for p in coll["participants"] if p["name"].lower() == name.lower()), None)
    if not participant:
        print("Такого участника нет в этом сборе.")
        return
    debt = round(float(participant["obligation"]) - float(participant["paid"]), 2)
    if debt <= 0:
        print("Участник уже полностью рассчитался.")
        return
    amount_str = input(f"Сумма взноса (можно частями, долг {debt:.2f}): ").strip()
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except:
        print("Некорректная сумма.")
        return
    if amount > debt:
        print(f"Сумма превышает долг ({debt:.2f}). Будет зачислено {debt:.2f}.")
        amount = debt
    add_contribution_db(cid, participant["name"], amount)
    print(f"Зачислено {amount:.2f} руб. от {participant['name']}.")

def view_collections():
    collections = get_collections()
    if not collections:
        print("Нет ни одного сбора.")
        return
    today = date.today()
    for c in collections:
        deadline = datetime.strptime(c["deadline"], "%d.%m.%Y").date()
        status = "Активен" if deadline >= today else "Просрочен"
        print(f"Сбор #{c['id']} [{status}]: {c['description']} для {c['honoree']}")
        print(f"  Общая сумма: {float(c['total_sum']):.2f} руб., дедлайн: {c['deadline']}")
        for p in c["participants"]:
            debt = round(float(p["obligation"]) - float(p["paid"]), 2)
            print(f"    {p['name']}: внёс {float(p['paid']):.2f} из {float(p['obligation']):.2f} (долг {debt:.2f})")
        print()

def view_debtors():
    debtors = get_debtors()
    if not debtors:
        print("Нет просроченных долгов.")
        return
    for d in debtors:
        debt = round(float(d["obligation"]) - float(d["paid"]), 2)
        print(f"Сбор #{d['id']} ({d['description']}) – {d['name']} должен {debt:.2f} руб. (просрочен с {d['deadline']})")