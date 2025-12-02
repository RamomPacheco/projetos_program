from __future__ import annotations

import locale

# Tenta configurar locale pt_BR, usa fallback na função quando necessário
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except locale.Error:
    pass


def format_currency(value: float) -> str:
    """Formata número como moeda BR sem símbolo, com separador de milhar e vírgula decimal."""
    try:
        return locale.currency(value, grouping=True, symbol=False)
    except Exception:
        s = f"{value:,.2f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
