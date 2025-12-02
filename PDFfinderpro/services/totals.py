from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Tuple

from utils.formatting import formatar_moeda


def calcular_totais_de_linhas(linhas: Iterable[str]) -> Tuple[int, float]:
    total_valor = 0.0
    total_nomes = 0
    for line in linhas:
        if not line.startswith("Total:"):
            m = re.match(r".+?:\s*([\d,.]+)", line)
            if m:
                try:
                    valor = float(m.group(1).replace('.', '').replace(',', '.'))
                    total_valor += valor
                    total_nomes += 1
                except ValueError:
                    total_nomes += 1
    return total_nomes, total_valor


def atualizar_totais_txt(arquivo_path: str) -> None:
    try:
        with open(arquivo_path, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            total_nomes, total_valor = calcular_totais_de_linhas(lines)
            new_total_line = f"Total: {total_nomes} nomes, Valor: {formatar_moeda(total_valor)}\n"
            if lines and lines[0].startswith("Total:"):
                lines[0] = new_total_line
            else:
                lines.insert(0, new_total_line)
            f.seek(0)
            f.writelines(lines)
            f.truncate()
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado '{arquivo_path}'.")
    except Exception as e:
        print(f"Erro ao atualizar totais em '{arquivo_path}': {e}")


def atualizar_totais_em_todos_txts(base_output_dir: str) -> None:
    base = Path(base_output_dir)
    for item in base.iterdir():
        if item.is_dir():
            for file in item.iterdir():
                if file.suffix == '.txt':
                    atualizar_totais_txt(str(file))
