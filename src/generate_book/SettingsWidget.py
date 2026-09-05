from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QGuiApplication

from src.generate_book.ui.SettingsWidget import Ui_SettingsWidget
from PyQt5.QtWidgets import QWidget, QApplication
import sys


class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)
        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        self.setStyleSheet("background: rgb(230, 230, 230); border: 1px solid rgb(0, 0, 0); border-radius: 5px;")


if __name__ == "__main__":
    # 高DPI支持
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    try:
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        pass
    app = QApplication(sys.argv)
    widget = SettingsWidget()
    widget.show()
    sys.exit(app.exec_())