from __future__ import annotations

import os
import subprocess
import sys


def abrir_pasta_os(caminho_pasta: str) -> None:
    """Abre uma pasta no sistema operacional de forma segura."""
    if sys.platform == 'win32':
        os.startfile(caminho_pasta)  # type: ignore[attr-defined]
    elif sys.platform == 'darwin':
        subprocess.run(['open', caminho_pasta], check=True)
    elif sys.platform.startswith('linux'):
        subprocess.run(['xdg-open', caminho_pasta], check=True)
    else:
        raise RuntimeError(f"Sistema Operacional não suportado: {sys.platform}")
