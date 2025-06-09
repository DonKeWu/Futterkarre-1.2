# test_fuettern.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow
from views.fuettern_seite import FuetternSeite


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test: Fütterungsseite")
        self.setFixedSize(1024, 600)

        self.fuettern = FuetternSeite(parent=self)
        self.setCentralWidget(self.fuettern)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
