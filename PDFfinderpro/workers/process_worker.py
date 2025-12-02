from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMessageBox

from constants.filenames import (
    FN_DADOS_PAGOS,
    FN_DADOS_PROJETO,
    FN_FUNC_ENCONTRADOS,
    FN_FUNC_NOMES_DIF,
    FN_NOMES_NAO_ENC,
)
from constants.regex import REGEX_PAGAMENTOS, REGEX_PROJETOS
from services.annotate import anotar_pdf
from services.artifacts import salvar_arquivos_na_pasta
from services.compare import (
    adicionar_nomes_encontrados,
    comparar_busca_parcial,
    comparar_exata_e_parcial,
)
from services.pdf_extraction import extrair_pagos, extrair_projeto
from services.totals import atualizar_totais_txt


class Worker(QThread):
    progress_update = Signal(int)
    finished = Signal(str)

    def __init__(self, pdf_pagos_path: str, pdf_projetos_dir: str, base_output_dir: str):
        super().__init__()
        self.pdf_pagos_path = pdf_pagos_path
        self.pdf_projetos_dir = pdf_projetos_dir
        self.base_output_dir = base_output_dir

    def run(self) -> None:
        pasta_base = self.processar_pdfs(self.pdf_pagos_path, self.pdf_projetos_dir, self.base_output_dir)
        self.finished.emit(pasta_base or "")

    def processar_pdfs(self, pdf_pagos_path: str, pdf_projetos_dir: str, base_output_dir: str) -> Optional[str]:
        pdf_projetos_files = [
            str(Path(pdf_projetos_dir, f))
            for f in os.listdir(pdf_projetos_dir)
            if f.lower().endswith('.pdf')
        ]
        if not pdf_projetos_files:
            QMessageBox.critical(None, "Erro", "Não foram encontrados arquivos PDF na pasta selecionada.")
            return None

        total_stages_por_pdf = 6
        total_stages = len(pdf_projetos_files) * total_stages_por_pdf
        current_stage = 0

        for pdf_todos in pdf_projetos_files:
            pasta_saida = self._criar_pasta_saida_por_pdf(pdf_todos, base_output_dir)
            if not pasta_saida:
                QMessageBox.critical(None, "Erro", f"Não foi possível criar a pasta de saída para '{Path(pdf_todos).name}'.")
                continue

            output_pagos = str(Path(pasta_saida, FN_DADOS_PAGOS))
            output_projeto = str(Path(pasta_saida, FN_DADOS_PROJETO))
            arquivo_saida_path = str(Path(pasta_saida, FN_FUNC_ENCONTRADOS))
            arquivo1_path = output_pagos
            arquivo2_path = output_projeto
            arquivo_saida_exato = str(Path(pasta_saida, FN_FUNC_ENCONTRADOS))
            arquivo_saida_diferente = str(Path(pasta_saida, FN_FUNC_NOMES_DIF))
            output_pdf = str(Path(pasta_saida, f"{Path(pdf_todos).stem}_destacado.pdf"))
            arquivo_nomes_nao_encontrados = str(Path(pasta_saida, FN_NOMES_NAO_ENC))

            # 1) Extrair dados de pagamentos
            current_stage += 1
            self._emit_progresso_etapa(current_stage, total_stages, 0)
            def prog_etapa1(pct: int) -> None:
                self._emit_progresso_etapa(current_stage, total_stages, pct)
            dados_pagos = extrair_pagos(pdf_pagos_path, REGEX_PAGAMENTOS, prog_etapa1)
            if dados_pagos:
                with open(output_pagos, "w", encoding="utf-8") as f:
                    for nome, valor in sorted(dados_pagos.items()):
                        f.write(f"{nome}: {valor}\n")

            # 2) Extrair dados do projeto
            current_stage += 1
            self._emit_progresso_etapa(current_stage, total_stages, 0)
            def prog_etapa2(pct: int) -> None:
                self._emit_progresso_etapa(current_stage, total_stages, pct)
            dados_proj = extrair_projeto(pdf_todos, REGEX_PROJETOS, prog_etapa2)
            if dados_proj:
                with open(output_projeto, "w", encoding="utf-8") as f:
                    for nome, valor in sorted(dados_proj.items()):
                        f.write(f"{nome}: {valor}\n")

            # 3) Comparação parcial simples
            current_stage += 1
            self._emit_progresso_etapa(current_stage, total_stages, 0)
            def prog_etapa3(pct: int) -> None:
                self._emit_progresso_etapa(current_stage, total_stages, pct)
            comparar_busca_parcial(output_projeto, output_pagos, arquivo_saida_path, prog_etapa3)

            # 4) Comparação exata e parcial
            current_stage += 1
            self._emit_progresso_etapa(current_stage, total_stages, 0)
            def prog_etapa4(pct: int) -> None:
                self._emit_progresso_etapa(current_stage, total_stages, pct)
            comparar_exata_e_parcial(arquivo1_path, arquivo2_path, arquivo_saida_exato, arquivo_saida_diferente, arquivo_nomes_nao_encontrados, prog_etapa4)

            # 5) Adicionar nomes encontrados do relatório "diferentes"
            current_stage += 1
            self._emit_progresso_etapa(current_stage, total_stages, 0)
            def prog_etapa5(pct: int) -> None:
                self._emit_progresso_etapa(current_stage, total_stages, pct)
            adicionar_nomes_encontrados(arquivo_saida_diferente, arquivo_saida_exato, prog_etapa5)

            # 6) Anotar PDF
            current_stage += 1
            self._emit_progresso_etapa(current_stage, total_stages, 0)
            def prog_etapa6(pct: int) -> None:
                self._emit_progresso_etapa(current_stage, total_stages, pct)
            nomes_nao_dest_path = anotar_pdf(pdf_pagos_path, arquivo_saida_exato, output_pdf, prog_etapa6)

            # Atualiza totais
            for fp in [output_pagos, output_projeto, arquivo_saida_path, arquivo_saida_exato, arquivo_saida_diferente]:
                atualizar_totais_txt(fp)
            if nomes_nao_dest_path:
                atualizar_totais_txt(nomes_nao_dest_path)

            # Copiar artefatos
            salvar_arquivos_na_pasta(
                pasta_saida=str(pasta_saida),
                output_pagos=output_pagos,
                output_projeto=output_projeto,
                arquivo_saida_path=arquivo_saida_path,
                arquivo_saida_exato=arquivo_saida_exato,
                arquivo_saida_diferente=arquivo_saida_diferente,
                output_pdf=output_pdf,
                nomes_nao_encontrados_path=nomes_nao_dest_path,
                arquivo_nomes_nao_encontrados=arquivo_nomes_nao_encontrados,
            )

            print(f"Processamento concluído para: {Path(pdf_todos).name}")

        return base_output_dir

    def _criar_pasta_saida_por_pdf(self, pdf_path: str, base_output_dir: str) -> Optional[str]:
        try:
            nome_arquivo = Path(pdf_path).name
            nome_pasta = nome_arquivo.split(' - ')[0].strip()
            pasta_saida = Path(base_output_dir, nome_pasta)
            os.makedirs(pasta_saida, exist_ok=True)
            return str(pasta_saida)
        except Exception as e:
            print(f"Erro ao criar pasta de saída: {e}")
            return None

    def _emit_progresso_etapa(self, current_stage: int, total_stages: int, pct: int) -> None:
        frac_etapa = 1 / total_stages
        base = (current_stage - 1) / total_stages
        self.progress_update.emit(int(100 * (base + frac_etapa * (pct / 100))))

    def atualizar_totais_em_todos_txts(self, base_output_dir: str) -> None:
        # Compatibilidade com UI atual; podemos reimportar aqui para evitar ciclo
        from services.totals import atualizar_totais_em_todos_txts as _att
        _att(base_output_dir)
