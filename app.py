from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QGroupBox,
                             QDialog, QInputDialog, QMessageBox, QListWidget, QDateEdit, QHBoxLayout)
from PyQt5.QtCore import QDate

from db import Database
from search_edit_dialog import SearchEditDialog
from add_dish_dialog import AddDishDialog

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class CalorieApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор калорий")
        self.resize(1000, 1000)

        self.db = Database()

        layout = QVBoxLayout()

        # Блок для отображения КБЖУ за выбранную дату
        kbju_group = QGroupBox("КБЖУ за выбранную дату")
        kbju_layout = QVBoxLayout()
        self.check_date_label = QLabel("Выберите дату для просмотра потребленного КБЖУ:")
        kbju_layout.addWidget(self.check_date_label)

        self.check_date_input = QDateEdit(self)
        self.check_date_input.setDate(QDate.currentDate())
        kbju_layout.addWidget(self.check_date_input)

        check_kbju_button = QPushButton('Показать КБЖУ', self)
        check_kbju_button.clicked.connect(self.show_kbju_for_date)
        kbju_layout.addWidget(check_kbju_button)

        kbju_group.setLayout(kbju_layout)
        layout.addWidget(kbju_group)

        # Блок для построения графика динамики
        dynamic_plot_group = QGroupBox("Динамика потребляемых калорий")
        dynamic_plot_layout = QVBoxLayout()

        date_layout = QHBoxLayout()
        self.start_date_input = QDateEdit(self)
        self.start_date_input.setDate(QDate.currentDate().addDays(-7))
        date_layout.addWidget(QLabel("Начальная дата:"))
        date_layout.addWidget(self.start_date_input)

        self.end_date_input = QDateEdit(self)
        self.end_date_input.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Конечная дата:"))
        date_layout.addWidget(self.end_date_input)

        plot_button = QPushButton('Посмотреть динамику потребляемых калорий', self)
        plot_button.clicked.connect(self.plot_calories)

        dynamic_plot_layout.addWidget(plot_button)
        dynamic_plot_layout.addLayout(date_layout)

        dynamic_plot_group.setLayout(dynamic_plot_layout)
        layout.addWidget(dynamic_plot_group)

        # Блок для отображения потребленных калорий сегодня
        summary_group = QGroupBox("Потреблено сегодня:")
        summary_layout = QVBoxLayout()
        self.summary_label = QLabel("Ккал: 0\n"
                                     "Б: 0 г,\nЖ: 0 г,\nУ: 0 г\n", self)
        summary_layout.addWidget(self.summary_label)
        self.update_today_summary()
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Блок для добавления приема пищи
        food_group = QGroupBox("Добавление приема пищи")
        food_layout = QVBoxLayout()
        
        # Поле для поиска блюда
        self.search_line = QLineEdit(self)
        self.search_line.setPlaceholderText("Поиск блюда...")
        self.search_line.textChanged.connect(self.filter_dish_list)
        food_layout.addWidget(self.search_line)

        # Список для выбора блюда
        self.dish_list = QListWidget(self)
        self.populate_dish_list()
        food_layout.addWidget(QLabel("Выберите блюдо:"))
        food_layout.addWidget(self.dish_list)

        # Поле, чтобы ввести граммы добавляемой пищи
        self.grams_input = QLineEdit(self)
        self.grams_input.setPlaceholderText("Введите количество граммов")
        food_layout.addWidget(self.grams_input)

        # Поле выбора даты для добавляемой пищи
        self.date_input = QDateEdit(self)
        self.date_input.setDate(QDate.currentDate())
        food_layout.addWidget(QLabel("Выберите дату, к которой добавить прием пищи:"))
        food_layout.addWidget(self.date_input)

        # Добавление приема пищи: кнопка
        add_calories_button = QPushButton('Добавить прием пищи', self)
        add_calories_button.clicked.connect(self.add_calories_from_dish)
        food_layout.addWidget(add_calories_button)

        food_group.setLayout(food_layout)
        layout.addWidget(food_group)

        # Добавление нового блюда
        add_dish_button = QPushButton('Добавить новое блюдо', self)
        add_dish_button.clicked.connect(self.open_add_dish_dialog)
        layout.addWidget(add_dish_button)

        # Поиск и редактирование блюд
        edit_dish_button = QPushButton('Поиск и редактирование блюд', self)
        edit_dish_button.clicked.connect(self.open_search_edit_dialog)
        layout.addWidget(edit_dish_button)

        self.setLayout(layout)

    def show_kbju_for_date(self):
        selected_date = self.check_date_input.date().toString("yyyy-MM-dd")
        total_calories, total_proteins, total_fats, total_carbs = self.db.get_data_by_date(selected_date)
        
        result_message = (
            f"Потреблено за {selected_date}:\n"
            f"Калории: {total_calories:.2f} ккал\n"
            f"Белки: {total_proteins:.2f} г\n"
            f"Жиры: {total_fats:.2f} г\n"
            f"Углеводы: {total_carbs:.2f} г"
        )

        QMessageBox.information(self, "КБЖУ за выбранную дату", result_message)

    def update_today_summary(self):
        today_date = QDate.currentDate().toString("yyyy-MM-dd")
        total_calories, total_proteins, total_fats, total_carbs = self.db.get_data_by_date(today_date)
        self.summary_label.setText(
            f"Ккал: {total_calories:.2f}\n"
            f"Б: {total_proteins:.2f} г,\nЖ: {total_fats:.2f} г,\nУ: {total_carbs:.2f} г\n"
        )

    def populate_dish_list(self):
        self.dish_list.clear()
        dishes = self.db.get_dishes()
        for dish in dishes:
            name, _, _, _, _ = dish
            self.dish_list.addItem(name)

    def add_calories_from_dish(self):
        selected_item = self.dish_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите блюдо из списка.")
            return

        dish_name = selected_item.text()
        grams_input = self.grams_input.text()
        try:
            grams = float(grams_input)
            if grams <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное количество граммов.")
            return

        date = self.date_input.date().toString("yyyy-MM-dd")
        total_calories = self.db.track_calories(dish_name, grams, date)
        QMessageBox.information(self, "Результат", f"{total_calories:.2f} ккал добавлено из {dish_name}.")
        self.update_today_summary()

    def open_add_dish_dialog(self):
        dialog = AddDishDialog(self)
        dialog.exec_()
        self.populate_dish_list()

    def open_search_edit_dialog(self):
        dialog = SearchEditDialog(self)
        dialog.exec_()
        self.populate_dish_list()

    def plot_calories(self):
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")

        calorie_data = self.db.get_calorie_data_by_date_range(start_date, end_date)
        if not calorie_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных за выбранный период.")
            return

        df = pd.DataFrame(calorie_data, columns=["date", "total_kcal", "total_proteins", "total_fats", "total_carbs"])

        sns.set_palette("Set2")

        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x="date", y="total_kcal", label="Калории", marker='o')
        sns.lineplot(data=df, x="date", y="total_proteins", label="Белки", marker='o')
        sns.lineplot(data=df, x="date", y="total_fats", label="Жиры", marker='o')
        sns.lineplot(data=df, x="date", y="total_carbs", label="Углеводы", marker='o')

        plt.title('Динамика потребляемых КБЖУ')
        plt.xlabel('Дата')
        plt.ylabel('Количество (г)')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()
    
    def filter_dish_list(self):
            search_text = self.search_line.text().lower()
            self.dish_list.clear()
            dishes = self.db.get_dishes()
            for dish in dishes:
                name, _, _, _, _ = dish
                if search_text in name.lower():
                    self.dish_list.addItem(name)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    calorie_app = CalorieApp()
    calorie_app.show()
    sys.exit(app.exec_())
