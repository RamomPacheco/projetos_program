from __future__ import annotations

import re
from typing import Dict

from PyPDF2 import PdfReader

from constants.regex import PDF_NAME_CPF_VALUE


def extract_data(pdf_path: str) -> Dict[str, Dict[str, float]]:
    """Extrai nomes, CPF e valor líquido de um PDF e retorna dict nome -> {cpf, valor}."""
    try:
        reader = PdfReader(pdf_path)
        all_text = ""
        for page in reader.pages:
            all_text += page.extract_text() or ""

        matches = re.findall(PDF_NAME_CPF_VALUE, all_text)
        extracted_data: Dict[str, Dict[str, float]] = {}
        for name, cpf, value in matches:
            name = name.strip()
            value_norm = value.replace(".", "").replace(",", ".")
            try:
                value_f = float(value_norm)
                extracted_data[name] = {"cpf": cpf, "valor": value_f}
            except ValueError:
                # ignora valores inválidos
                pass
        return extracted_data
    except Exception as e:
        print(f"Erro ao processar o arquivo PDF: {e}")
        return {}
