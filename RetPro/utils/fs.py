from __future__ import annotations

import os
import subprocess
import sys


def open_folder(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", path], check=True)
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", path], check=True)
    else:
        raise RuntimeError(f"SO não suportado: {sys.platform}")
