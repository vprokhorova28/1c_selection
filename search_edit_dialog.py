from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox, QFormLayout

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

        self.delete_button = QPushButton("Удалить блюдо", self)
        self.delete_button.clicked.connect(self.delete_dish)
        layout.addWidget(self.delete_button)

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
        if dialog.exec_() == QDialog.Accepted:
            self.populate_dish_list()
            self.accept()

    def delete_dish(self):
        selected_item = self.dish_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите блюдо из списка")
            return

        dish_name = selected_item.text()
        reply = QMessageBox.question(self, "Подтверждение", f"Вы уверены, что хотите удалить блюдо '{dish_name}'?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.parent().db.delete_dish(dish_name)
            self.populate_dish_list()
            self.accept()


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