import sys
from PyQt5.QtWidgets import QApplication
from interface import CalorieApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalorieApp()
    window.show()
    sys.exit(app.exec_())
