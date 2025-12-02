"""
Utilitários de formatação e configuração de locale.
"""
from __future__ import annotations

import locale

# Tenta configurar o locale pt_BR; se falhar, a função formatar_moeda usará fallback
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    pass


def formatar_moeda(valor: float) -> str:
    """Formata um float como moeda BR com separadores de milhar e vírgula decimal.

    Usa locale se disponível; caso contrário, aplica fallback manual.
    """
    try:
        return locale.format_string('%.2f', valor, grouping=True)
    except Exception:
        s = f"{valor:,.2f}"
        return s.replace(',', 'X').replace('.', ',').replace('X', '.')
