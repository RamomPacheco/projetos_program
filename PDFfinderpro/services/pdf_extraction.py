from __future__ import annotations

import re
from typing import Callable, Dict, Optional

import pymupdf as fitz  # type: ignore
from PyPDF2 import PdfReader

from constants.regex import REGEX_PAGAMENTOS, REGEX_PROJETOS
from utils.formatting import formatar_moeda


def extrair_pagos(
    pdf_path: str,
    regex: str = REGEX_PAGAMENTOS,
    progress_cb: Optional[Callable[[int], None]] = None,
) -> Dict[str, str]:
    dados: Dict[str, str] = {}
    try:
        with fitz.open(pdf_path) as pdf:
            total_pages = max(1, len(pdf))
            for page_num, page in enumerate(pdf, start=1):
                texto = page.get_text("text")
                for nome, valor in re.findall(regex, texto):
                    nome = nome.strip()
                    try:
                        valor_float = float(valor.replace('.', '').replace(',', '.'))
                        dados[nome] = formatar_moeda(valor_float)
                    except ValueError:
                        pass
                if progress_cb:
                    progress_cb(int(100 * page_num / total_pages))
    except Exception as e:
        print(f"Erro ao abrir/processar PDF (Pagos): {e}")
        return {}
    return dados


def extrair_projeto(
    pdf_path: str,
    regex: str = REGEX_PROJETOS,
    progress_cb: Optional[Callable[[int], None]] = None,
) -> Dict[str, str]:
    extracted: Dict[str, str] = {}
    try:
        reader = PdfReader(pdf_path)
        total_pages = max(1, len(reader.pages))
        all_text = ""
        for page_num, page in enumerate(reader.pages, start=1):
            all_text += (page.extract_text() or "")
            if progress_cb:
                progress_cb(int(100 * page_num / total_pages))
        for name, value in re.findall(regex, all_text):
            name = name.strip()
            try:
                valor_float = float(value.replace('.', '').replace(',', '.'))
                extracted[name] = formatar_moeda(valor_float)
            except ValueError:
                pass
    except Exception as e:
        print(f"Erro ao processar o arquivo PDF (Projeto): {e}")
        return {}
    return extracted
