from __future__ import annotations

import os
from typing import Iterable

from PyPDF2 import PdfMerger


def merge_pdfs(files: Iterable[str], output_file: str) -> None:
    files = list(files)
    if not files:
        raise ValueError("Nenhum arquivo para mesclar")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    merger = PdfMerger()
    try:
        for f in files:
            merger.append(f)
        merger.write(output_file)
    finally:
        merger.close()
