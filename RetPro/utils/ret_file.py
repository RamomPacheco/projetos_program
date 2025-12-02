from __future__ import annotations

import os
from typing import Optional


def alterar_extensao_para_txt(arquivo_ret: str) -> Optional[str]:
    """Renomeia .ret para .txt e retorna o novo caminho; caso contrário, None."""
    if arquivo_ret.endswith(".ret"):
        arquivo_txt = arquivo_ret[:-4] + ".txt"
        os.rename(arquivo_ret, arquivo_txt)
        return arquivo_txt
    return None
