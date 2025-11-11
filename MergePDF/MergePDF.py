import os
import sys
from PyPDF2 import PdfMerger

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QListWidget,
    QLabel,
    QLineEdit,
    QProgressBar,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtCore import Qt, QMimeData, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent


class PDFMergerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Unir PDFs")
        self.setGeometry(100, 100, 500, 400)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.pdf_list = QListWidget()
        self.pdf_list.setAcceptDrops(True)  # Habilita drag and drop
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

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(".pdf"):
                    self.pdf_list.addItem(file_path)
        else:
            event.ignore()

    def select_pdfs(self):
        pdf_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar arquivos PDF",
            "",
            "Arquivos PDF (*.pdf);;Todos os arquivos (*.*)",
        )
        if pdf_files:
            self.pdf_list.clear()
            self.pdf_list.addItems(pdf_files)

    def merge_pdfs(self):
        files_to_merge = [
            self.pdf_list.item(i).text() for i in range(self.pdf_list.count())
        ]

        if not files_to_merge:
            QMessageBox.critical(self, "Erro", "Nenhum arquivo PDF selecionado.")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "Salvar PDF unificado")
        if not save_dir:
            return

        output_filename = self.filename_input.text()
        if not output_filename:
            output_filename = "pdf_unificado"

        output_file = os.path.join(save_dir, f"{output_filename}.pdf")

        self.progress_bar.setValue(0)
        
        try:
            merger = PdfMerger()
            total_files = len(files_to_merge)

            for i, file in enumerate(files_to_merge):
                merger.append(file)
                self.progress_bar.setValue((i + 1) / total_files * 100)
                QApplication.processEvents()
            
            merger.write(output_file)
            merger.close()

            # Pergunta ao usuário se deseja continuar
            reply = QMessageBox.question(
                self,
                "Concluído",
                "PDFs unidos com sucesso! Deseja continuar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,  # Define "Não" como padrão
            )

            if reply == QMessageBox.No:
                self._open_output_folder(output_file)  # Abre a pasta de saída
                QApplication.quit()  # Fecha a aplicação
            else:
                self.progress_bar.setValue(0)  # Reseta a barra de progresso

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao unir os PDFs: {e}")
        # finally removido, pois a barra de progresso é resetada na condição do 'if' acima.

    def _open_output_folder(self, file_path):
        """Abre a pasta onde o arquivo foi salvo."""
        if file_path:
            folder_path = os.path.dirname(file_path)
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder_path])
            elif sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", folder_path])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec())
