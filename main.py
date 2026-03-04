from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QShortcut, QKeySequence
import sys
import pyautogui as pg


class Fenster(QWidget):
    def __init__(self):
        super().__init__()

        shortcut = QShortcut(QKeySequence("Ctrl+Alt+f5"), self)
        shortcut.activated.connect(self.screenshot)

        shortcut = QShortcut(QKeySequence("F4"), self)
        shortcut.activated.connect(self.check_screenshot)

    def screenshot(self):
        image = pg.screenshot()

        image.save("test.png")
        print("screenshot wurde gemacht")

    def check_screenshot(self):
        print("F4 gedrückt!")


app = QApplication(sys.argv)
window = Fenster()
window.show()
sys.exit(app.exec())
