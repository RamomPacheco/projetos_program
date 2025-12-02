"""
Este arquivo foi migrado para uma estrutura modular.

Novo ponto de entrada: app.py
Principais módulos:
- ui/main_window.py
- workers/process_worker.py
- services/*
- utils/*
- constants/*

Execute a aplicação com:
    python app.py
"""


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
