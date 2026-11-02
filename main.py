# Copyright 2026 Igram4ik
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
