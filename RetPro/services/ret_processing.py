from __future__ import annotations

import glob
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from constants.regex import RET_EXCLUDE_SUFFIX, RET_NAME_LINE
from services.db import load_data_from_json
from utils.formatting import format_currency


def parse_ret_txt_files(folder: str) -> Tuple[List[str], int, Dict[str, int]]:
    """Lê .txt na pasta, filtra linhas, extrai nomes e retorna:
    - nomes_encontrados (lista)
    - total_nomes_encontrados (int)
    - nomes_por_arquivo (dict filename -> count)
    """
    palavra_excluida = "0BD"
    regex_excluir = re.compile(RET_EXCLUDE_SUFFIX)
    regex_nome = re.compile(RET_NAME_LINE)

    nomes_encontrados_total: List[str] = []
    nomes_por_arquivo: Dict[str, int] = {}
    arquivos_txt: List[str] = []

    for arquivo in glob.glob(os.path.join(folder, "*.txt")):
        arquivos_txt.append(arquivo)

    for file_path in arquivos_txt:
        nome_arquivo = os.path.basename(file_path)
        nomes_encontrados_arquivo = 0
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                linhas = f.readlines()[2:-2]
                for i, line in enumerate(linhas, start=3):
                    if i % 2 != 0 and palavra_excluida not in line and not regex_excluir.search(line):
                        nomes = regex_nome.findall(line)
                        nomes_encontrados_total.extend(nomes)
                        nomes_encontrados_arquivo += len(nomes)
        except Exception as e:
            print(f"Erro ao processar o arquivo {nome_arquivo}: {e}")
            continue
        nomes_por_arquivo[nome_arquivo] = nomes_encontrados_arquivo

    total_nomes = sum(nomes_por_arquivo.values())
    return nomes_encontrados_total, total_nomes, nomes_por_arquivo


