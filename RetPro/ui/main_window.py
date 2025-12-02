from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QButtonGroup,
    QRadioButton,
)

from utils.fs import open_folder
from workers.process_worker import ProcessadorThread


class JanelaPrincipal(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RetFindErro")
        self.setGeometry(100, 100, 500, 250)
        self._thread: Optional[ProcessadorThread] = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Pasta PDF
        pasta_pdf_layout = QHBoxLayout()
        self.pasta_pdf_label = QLabel("Pasta com arquivos .pdf para (BANCO DE DADOS):")
        self.pasta_pdf_input = QLineEdit(self)
        self.pasta_pdf_button = QPushButton("Selecionar Pasta", self)
        self.pasta_pdf_button.clicked.connect(self.selecionar_pasta_pdf)
        pasta_pdf_layout.addWidget(self.pasta_pdf_label)
        pasta_pdf_layout.addWidget(self.pasta_pdf_input)
        pasta_pdf_layout.addWidget(self.pasta_pdf_button)
        layout.addLayout(pasta_pdf_layout)

        # Pasta .ret/.txt
        pasta_layout = QHBoxLayout()
        self.pasta_label = QLabel("Pasta com arquivos .ret:")
        self.pasta_input = QLineEdit(self)
        self.pasta_button = QPushButton("Selecionar Pasta", self)
        self.pasta_button.clicked.connect(self.selecionar_pasta_origem)
        pasta_layout.addWidget(self.pasta_label)
        pasta_layout.addWidget(self.pasta_input)
        pasta_layout.addWidget(self.pasta_button)
        layout.addLayout(pasta_layout)

        # Formato de saída
        self.formato_layout = QHBoxLayout()
        self.formato_label = QLabel("Formato de Saída:")
        self.radio_txt = QRadioButton("TXT")
        self.radio_csv = QRadioButton("CSV")
        self.radio_csv.setChecked(True)
        self.formato_layout.addWidget(self.formato_label)
        self.formato_layout.addWidget(self.radio_txt)
        self.formato_layout.addWidget(self.radio_csv)
        self.button_group_formato = QButtonGroup(self)
        self.button_group_formato.addButton(self.radio_txt)
        self.button_group_formato.addButton(self.radio_csv)
        layout.addLayout(self.formato_layout)

        # Arquivo de saída
        arquivo_layout = QHBoxLayout()
        self.arquivo_label = QLabel("salvar como:")
        self.arquivo_input = QLineEdit(self)
        self.arquivo_button = QPushButton("Selecionar Local", self)
        self.arquivo_button.clicked.connect(self.selecionar_arquivo_saida)
        arquivo_layout.addWidget(self.arquivo_label)
        arquivo_layout.addWidget(self.arquivo_input)
        arquivo_layout.addWidget(self.arquivo_button)
        layout.addLayout(arquivo_layout)

        # Opção valores
        self.checkbox_valores = QCheckBox("Incluir valores na saída", self)
        self.checkbox_valores.setChecked(True)
        layout.addWidget(self.checkbox_valores)

        # Progresso
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Iniciar
        self.iniciar_button = QPushButton("Iniciar Extração", self)
        self.iniciar_button.clicked.connect(self.iniciar_processamento)
        layout.addWidget(self.iniciar_button)

        # Rodapé
        rodape_layout = QHBoxLayout()
        self.rodape_label = QLabel("Criado por Max Ramom.F", self)
        self.rodape_label.setAlignment(Qt.AlignCenter)
        rodape_layout.addWidget(self.rodape_label)
        layout.addLayout(rodape_layout)

    # ------------ Seletor de entradas ------------
    def selecionar_pasta_pdf(self) -> None:
        pasta_pdf = QFileDialog.getExistingDirectory(self, "Selecione a pasta com os arquivos .pdf")
        if pasta_pdf:
            self.pasta_pdf_input.setText(pasta_pdf)

    def selecionar_pasta_origem(self) -> None:
        pasta_origem = QFileDialog.getExistingDirectory(self, "Selecione a pasta com os arquivos .txt/.ret")
        if pasta_origem:
            self.pasta_input.setText(pasta_origem)

    def selecionar_arquivo_saida(self) -> None:
        if self.radio_csv.isChecked():
            arquivo_saida, _ = QFileDialog.getSaveFileName(self, "Escolha o local para salvar o arquivo", "", "CSV files (*.csv)")
        else:
            arquivo_saida, _ = QFileDialog.getSaveFileName(self, "Escolha o local para salvar o arquivo", "", "Text files (*.txt)")
        if arquivo_saida:
            self.arquivo_input.setText(arquivo_saida)

    # ------------ Fluxo ------------
    def iniciar_processamento(self) -> None:
        pasta_txt = self.pasta_input.text()
        arquivo_saida = self.arquivo_input.text()
        pasta_pdf = self.pasta_pdf_input.text()
        incluir_valores = self.checkbox_valores.isChecked()
        saida_csv = self.radio_csv.isChecked()

        if not pasta_txt or not arquivo_saida or not pasta_pdf:
            QMessageBox.critical(self, "Erro", "Por favor, selecione a pasta de origem, arquivo de saída e pasta PDF")
            return

        self._thread = ProcessadorThread(pasta_txt, arquivo_saida, pasta_pdf, incluir_valores, saida_csv)
        self._thread.progresso.connect(self.atualizar_barra_progresso)
        self._thread.concluido.connect(self.finalizar_processamento)
        self._thread.start()
        self.iniciar_button.setEnabled(False)

    def atualizar_barra_progresso(self, progresso: int) -> None:
        self.progress_bar.setValue(progresso)

    def finalizar_processamento(self) -> None:
        resposta = QMessageBox.question(self, "Processamento Concluído", "Processamento concluído! Deseja fazer outra execução?", QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.No:
            output_file_path = self.arquivo_input.text()
            try:
                open_folder(os.path.dirname(output_file_path))
            except Exception:
                pass
            QApplication.quit()
        else:
            self.resetar_campos()

    def resetar_campos(self) -> None:
        self.pasta_pdf_input.clear()
        self.pasta_input.clear()
        self.arquivo_input.clear()
        self.progress_bar.setValue(0)
        self.checkbox_valores.setChecked(True)
        self.iniciar_button.setEnabled(True)
