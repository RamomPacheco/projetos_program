from PySide6.QtWidgets import QApplication
import sys

from ui.main_window import JanelaPrincipal


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
