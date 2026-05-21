import birthdays
import icollections
import statistics

def main_menu():
    while True:
        print("\n===== Календарь-помощник =====")
        print("1. Управление днями рождения 🎊")
        print("2. Управление сборами 🎁")
        print("3. Статистика 📊")
        print("0. Выход 💠")
        choice = input("Ваш выбор: ").strip()
        if choice == "1":
            birthday_menu()
        elif choice == "2":
            collection_menu()
        elif choice == "3":
            statistics.export_statistics()
        elif choice == "0":
            print("Выход...")
            break
        else:
            print("Неверный ввод.")

def birthday_menu():
    while True:
        print("\n--- Дни рождения ---")
        print("1. Добавить человека 🆕")
        print("2. Показать все записи #️⃣")
        print("3. Дни рождения в текущем месяце 🎉")
        print("4. Дни рождения в выбранном месяце")
        print("5. Удалить человека ⭕️")
        print("0. Назад")
        choice = input("Выбор: ").strip()
        if choice == "1":
            birthdays.add_person()
        elif choice == "2":
            birthdays.view_all_people()
        elif choice == "3":
            birthdays.list_birthdays_in_month()
        elif choice == "4":
            try:
                m = int(input("Введите номер месяца (1-12): ").strip())
                if 1 <= m <= 12:
                    birthdays.list_birthdays_in_month(m)
                else:
                    print("Некорректный месяц.")
            except ValueError:
                print("Нужно ввести число.")
        elif choice == "5":
            birthdays.delete_person()
        elif choice == "0":
            break
        else:
            print("Неверный выбор.")

def collection_menu():
    while True:
        print("\n--- Сборы на подарки ---")
        print("1. Создать сбор")
        print("2. Внести взнос")
        print("3. Просмотреть все сборы")
        print("4. Просмотреть должников (просроченные)")
        print("0. Назад")
        choice = input("Выбор: ").strip()
        if choice == "1":
            icollections.create_collection()
        elif choice == "2":
            icollections.make_contribution()
        elif choice == "3":
            icollections.view_collections()
        elif choice == "4":
            icollections.view_debtors()
        elif choice == "0":
            break
        else:
            print("Неверный выбор.")