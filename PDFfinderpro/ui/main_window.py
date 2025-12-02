from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Importa Worker e utilitário de abrir pasta dos novos módulos
from workers.process_worker import Worker
from utils.fs import abrir_pasta_os
import subprocess


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Processador de PDFs")
        self.setGeometry(100, 100, 700, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # PDF de Pagamentos
        self.label_pdf_pagos = QLabel("PDF de Pagamentos:")
        self.entry_pdf_pagos = QLineEdit()
        self.btn_pdf_pagos = QPushButton("Selecionar")
        self.btn_pdf_pagos.clicked.connect(self.selecionar_arquivo_pagos)

        self.layout_pagos = QHBoxLayout()
        self.layout_pagos.addWidget(self.label_pdf_pagos)
        self.layout_pagos.addWidget(self.entry_pdf_pagos)
        self.layout_pagos.addWidget(self.btn_pdf_pagos)
        self.layout.addLayout(self.layout_pagos)

        # Pasta de PDFs de Projetos
        self.label_pdf_projetos = QLabel("Pasta de PDFs de Projetos:")
        self.entry_pdf_projetos = QLineEdit()
        self.btn_pdf_projetos = QPushButton("Selecionar")
        self.btn_pdf_projetos.clicked.connect(self.selecionar_pasta_projetos)

        self.layout_projetos = QHBoxLayout()
        self.layout_projetos.addWidget(self.label_pdf_projetos)
        self.layout_projetos.addWidget(self.entry_pdf_projetos)
        self.layout_projetos.addWidget(self.btn_pdf_projetos)
        self.layout.addLayout(self.layout_projetos)

        # Pasta de Saída
        self.label_pasta_saida = QLabel("Pasta de Saída:")
        self.entry_pasta_saida = QLineEdit()
        self.btn_pasta_saida = QPushButton("Selecionar")
        self.btn_pasta_saida.clicked.connect(self.selecionar_pasta_saida)

        self.layout_saida = QHBoxLayout()
        self.layout_saida.addWidget(self.label_pasta_saida)
        self.layout_saida.addWidget(self.entry_pasta_saida)
        self.layout_saida.addWidget(self.btn_pasta_saida)
        self.layout.addLayout(self.layout_saida)

        # Barra de Progresso
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        # Botão de Iniciar
        self.btn_iniciar = QPushButton("Iniciar Processamento")
        self.btn_iniciar.clicked.connect(self.iniciar_processamento)
        self.layout.addWidget(self.btn_iniciar)

        self.worker_thread: Optional[Worker] = None

    # ---------- Ações UI ----------
    def selecionar_arquivo_pagos(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Selecione o PDF de Pagamentos", "", "Arquivos PDF (*.pdf)")
        if filename:
            self.entry_pdf_pagos.setText(filename)

    def selecionar_pasta_projetos(self) -> None:
        foldername = QFileDialog.getExistingDirectory(self, "Selecione a pasta com os PDFs de Projetos")
        if foldername:
            self.entry_pdf_projetos.setText(foldername)

    def selecionar_pasta_saida(self) -> None:
        foldername = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        if foldername:
            self.entry_pasta_saida.setText(foldername)

    def iniciar_processamento(self) -> None:
        pdf_pagos_path = self.entry_pdf_pagos.text()
        pdf_projetos_dir = self.entry_pdf_projetos.text()
        base_output_dir = self.entry_pasta_saida.text()

        if not pdf_pagos_path or not pdf_projetos_dir or not base_output_dir:
            QMessageBox.critical(self, "Erro", "Por favor, selecione todos os arquivos e pastas.")
            return

        self.iniciar_thread(pdf_pagos_path, pdf_projetos_dir, base_output_dir)

    def iniciar_thread(self, pdf_pagos_path: str, pdf_projetos_dir: str, base_output_dir: str) -> None:
        self.progress_bar.setValue(0)
        self.worker_thread = Worker(pdf_pagos_path, pdf_projetos_dir, base_output_dir)
        self.worker_thread.progress_update.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.processamento_finalizado)
        self.worker_thread.start()

    def processamento_finalizado(self, base_output_dir: Optional[str]) -> None:
        if QMessageBox.question(self, "Concluído", "Todos os PDFs foram processados! Deseja continuar?") == QMessageBox.Yes:
            self.limpar_campos()
        else:
            if base_output_dir:
                # Chama método do worker (compat) e abre pasta via utilitário
                self.worker_thread.atualizar_totais_em_todos_txts(base_output_dir)  # type: ignore[union-attr]
                try:
                    abrir_pasta_os(base_output_dir)
                except (subprocess.CalledProcessError, FileNotFoundError, RuntimeError):
                    QMessageBox.critical(self, "Erro", "Pasta não encontrada ou SO não suportado.")
                QApplication.quit()  # Encerra o programa após abrir a pasta
        self.worker_thread = None

    def limpar_campos(self) -> None:
        self.entry_pdf_pagos.clear()
        self.entry_pdf_projetos.clear()
        self.entry_pasta_saida.clear()
        self.progress_bar.setValue(0)
