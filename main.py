from ui import main_menu
from istorage import init_database

if __name__ == "__main__":
    # print("Выберите тип базы данных:")
    # print("1. SQLite (файл data/calendar.db)")
    # print("2. MySQL")
    # choice = input("Ваш выбор (1/2): ").strip()
    # if choice == "2":
    #     host = input("MySQL хост [localhost]: ").strip() or "localhost"
    #     port = int(input("Порт [3306]: ").strip() or 3306)
    #     user = input("Пользователь [root]: ").strip() or "root"
    #     password = input("Пароль: ").strip()
    #     database = input("Имя базы данных [calendar]: ").strip() or "calendar"
    #     init_database("mysql", host=host, port=port, user=user,
    #                   password=password, database=database)
    # else:
    init_database("sqlite", db_path="data/icalendar.db")
    main_menu()