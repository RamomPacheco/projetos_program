from __future__ import annotations

import os
from typing import Callable, List, Optional

import pymupdf as fitz  # type: ignore

from constants.filenames import FN_NOMES_NAO_DEST


def anotar_pdf(
    pdf_path: str,
    txt_path: str,
    output_pdf_path: str,
    progress_cb: Optional[Callable[[int], None]] = None,
) -> Optional[str]:
    """Destaca nomes no PDF conforme lista do txt. Retorna caminho de 'nomes_nao_destacados.txt' se houver, senão None."""
    nomes: List[str] = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                nomes.append(line.split(":")[0].strip())

    nomes_nao_destacados = set(nomes)
    try:
        with fitz.open(pdf_path) as pdf:
            total_pages = max(1, len(pdf))
            for page_num, page in enumerate(pdf, start=1):
                for nome in nomes:
                    areas = page.search_for(nome)
                    if areas:
                        if nome in nomes_nao_destacados:
                            nomes_nao_destacados.discard(nome)
                        for area in areas:
                            page.add_highlight_annot(area)
                for nome in list(nomes_nao_destacados):
                    areas = page.search_for(nome)
                    if areas:
                        nomes_nao_destacados.discard(nome)
                        for area in areas:
                            page.add_underline_annot(area)
                if progress_cb:
                    progress_cb(int(100 * page_num / total_pages))
            pdf.save(output_pdf_path)
    except Exception as e:
        print(f"Erro ao processar PDF para destaque: {e}")
        return None

    if nomes_nao_destacados:
        nomes_nao_encontrados_path = os.path.join(os.path.dirname(output_pdf_path), FN_NOMES_NAO_DEST)
        try:
            nomes_nao_destacados_lista = sorted(list(nomes_nao_destacados))
            with open(nomes_nao_encontrados_path, "w", encoding="utf-8") as f:
                total_nomes = len(nomes_nao_destacados_lista)
                f.write(f"Total de nomes não encontrados: {total_nomes}\n")
                for nome in nomes_nao_destacados_lista:
                    f.write(f"{nome}\n")
            return nomes_nao_encontrados_path
        except Exception as e:
            print(f"Erro ao salvar nomes não encontrados: {e}")
            return None
    else:
        nomes_nao_encontrados_path = os.path.join(os.path.dirname(output_pdf_path), FN_NOMES_NAO_DEST)
        if os.path.exists(nomes_nao_encontrados_path):
            try:
                os.remove(nomes_nao_encontrados_path)
            except Exception:
                pass
        return None
