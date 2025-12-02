# Padrões regex usados no processamento
# PDF: nome (caps/acentos), CPF e valor no formato 1.234,56
PDF_NAME_CPF_VALUE = r" - ([A-ZÀ-Ú ]+)\s+(\d{3}\.\d{3}\.\d{3}-\d{2}).*?(\d{1,3}(?:\.\d{3})*,\d{2})"

# Linhas .ret/.txt: nomes em CAPS com acentos (evita capturar códigos finais)
RET_EXCLUDE_SUFFIX = r"\d+[A-Za-z]$"
RET_NAME_LINE = r"\b[A-ZÁ-Ú][A-ZÁ-Ú\s]+[A-ZÁ-Ú]\b"
