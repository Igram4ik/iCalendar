import sqlite3
import os
from datetime import date

_db = None

def init_database(db_type, **kwargs):
    global _db
    if db_type == "sqlite":
        db_path = kwargs.get("db_path", "data/calendar.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        _db = SQLiteDatabase(db_path)
    elif db_type == "mysql":
        import pymysql
        _db = MySQLDatabase(
            host=kwargs["host"],
            port=kwargs.get("port", 3306),
            user=kwargs["user"],
            password=kwargs["password"],
            database=kwargs["database"]
        )
    else:
        raise ValueError("Unsupported database type")
    _db.create_tables()

def get_db():
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db

# ----------------------------------------------------------------------
# Абстрактный интерфейс (реализован через одинаковые методы в классах)
# ----------------------------------------------------------------------

class SQLiteDatabase:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def create_tables(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                day INTEGER NOT NULL,
                month INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                honoree TEXT NOT NULL,
                description TEXT NOT NULL,
                total_sum REAL NOT NULL,
                deadline TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                obligation REAL NOT NULL,
                paid REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (collection_id) REFERENCES collections(id)
            );
        """)
        self.conn.commit()

    # --- Работа с людьми ---
    def get_all_people(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, day, month FROM people ORDER BY month, day")
        return [dict(row) for row in cur.fetchall()]

    def person_exists(self, name):
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM people WHERE name = ?", (name,))
        return cur.fetchone() is not None

    def add_person(self, name, day, month):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO people (name, day, month) VALUES (?,?,?)",
                    (name, day, month))
        self.conn.commit()
        return cur.lastrowid

    def delete_person(self, person_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM people WHERE id = ?", (person_id,))
        self.conn.commit()

    def get_people_in_month(self, month):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, day, month FROM people WHERE month = ? ORDER BY day", (month,))
        return [dict(row) for row in cur.fetchall()]

    # --- Сборы ---
    def create_collection(self, honoree, description, total_sum, deadline, participants):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO collections (honoree, description, total_sum, deadline) VALUES (?,?,?,?)",
                    (honoree, description, total_sum, deadline))
        coll_id = cur.lastrowid
        for p in participants:
            cur.execute("INSERT INTO participants (collection_id, name, obligation, paid) VALUES (?,?,?,0)",
                        (coll_id, p["name"], p["obligation"]))
        self.conn.commit()
        return coll_id

    def get_collections(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, honoree, description, total_sum, deadline FROM collections")
        collections = []
        for row in cur.fetchall():
            coll = dict(row)
            cur2 = self.conn.cursor()
            cur2.execute("SELECT name, obligation, paid FROM participants WHERE collection_id = ?", (coll["id"],))
            coll["participants"] = [dict(r) for r in cur2.fetchall()]
            collections.append(coll)
        return collections

    def get_collection(self, coll_id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, honoree, description, total_sum, deadline FROM collections WHERE id = ?", (coll_id,))
        row = cur.fetchone()
        if row is None:
            return None
        coll = dict(row)
        cur2 = self.conn.cursor()
        cur2.execute("SELECT name, obligation, paid FROM participants WHERE collection_id = ?", (coll_id,))
        coll["participants"] = [dict(r) for r in cur2.fetchall()]
        return coll

    def add_contribution(self, coll_id, participant_name, amount):
        cur = self.conn.cursor()
        cur.execute("UPDATE participants SET paid = paid + ? WHERE collection_id = ? AND name = ?",
                    (amount, coll_id, participant_name))
        self.conn.commit()

    def get_debtors(self):
        today = date.today().strftime("%d.%m.%Y")
        cur = self.conn.cursor()
        cur.execute("""
            SELECT c.id, c.description, c.deadline, p.name, p.obligation, p.paid
            FROM collections c
            JOIN participants p ON c.id = p.collection_id
            WHERE c.deadline < ? AND p.paid < p.obligation
        """, (today,))
        return [dict(row) for row in cur.fetchall()]

    def close(self):
        self.conn.close()


class MySQLDatabase:
    def __init__(self, host, port, user, password, database):
        import pymysql
        self.conn = pymysql.connect(
            host=host, port=port, user=user,
            password=password, database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                day INT NOT NULL,
                month INT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                honoree VARCHAR(255) NOT NULL,
                description VARCHAR(255) NOT NULL,
                total_sum DECIMAL(10,2) NOT NULL,
                deadline VARCHAR(10) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id INT AUTO_INCREMENT PRIMARY KEY,
                collection_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                obligation DECIMAL(10,2) NOT NULL,
                paid DECIMAL(10,2) NOT NULL DEFAULT 0,
                FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        self.conn.commit()

    def get_all_people(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, day, month FROM people ORDER BY month, day")
        return cur.fetchall()

    def person_exists(self, name):
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM people WHERE name = %s", (name,))
        return cur.fetchone() is not None

    def add_person(self, name, day, month):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO people (name, day, month) VALUES (%s,%s,%s)", (name, day, month))
        self.conn.commit()
        return cur.lastrowid

    def delete_person(self, person_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM people WHERE id = %s", (person_id,))
        self.conn.commit()

    def get_people_in_month(self, month):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, day, month FROM people WHERE month = %s ORDER BY day", (month,))
        return cur.fetchall()

    def create_collection(self, honoree, description, total_sum, deadline, participants):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO collections (honoree, description, total_sum, deadline) VALUES (%s,%s,%s,%s)",
            (honoree, description, total_sum, deadline)
        )
        coll_id = cur.lastrowid
        for p in participants:
            cur.execute(
                "INSERT INTO participants (collection_id, name, obligation, paid) VALUES (%s,%s,%s,0)",
                (coll_id, p["name"], p["obligation"])
            )
        self.conn.commit()
        return coll_id

    def get_collections(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, honoree, description, total_sum, deadline FROM collections")
        collections = []
        for row in cur.fetchall():
            coll = row
            cur2 = self.conn.cursor()
            cur2.execute("SELECT name, obligation, paid FROM participants WHERE collection_id = %s", (coll["id"],))
            coll["participants"] = cur2.fetchall()
            collections.append(coll)
        return collections

    def get_collection(self, coll_id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, honoree, description, total_sum, deadline FROM collections WHERE id = %s", (coll_id,))
        row = cur.fetchone()
        if row is None:
            return None
        coll = row
        cur2 = self.conn.cursor()
        cur2.execute("SELECT name, obligation, paid FROM participants WHERE collection_id = %s", (coll_id,))
        coll["participants"] = cur2.fetchall()
        return coll

    def add_contribution(self, coll_id, participant_name, amount):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE participants SET paid = paid + %s WHERE collection_id = %s AND name = %s",
            (amount, coll_id, participant_name)
        )
        self.conn.commit()

    def get_debtors(self):
        today = date.today().strftime("%d.%m.%Y")
        cur = self.conn.cursor()
        cur.execute("""
            SELECT c.id, c.description, c.deadline, p.name, p.obligation, p.paid
            FROM collections c
            JOIN participants p ON c.id = p.collection_id
            WHERE c.deadline < %s AND p.paid < p.obligation
        """, (today,))
        return cur.fetchall()

    def close(self):
        self.conn.close()


# ----- Глобальные функции-обёртки для совместимости с остальными модулями -----
def get_all_people():
    return get_db().get_all_people()

def person_exists(name):
    return get_db().person_exists(name)

def add_person_db(name, day, month):
    return get_db().add_person(name, day, month)

def delete_person_db(person_id):
    get_db().delete_person(person_id)

def get_people_in_month(month):
    return get_db().get_people_in_month(month)

def create_collection_db(honoree, description, total_sum, deadline, participants):
    return get_db().create_collection(honoree, description, total_sum, deadline, participants)

def get_collections():
    return get_db().get_collections()

def get_collection(coll_id):
    return get_db().get_collection(coll_id)

def add_contribution_db(coll_id, name, amount):
    get_db().add_contribution(coll_id, name, amount)

def get_debtors():
    return get_db().get_debtors()