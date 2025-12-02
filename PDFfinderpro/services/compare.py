from __future__ import annotations

import re
from typing import Callable, Dict, List, Optional, Tuple

from tqdm import tqdm

from utils.names import gerar_prefixos_nome


def comparar_busca_parcial(
    arquivo1_path: str,
    arquivo2_path: str,
    arquivo_saida_path: str,
    progress_cb: Optional[Callable[[int], None]] = None,
) -> None:
    try:
        with open(arquivo1_path, 'r', encoding='utf-8') as a1, \
             open(arquivo2_path, 'r', encoding='utf-8') as a2, \
             open(arquivo_saida_path, 'w', encoding='utf-8') as out:

            dados_arquivo1: Dict[str, str] = {}
            for linha in a1:
                m = re.match(r"(.+?):\s*([\d,.]+)", linha)
                if m:
                    dados_arquivo1[m.group(1).strip()] = m.group(2).strip()

            linhas = a2.readlines()
            total = max(1, len(linhas))
            for idx, linha in enumerate(linhas, start=1):
                m = re.match(r"(.+?):\s*([\d,.]+)", linha)
                if m:
                    nome2_completo = m.group(1).strip()
                    valor2 = m.group(2).strip()
                    partes_nome2 = nome2_completo.split()
                    encontrado = False
                    for i in range(len(partes_nome2), 0, -1):
                        nome2_parcial = " ".join(partes_nome2[:i])
                        for nome1, valor1 in dados_arquivo1.items():
                            if nome2_parcial in nome1 and valor1 == valor2:
                                out.write(linha)
                                encontrado = True
                                break
                        if encontrado:
                            break
                if progress_cb:
                    progress_cb(int(100 * idx / total))
    except FileNotFoundError:
        print("Erro: Um ou ambos os arquivos de entrada não foram encontrados.")
    except Exception as e:
        print(f"Um erro ocorreu: {e}")


def comparar_exata_e_parcial(
    arquivo1_path: str,
    arquivo2_path: str,
    arquivo_saida_exato: str,
    arquivo_saida_diferente: str,
    arquivo_nomes_nao_encontrados: str,
    progress_cb: Optional[Callable[[int], None]] = None,
) -> None:
    try:
        dados_arquivo1: Dict[str, str] = {}
        with open(arquivo1_path, 'r', encoding='utf-8') as arquivo1:
            for linha in arquivo1:
                m = re.match(r"(.+?):\s*([\d,.]+)", linha)
                if m:
                    dados_arquivo1[m.group(1).strip()] = m.group(2).strip()

        nomes_nao_encontrados: List[Tuple[str, str]] = []

        with open(arquivo2_path, 'r', encoding='utf-8') as arquivo2, \
             open(arquivo_saida_exato, 'w', encoding='utf-8') as saida_exato:
            linhas = arquivo2.readlines()
            total = max(1, len(linhas))
            for idx, linha in enumerate(linhas, start=1):
                m = re.match(r"(.+?):\s*([\d,.]+)", linha)
                if m:
                    nome2_completo = m.group(1).strip()
                    valor2 = m.group(2).strip()
                    if nome2_completo in dados_arquivo1 and dados_arquivo1[nome2_completo] == valor2:
                        saida_exato.write(linha)
                    else:
                        nomes_nao_encontrados.append((nome2_completo, valor2))
                if progress_cb:
                    progress_cb(int(100 * idx / total))

        with open(arquivo_nomes_nao_encontrados, 'w', encoding='utf-8') as f_nao, \
             open(arquivo_saida_diferente, 'w', encoding='utf-8') as f_dif:
            for nome_original, valor_original in tqdm(nomes_nao_encontrados, desc="Comparando arquivos (Parcial)"):
                encontrado = False
                for prefixo in gerar_prefixos_nome(nome_original):
                    correspondencias = [
                        nome for nome, valor in dados_arquivo1.items()
                        if nome.startswith(prefixo) and valor == valor_original
                    ]
                    if len(correspondencias) == 1:
                        nome_encontrado = correspondencias[0]
                        f_dif.write(
                            f"Original: {nome_original}: {valor_original}\nEncontrado como: {nome_encontrado}: {valor_original}\n"
                        )
                        encontrado = True
                        break
                if not encontrado:
                    f_dif.write(
                        f"Original: {nome_original}: {valor_original} -> Nenhuma correspondência única encontrada\n"
                    )
                    f_nao.write(f"{nome_original}: {valor_original}\n")
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e.filename}")
    except Exception as e:
        print(f"Um erro ocorreu: {e}")


def adicionar_nomes_encontrados(
    arquivo_entrada_path: str,
    arquivo_saida_path: str,
    progress_cb: Optional[Callable[[int], None]] = None,
) -> None:
    try:
        with open(arquivo_entrada_path, 'r', encoding='utf-8') as ent:
            linhas = ent.readlines()
        total = max(1, len(linhas))
        with open(arquivo_saida_path, 'a', encoding='utf-8') as sai:
            for idx, linha in enumerate(linhas, start=1):
                if "Encontrado como" in linha:
                    m = re.match(r"Encontrado como:\s*(.*?):\s*([\d,.]+)", linha.strip())
                    if m:
                        nome = m.group(1).strip()
                        valor = m.group(2).strip()
                        sai.write(f"{nome}: {valor}\n")
                if progress_cb:
                    progress_cb(int(100 * idx / total))
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e.filename}")
    except Exception as e:
        print(f"Um erro ocorreu: {e}")
