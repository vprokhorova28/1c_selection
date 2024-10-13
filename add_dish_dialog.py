from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox


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