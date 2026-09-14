import sys
from PySide6.QtWidgets import QApplication
from vectorforge.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VectorForge Vision Engine 12.0")
    app.setOrganizationName("VectorForge")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
