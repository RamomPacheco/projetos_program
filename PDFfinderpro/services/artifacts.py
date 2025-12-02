from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional


def salvar_arquivos_na_pasta(
    pasta_saida: str,
    output_pagos: str,
    output_projeto: str,
    arquivo_saida_path: str,
    arquivo_saida_exato: str,
    arquivo_saida_diferente: str,
    output_pdf: str,
    nomes_nao_encontrados_path: Optional[str],
    arquivo_nomes_nao_encontrados: str,
) -> Optional[str]:
    if not pasta_saida:
        return None
    try:
        novo_output_pagos = Path(pasta_saida, Path(output_pagos).name)
        novo_output_projeto = Path(pasta_saida, Path(output_projeto).name)
        novo_arquivo_saida_path = Path(pasta_saida, Path(arquivo_saida_path).name)
        novo_arquivo_saida_exato = Path(pasta_saida, Path(arquivo_saida_exato).name)
        novo_arquivo_saida_diferente = Path(pasta_saida, Path(arquivo_saida_diferente).name)
        novo_output_pdf = Path(pasta_saida, Path(output_pdf).name)
        novo_arquivo_nomes_nao_encontrados = Path(pasta_saida, Path(arquivo_nomes_nao_encontrados).name)

        shutil.copy2(output_pagos, novo_output_pagos)
        shutil.copy2(output_projeto, novo_output_projeto)
        shutil.copy2(arquivo_saida_path, novo_arquivo_saida_path)
        shutil.copy2(arquivo_saida_exato, novo_arquivo_saida_exato)
        shutil.copy2(arquivo_saida_diferente, novo_arquivo_saida_diferente)
        shutil.copy2(output_pdf, novo_output_pdf)
        if nomes_nao_encontrados_path and os.path.exists(nomes_nao_encontrados_path):
            novo_nomes_nao_encontrados_path = Path(pasta_saida, Path(nomes_nao_encontrados_path).name)
            shutil.copy2(nomes_nao_encontrados_path, novo_nomes_nao_encontrados_path)
        shutil.copy2(arquivo_nomes_nao_encontrados, novo_arquivo_nomes_nao_encontrados)
        return pasta_saida
    except Exception as e:
        print(f"Erro ao salvar os arquivos na pasta: {e}")
        return None
