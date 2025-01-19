import sys
import os
import ocrmypdf
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QWidget,
    QProgressBar,
    QMessageBox,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QCursor
import traceback
import time
import subprocess


# Constantes
WINDOW_TITLE = "Aplicativo OCR para PDF"
SELECT_PDF_TEXT = "Selecionar PDF"
SELECT_OUTPUT_TEXT = "Salvar como..."
START_OCR_TEXT = "Iniciar OCR"
DEFAULT_TEXT = "Selecione um arquivo PDF para aplicar OCR"
RESULT_TEXT = "Resultado do OCR aparecerá aqui"
PROCESSING_TEXT = "Processando..."
COMPLETED_TEXT = "OCR concluído com sucesso!"


class OCRPDFWorker(QThread):
    """Thread para realizar o OCR em um PDF."""

    progress = Signal(int)
    result = Signal(str)

    def __init__(self, input_pdf, output_pdf):
        """Inicializa a thread de OCR."""
        super().__init__()
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf

    def run(self):
        """Executa o processo de OCR."""
        try:
            self.progress.emit(10)  # Simula início do processo de OCR
            # Você pode substituir esse trecho por etapas específicas,
            # se houver no seu caso, não existe, então ele apenas
            #  simulará o progresso
            ocrmypdf.ocr(self.input_pdf, self.output_pdf, lang="por")
            self.progress.emit(90)  # Simula fim do processo de OCR
            time.sleep(0.5)
            self.progress.emit(100)
            self.result.emit(f"{COMPLETED_TEXT} Arquivo salvo em:"
                             f"{self.output_pdf}")
        except Exception as e:
            error_msg = f"Erro ao processar o OCR: {e}\n"
            f"{traceback.format_exc()}"
            self.result.emit(error_msg)


class OCRPDFApp(QMainWindow):
    """Janela principal do aplicativo OCR."""

    def __init__(self):
        """Inicializa a janela principal."""
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, 600, 300)

        self.input_pdf = None
        self.output_pdf = None
        self.worker = None

        self._create_widgets()

    def _create_widgets(self):
        """Cria os widgets da interface."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.label = QLabel(DEFAULT_TEXT)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.select_button = QPushButton(SELECT_PDF_TEXT)
        self.select_button.clicked.connect(self.select_pdf)
        layout.addWidget(self.select_button)

        self.select_output_button = QPushButton(SELECT_OUTPUT_TEXT)
        self.select_output_button.clicked.connect(self.select_output)
        self.select_output_button.setEnabled(False)  # Desabilita inicialmente
        layout.addWidget(self.select_output_button)

        self.start_button = QPushButton(START_OCR_TEXT)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_ocr)
        layout.addWidget(self.start_button)

        self.result_label = QLabel(RESULT_TEXT)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

    def select_pdf(self):
        """Abre o diálogo para selecionar o PDF."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar PDF", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.input_pdf = file_path
            self.label.setText(f"PDF selecionado: {file_path}")
            self.select_output_button.setEnabled(True)
            # Habilita o botão de saída
            self.start_button.setEnabled(
                False
            )  # Desabilita o botão de iniciar até definir o local de saída

    def select_output(self):
        """Abre o diálogo para selecionar onde salvar o PDF."""
        if self.input_pdf:
            base_name = os.path.splitext(self.input_pdf)[0]
            self.output_pdf, _ = QFileDialog.getSaveFileName(
                self, "Salvar PDF OCR",
                base_name + "_ocr.pdf",
                "PDF Files (*.pdf)"
            )
            if self.output_pdf:
                self.label.setText(
                    f"PDF selecionado: {self.input_pdf}\nArquivo de saída:"
                    f"{self.output_pdf}"
                )
                self.start_button.setEnabled(True)

    def start_ocr(self):
        """Inicia o processo de OCR em uma thread."""
        if self.input_pdf and self.output_pdf:
            try:
                self._validate_output_path()
                self._disable_buttons(True)
                self.progress_bar.setValue(0)
                self.result_label.setText(PROCESSING_TEXT)
                QApplication.setOverrideCursor(
                    QCursor(Qt.CursorShape.WaitCursor)
                )  # Coloca cursor de espera

                self.worker = OCRPDFWorker(self.input_pdf, self.output_pdf)
                self.worker.progress.connect(self.progress_bar.setValue)
                self.worker.result.connect(self.display_result)
                self.worker.start()
            except Exception as e:
                self.display_error(f"Erro ao iniciar OCR: {e}")
                self._disable_buttons(False)

    def display_result(self, result):
        """Exibe o resultado do processo de OCR e pergunta se fecha."""
        self.result_label.setText(result)
        self._disable_buttons(False)
        QApplication.restoreOverrideCursor()

        reply = QMessageBox.question(
            self,
            "Conclusão",
            "OCR concluído. Deseja Continuar ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            # Tratamento da resposta "Não"
            self._open_output_folder()
            QApplication.quit()

    def display_error(self, message):
        """Exibe uma mensagem de erro usando QMessageBox."""
        QMessageBox.critical(self, "Erro", message,
                             QMessageBox.StandardButton.Ok)  # type: ignore

    def _disable_buttons(self, state):
        """Desabilita ou habilita os botões."""
        self.select_button.setEnabled(not state)
        self.select_output_button.setEnabled(not state)
        self.start_button.setEnabled(not state)

    def _validate_output_path(self):
        """Verifica se o caminho de saída para o PDF é válido."""
        if not self.output_pdf:
            raise Exception("Caminho de saída inválido")

        if os.path.exists(self.output_pdf):
            try:
                # Tenta abrir o arquivo para escrita
                open(self.output_pdf, "a").close()
            except IOError:
                raise Exception(
                    "O arquivo de saída já existe"
                    "e não pode ser acessado para escrita."
                )
        else:
            try:
                with open(self.output_pdf, "w"):  # Tenta criar o arquivo
                    pass
            except IOError:
                raise Exception("O arquivo de saída não pôde ser criado.")

    def _open_output_folder(self):
        """Abre a pasta onde o arquivo foi salvo."""
        if self.output_pdf:
            folder_path = os.path.dirname(self.output_pdf)
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder_path])
            elif sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", folder_path])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OCRPDFApp()
    window.show()
    sys.exit(app.exec())
