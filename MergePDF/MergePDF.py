from PySide6.QtWidgets import QApplication
import sys

from ui.main_window import PDFMergerApp


def main() -> int:
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
