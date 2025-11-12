import sys
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

# Import controller
from controllers.main_controller import MainController


HERE = Path(__file__).parent
UI_PATH = HERE / 'ui' / 'main_window.ui'

def load_ui(path):
    loader = QUiLoader()
    ui_file = QFile(str(path))
    ui_file.open(QFile.ReadOnly)
    ui = loader.load(ui_file)
    ui_file.close()
    return ui


def main():
    app = QtWidgets.QApplication(sys.argv)
    # Los estilos se aplican inline en cada widget, no necesitamos QSS externo

    ui = load_ui(UI_PATH)
    controller = MainController(ui)
    ui.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