def buscar_no_banco(
    nomes_encontrados: List[str], banco_json_path: str, incluir_valores: bool
) -> Tuple[List[Dict[str, Any]], float, Dict[str, Dict[str, List[Tuple[str, Optional[str], Optional[str], str]]]]]:
    """Busca nomes no banco JSON e constrói resultados agregados por arquivo de origem.
    Retorna:
    - all_results (linhas para CSV)
    - total_valores_encontrados (float)
    - resultados_por_arquivo (para sa��da .txt organizada)
    """
    dados_banco = load_data_from_json(banco_json_path)
    total_valores_encontrados = 0.0
    resultados_por_arquivo: Dict[str, Dict[str, List[Tuple[str, Optional[str], Optional[str], str]]]] = {}
    all_results: List[Dict[str, Any]] = []

    # Index auxiliar: nome -> lista de (arquivo, dado)
    index: Dict[str, List[Tuple[str, Any]]] = {}
    for nome_arquivo_db, dados in dados_banco.items():
        for nome, raw in dados.items():
            index.setdefault(nome, []).append((nome_arquivo_db, raw))

    for nome_original in nomes_encontrados:
        pdf_origem: Optional[str] = None
        nome_encontrado: Optional[str] = None
        valor_encontrado: Optional[float] = None
        cpf_encontrado: Optional[str] = None

        # Busca direta
        if nome_original in index:
            for nome_arquivo_db, raw in index[nome_original]:
                pdf_origem = nome_arquivo_db
                nome_encontrado = nome_original
                if isinstance(raw, dict):
                    valor_encontrado = raw.get("valor")
                    cpf_encontrado = raw.get("cpf")
                else:
                    valor_encontrado = raw
                    cpf_encontrado = None
                break

            if nome_encontrado:
                chave_saida = pdf_origem.split(" - ")[0].replace("  ", " ") if pdf_origem else "Desconhecido"
                resultados_por_arquivo.setdefault(chave_saida, [])
                if incluir_valores:
                    formatted_valor = (
                        format_currency(valor_encontrado) if isinstance(valor_encontrado, (int, float)) else None
                    )
                    resultados_por_arquivo[chave_saida].append((nome_original, cpf_encontrado, formatted_valor, "Completo"))
                    if isinstance(valor_encontrado, (int, float)):
                        total_valores_encontrados += valor_encontrado
                else:
                    resultados_por_arquivo[chave_saida].append((nome_original, cpf_encontrado, None, "Completo"))
        else:
            # Busca parcial por prefixos acumulados
            partes = nome_original.split()
            encontrado = False
            for i in range(1, len(partes) + 1):
                nome_parcial = " ".join(partes[:i])
                correspondencias = [
                    (nome, nome_arquivo_db, dados_banco[nome_arquivo_db][nome])
                    for nome_arquivo_db in dados_banco
                    for nome in dados_banco[nome_arquivo_db]
                    if nome.startswith(nome_parcial)
                ]
                if len(correspondencias) == 1:
                    nome_encontrado = correspondencias[0][0]
                    pdf_origem = correspondencias[0][1]
                    raw = correspondencias[0][2]
                    if isinstance(raw, dict):
                        valor_encontrado = raw.get("valor")
                        cpf_encontrado = raw.get("cpf")
                    else:
                        valor_encontrado = raw
                        cpf_encontrado = None

                    chave_saida = pdf_origem.split(" - ")[0].replace("  ", " ") if pdf_origem else "Desconhecido"
                    resultados_por_arquivo.setdefault(chave_saida, [])

                    if incluir_valores and valor_encontrado is not None:
                        formatted_valor = (
                            format_currency(valor_encontrado) if isinstance(valor_encontrado, (int, float)) else None
                        )
                        resultados_por_arquivo[chave_saida].append(
                            (nome_original, cpf_encontrado, formatted_valor, f"Parcial - Encontrado como: {nome_encontrado}")
                        )
                        if isinstance(valor_encontrado, (int, float)):
                            total_valores_encontrados += valor_encontrado
                    else:
                        resultados_por_arquivo[chave_saida].append(
                            (nome_original, cpf_encontrado, None, f"Parcial - Encontrado como: {nome_encontrado}")
                        )
                    encontrado = True
                    break
            if not encontrado:
                resultados_por_arquivo.setdefault("Não Encontrado", [])
                tokens = [t.lower() for t in nome_original.split() if len(t) > 2]
                candidates: List[Tuple[str, str, Any]] = []
                for nome_db_file, dados in dados_banco.items():
                    for nome_db, raw in dados.items():
                        nome_db_low = nome_db.lower()
                        if tokens and all(tok in nome_db_low for tok in tokens):
                            candidates.append((nome_db, nome_db_file, raw))

                if len(candidates) == 1:
                    cand_nome, cand_file, raw = candidates[0]
                    cpf_cand = raw.get("cpf") if isinstance(raw, dict) else None
                    val_cand = raw.get("valor") if isinstance(raw, dict) else raw
                    status_text = f"Tentativa - Encontrado como: {cand_nome}"
                    formatted_val = format_currency(val_cand) if isinstance(val_cand, (int, float)) else None
                    resultados_por_arquivo["Não Encontrado"].append((nome_original, cpf_cand, formatted_val, status_text))
                    if isinstance(val_cand, (int, float)):
                        total_valores_encontrados += val_cand
                else:
                    resultados_por_arquivo["Não Encontrado"].append((nome_original, None, None, "Não encontrado"))

    # Flatten para CSV e remover duplicatas
    processed = set()
    for origem, registros in resultados_por_arquivo.items():
        for nome, cpf, valor, status in registros:
            tup = (origem, nome, cpf, valor, status)
            if tup in processed:
                continue
            all_results.append({
                "Origem": origem,
                "Nome": nome,
                "CPF": cpf,
                "Valor": valor,
                "Status": status,
            })
            processed.add(tup)

    return all_results, total_valores_encontrados, resultados_por_arquivo
