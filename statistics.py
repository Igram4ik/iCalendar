from collections import defaultdict
from istorage import get_all_people

def export_statistics():
    people = get_all_people()
    if not people:
        print("Нет данных для статистики.")
        return
    month_count = defaultdict(int)
    for p in people:
        month_count[p["month"]] += 1
    print("Количество дней рождения по месяцам:")
    for m in range(1, 13):
        print(f"  Месяц {m:02d}: {month_count.get(m, 0)}")
    filename = "birthdays_stat.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Статистика дней рождения по месяцам:\n")
        for m in range(1, 13):
            f.write(f"Месяц {m:02d}: {month_count.get(m, 0)}\n")
    print(f"Статистика сохранена в файл {filename}")