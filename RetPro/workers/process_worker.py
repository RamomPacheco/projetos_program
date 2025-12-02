from __future__ import annotations

import glob
import os
from typing import Optional

from PySide6.QtCore import QThread, Signal

from services.pdf_extraction import extract_data
from services.db import save_data_to_json, load_data_from_json
from services.ret_processing import parse_ret_txt_files, buscar_no_banco
from utils.ret_file import alterar_extensao_para_txt
from utils.formatting import format_currency


class ProcessadorThread(QThread):
    concluido = Signal()
    progresso = Signal(int)

    def __init__(self, pasta: str, arquivo_saida: str, pasta_pdf: str, incluir_valores: bool, saida_csv: bool) -> None:
        super().__init__()
        self.pasta = pasta
        self.arquivo_saida = arquivo_saida
        self.pasta_pdf = pasta_pdf
        self.incluir_valores = incluir_valores
        self.saida_csv = saida_csv
        # Local do banco JSON ao lado do executável/script
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.banco_dados_json = os.path.join(os.path.dirname(self.script_dir), "banco_de_dados.json")

    def run(self) -> None:
        # Converte .ret para .txt (in place)
        for arquivo in glob.glob(os.path.join(self.pasta, "*.ret")):
            alterar_extensao_para_txt(arquivo)

        # Gera banco JSON a partir dos PDFs
        pdf_files = [f for f in os.listdir(self.pasta_pdf) if f.lower().endswith(".pdf")]
        total_files = max(1, len(pdf_files))
        banco: dict[str, dict] = {}
        for i, filename in enumerate(pdf_files):
            pdf_path = os.path.join(self.pasta_pdf, filename)
            dados = extract_data(pdf_path)
            if dados:
                banco[filename] = dados
            self.progresso.emit(int((i + 1) / total_files * 100))
        save_data_to_json(banco, self.banco_dados_json)

        # Carrega e processa .txt
        nomes, total_nomes, nomes_por_arquivo = parse_ret_txt_files(self.pasta)
        all_results, total_valores, resultados_por_arquivo = buscar_no_banco(nomes, self.banco_dados_json, self.incluir_valores)

        # Gera saída
        if self.saida_csv:
            self._write_csv(all_results, total_valores, total_nomes)
        else:
            self._write_txt(resultados_por_arquivo, total_valores, total_nomes)

        self.concluido.emit()

    # -------------- Saídas --------------
    def _write_csv(self, all_results: list[dict], total_valores: float, total_nomes: int) -> None:
        import csv
        with open(self.arquivo_saida, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Origem", "Nome", "CPF", "Valor", "Status"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";", quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(all_results)
        if self.incluir_valores:
            total_texto = f"Total de nomes encontrados: {total_nomes}\nValor total : {format_currency(total_valores)}"
        else:
            total_texto = f"Total de nomes encontrados: {total_nomes}\nOBS: Opção sem valor total"
        with open(self.arquivo_saida, "a", encoding="utf-8") as f:
            f.write(f"\n{total_texto}")

    def _write_txt(self, resultados_por_arquivo: dict[str, list[tuple]], total_valores: float, total_nomes: int) -> None:
        with open(self.arquivo_saida, "w", encoding="latin-1") as saida:
            for origem, registros in resultados_por_arquivo.items():
                saida.write(f"{origem}:\n")
                for nome, cpf, valor, status in registros:
                    if self.incluir_valores:
                        saida.write(f"- {nome} - CPF: {cpf if cpf else 'N/A'} - {valor}\n    - {status}\n")
                    else:
                        saida.write(f"- {nome}\n    - {status}\n")
                saida.write("\n")
            saida.write(f"\nTotal de nomes encontrados: {total_nomes}\n")
            if self.incluir_valores:
                saida.write(f"Valor total : {format_currency(total_valores)}")
            else:
                saida.write("OBS: Opção sem valor total")
