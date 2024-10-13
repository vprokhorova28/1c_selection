import sqlite3
from datetime import datetime

DB_FILE = 'calories.db'

class Database:
    def __init__(self):
        self.connection = sqlite3.connect(DB_FILE)
        self.create_tables()

    def create_tables(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS dishes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    kcal REAL NOT NULL,
                    proteins REAL NOT NULL,
                    fats REAL NOT NULL,
                    carbs REAL NOT NULL
                )
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS calorie_log (
                    id INTEGER PRIMARY KEY,
                    dish_name TEXT NOT NULL,
                    grams INTEGER NOT NULL,
                    calories REAL NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY(dish_name) REFERENCES dishes(name)
                )
            ''')

    def add_dish(self, name, kcal, proteins, fats, carbs):
        try:
            with self.connection:
                self.connection.execute('''
                    INSERT INTO dishes (name, kcal, proteins, fats, carbs)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, kcal, proteins, fats, carbs))
        except sqlite3.IntegrityError:
            raise ValueError("Блюдо уже существует")

    def get_dishes(self):
        cursor = self.connection.execute('SELECT name, kcal, proteins, fats, carbs FROM dishes')
        return cursor.fetchall()

    def get_dish(self, name):
        cursor = self.connection.execute('SELECT kcal, proteins, fats, carbs FROM dishes WHERE name = ?', (name,))
        return cursor.fetchone()
    
    def update_dish(self, old_name, name, kcal, proteins, fats, carbs):
        with self.connection:
            self.connection.execute('''
                UPDATE dishes SET name = ?, kcal = ?, proteins = ?, fats = ?, carbs = ? WHERE name = ?
            ''', (name, kcal, proteins, fats, carbs, old_name))

    def track_calories(self, dish_name, grams, date):
        dish = self.get_dish(dish_name)
        if dish:
            kcal_per_100g = dish[0]
            total_calories = (kcal_per_100g / 100) * grams

            with self.connection:
                self.connection.execute('''
                    INSERT INTO calorie_log (dish_name, grams, calories, date) VALUES (?, ?, ?, ?)
                ''', (dish_name, grams, total_calories, date))

            return total_calories
        return 0

    def get_calories_by_date(self, date):
        cursor = self.connection.execute("SELECT SUM((grams * (SELECT kcal FROM dishes WHERE name=calorie_log.dish_name) / 100)) "
                            "FROM calorie_log WHERE date=?", (date,))
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0