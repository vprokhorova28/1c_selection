from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QGroupBox,
                             QDialog, QInputDialog, QMessageBox, QListWidget, QDateEdit, QHBoxLayout)
from PyQt5.QtCore import QDate
import matplotlib.pyplot as plt
from db import Database

class CalorieApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор калорий")
        self.resize(800, 800)

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
        
        # добавление приема пищи: выбор блюда
        self.dish_list = QListWidget(self)
        self.populate_dish_list()
        food_layout.addWidget(QLabel("Выберите блюдо:"))
        food_layout.addWidget(self.dish_list)

        # поле, чтобы ввести граммы добавляемой пищи
        self.grams_input = QLineEdit(self)
        self.grams_input.setPlaceholderText("Введите количество граммов")
        food_layout.addWidget(self.grams_input)

        # поле выбора даты для добавляемой пищи
        self.date_input = QDateEdit(self)
        self.date_input.setDate(QDate.currentDate())
        food_layout.addWidget(QLabel("Выберите дату, к которой добавить прием пищи:"))
        food_layout.addWidget(self.date_input)

        # добавление приема пищи: кнопка
        add_calories_button = QPushButton('Добавить прием пищи', self)
        add_calories_button.clicked.connect(self.add_calories_from_dish)
        food_layout.addWidget(add_calories_button)

        food_group.setLayout(food_layout)
        layout.addWidget(food_group)

        # добавление нового блюда
        add_dish_button = QPushButton('Добавить новое блюдо', self)
        add_dish_button.clicked.connect(self.open_add_dish_dialog)
        layout.addWidget(add_dish_button)

        # поиск и редактирование блюд
        edit_dish_button = QPushButton('Поиск и редактирование блюд', self)
        edit_dish_button.clicked.connect(self.open_search_edit_dialog)
        layout.addWidget(edit_dish_button)

        # построение графика
        plot_button = QPushButton('Построить график', self)
        plot_button.clicked.connect(self.plot_calories)
        layout.addWidget(plot_button)

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
        data = self.db.get_data_by_date()
        dates = [item[0] for item in data]
        calories = [item[1] for item in data]

        plt.figure(figsize=(10, 6))
        plt.plot(dates, calories, marker='o')
        plt.title('Потребление калорий за время')
        plt.xlabel('Дата')
        plt.ylabel('Калории (ккал)')
        plt.show()


class AddDishDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новое блюдо")

        layout = QFormLayout()

        self.dish_name = QLineEdit(self)
        self.kcal = QLineEdit(self)
        self.proteins = QLineEdit(self)
        self.fats = QLineEdit(self)
        self.carbs = QLineEdit(self)

        layout.addRow("Название блюда", self.dish_name)
        layout.addRow("Калории (на 100г)", self.kcal)
        layout.addRow("Белки (г)", self.proteins)
        layout.addRow("Жиры (г)", self.fats)
        layout.addRow("Углеводы (г)", self.carbs)

        add_button = QPushButton("Добавить", self)
        add_button.clicked.connect(self.add_dish)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def add_dish(self):
        name = self.dish_name.text()
        try:
            kcal = float(self.kcal.text())
            proteins = float(self.proteins.text())
            fats = float(self.fats.text())
            carbs = float(self.carbs.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректные данные")
            return

        try:
            parent_db = self.parent().db
            parent_db.add_dish(name, kcal, proteins, fats, carbs)
            QMessageBox.information(self, "Успех", f"Блюдо {name} добавлено!")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))


class SearchEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поиск и редактирование блюд")

        layout = QVBoxLayout()

        self.search_line = QLineEdit(self)
        self.search_line.setPlaceholderText("Введите название блюда для поиска")
        layout.addWidget(self.search_line)

        self.dish_list = QListWidget(self)
        layout.addWidget(self.dish_list)

        self.search_line.textChanged.connect(self.update_dish_list)

        self.edit_button = QPushButton("Редактировать блюдо", self)
        self.edit_button.clicked.connect(self.open_edit_dish_dialog)
        layout.addWidget(self.edit_button)

        self.setLayout(layout)
        self.populate_dish_list()

    def populate_dish_list(self):
        self.dish_list.clear()
        dishes = self.parent().db.get_dishes()
        for dish in dishes:
            name, _, _, _, _ = dish
            self.dish_list.addItem(name)

    def update_dish_list(self):
        search_text = self.search_line.text().lower()
        self.dish_list.clear()
        dishes = self.parent().db.get_dishes()
        for dish in dishes:
            name, _, _, _, _ = dish
            if search_text in name.lower():
                self.dish_list.addItem(name)

    def open_edit_dish_dialog(self):
        selected_item = self.dish_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите блюдо из списка")
            return

        dish_name = selected_item.text()
        dish_data = self.parent().db.get_dish(dish_name)
        if not dish_data:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить данные блюда")
            return

        dialog = EditDishDialog(dish_name, dish_data, self.parent().db, self)
        dialog.exec_()


class EditDishDialog(QDialog):
    def __init__(self, dish_name, dish_data, db, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать блюдо")

        self.db = db
        self.dish_name = dish_name

        layout = QFormLayout()

        self.dish_name_edit = QLineEdit(self)
        self.dish_name_edit.setText(dish_name)
        self.kcal_edit = QLineEdit(self)
        self.kcal_edit.setText(str(dish_data[0]))
        self.proteins_edit = QLineEdit(self)
        self.proteins_edit.setText(str(dish_data[1]))
        self.fats_edit = QLineEdit(self)
        self.fats_edit.setText(str(dish_data[2]))
        self.carbs_edit = QLineEdit(self)
        self.carbs_edit.setText(str(dish_data[3]))

        layout.addRow("Название блюда", self.dish_name_edit)
        layout.addRow("Калории (на 100г)", self.kcal_edit)
        layout.addRow("Белки (г)", self.proteins_edit)
        layout.addRow("Жиры (г)", self.fats_edit)
        layout.addRow("Углеводы (г)", self.carbs_edit)

        save_button = QPushButton("Сохранить изменения", self)
        save_button.clicked.connect(self.save_dish)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_dish(self):
        name = self.dish_name_edit.text()
        try:
            kcal = float(self.kcal_edit.text())
            proteins = float(self.proteins_edit.text())
            fats = float(self.fats_edit.text())
            carbs = float(self.carbs_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректные данные")
            return

        self.db.update_dish(self.dish_name, name, kcal, proteins, fats, carbs)
        QMessageBox.information(self, "Успех", "Изменения сохранены!")
        self.accept()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    calorie_app = CalorieApp()
    calorie_app.show()
    sys.exit(app.exec_())
