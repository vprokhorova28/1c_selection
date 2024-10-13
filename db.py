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

    def get_data_by_date(self, date):
        cursor = self.connection.execute("""
            SELECT 
                SUM(grams * (d.kcal / 100)) AS total_kcal,
                SUM(grams * (d.proteins / 100)) AS total_proteins,
                SUM(grams * (d.fats / 100)) AS total_fats,
                SUM(grams * (d.carbs / 100)) AS total_carbs
            FROM 
                calorie_log cl
            JOIN 
                dishes d ON cl.dish_name = d.name
            WHERE 
                cl.date = ?
        """, (date,))

        result = cursor.fetchone()
        total_kcal = result[0] if result[0] is not None else 0
        total_proteins = result[1] if result[1] is not None else 0
        total_fats = result[2] if result[2] is not None else 0
        total_carbs = result[3] if result[3] is not None else 0

        return total_kcal, total_proteins, total_fats, total_carbs
    
    def delete_dish(self, dish_name):
        with self.connection:
            # Удаление записей из calorie_log, связанных с блюдом
            self.connection.execute('''
                DELETE FROM calorie_log WHERE dish_name = ?
            ''', (dish_name,))
            # Удаление блюда из dishes
            self.connection.execute('''
                DELETE FROM dishes WHERE name = ?
            ''', (dish_name,))

    def get_calorie_data_by_date_range(self, start_date, end_date):
        cursor = self.connection.execute("""
            SELECT 
                cl.date,
                SUM(cl.grams * (d.kcal / 100)) AS total_kcal,
                SUM(cl.grams * (d.proteins / 100)) AS total_proteins,
                SUM(cl.grams * (d.fats / 100)) AS total_fats,
                SUM(cl.grams * (d.carbs / 100)) AS total_carbs
            FROM 
                calorie_log cl
            JOIN 
                dishes d ON cl.dish_name = d.name
            WHERE 
                cl.date BETWEEN ? AND ?
            GROUP BY 
                cl.date
            ORDER BY 
                cl.date
        """, (start_date, end_date))

        return cursor.fetchall()
