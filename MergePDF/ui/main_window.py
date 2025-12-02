from __future__ import annotations

import os
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QListWidget,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from services.merge import merge_pdfs
from utils.fs import open_folder


class PDFMergerApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unir PDFs")
        self.setGeometry(100, 100, 500, 400)
        self._init_ui()

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.pdf_list = QListWidget()
        self.pdf_list.setAcceptDrops(True)
        self.pdf_list.dragEnterEvent = self.dragEnterEvent
        self.pdf_list.dropEvent = self.dropEvent
        layout.addWidget(self.pdf_list)

        select_button = QPushButton("Selecionar PDFs")
        select_button.clicked.connect(self.select_pdfs)
        layout.addWidget(select_button)

        filename_label = QLabel("Nome do arquivo de saída:")
        layout.addWidget(filename_label)

        self.filename_input = QLineEdit("pdf_unificado")
        layout.addWidget(self.filename_input)

        merge_button = QPushButton("Juntar PDFs")
        merge_button.clicked.connect(self.merge_pdfs)
        layout.addWidget(merge_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        central_widget.setLayout(layout)

    # Drag & Drop
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(".pdf"):
                    self.pdf_list.addItem(file_path)
        else:
            event.ignore()

    # Ações
    def select_pdfs(self) -> None:
        pdf_files, _ = QFileDialog.getOpenFileNames(self, "Selecionar arquivos PDF", "", "Arquivos PDF (*.pdf);")
        if pdf_files:
            self.pdf_list.clear()
            self.pdf_list.addItems(pdf_files)

    def merge_pdfs(self) -> None:
        files_to_merge: List[str] = [self.pdf_list.item(i).text() for i in range(self.pdf_list.count())]
        if not files_to_merge:
            QMessageBox.critical(self, "Erro", "Nenhum arquivo PDF selecionado.")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "Salvar PDF unificado")
        if not save_dir:
            return

        output_filename = self.filename_input.text().strip() or "pdf_unificado"
        output_file = os.path.join(save_dir, f"{output_filename}.pdf")

        self.progress_bar.setValue(0)
        try:
            # Atualização simples de progresso por arquivo
            total = len(files_to_merge)
            for i, _ in enumerate(files_to_merge, start=1):
                self.progress_bar.setValue(int((i - 1) / total * 100))
                QApplication.processEvents()
            merge_pdfs(files_to_merge, output_file)
            self.progress_bar.setValue(100)

            reply = QMessageBox.question(
                self,
                "Concluído",
                "PDFs unidos com sucesso! Deseja continuar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                try:
                    open_folder(os.path.dirname(output_file))
                except Exception:
                    pass
                QApplication.quit()
            else:
                self.progress_bar.setValue(0)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao unir os PDFs: {e}")
