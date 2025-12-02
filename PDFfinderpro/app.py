from PySide6.QtWidgets import QApplication
import sys

# Importa a janela da estrutura modularizada
from ui.main_window import MainWindow  # noqa: E402


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
