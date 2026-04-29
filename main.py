import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow


def main():
    """Initialize and run the CPU Monitor application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
