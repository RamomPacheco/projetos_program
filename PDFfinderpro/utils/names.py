from __future__ import annotations

from typing import List


def gerar_prefixos_nome(nome_completo: str) -> List[str]:
    """Gera possíveis prefixos para comparação parcial.
    Ex.: "JOAO SILVA JUNIOR" -> ["JOAO", "JOAO S", "JOAO SILVA", "JOAO SILVA J", "JOAO SILVA JUNIOR"]
    """
    partes = nome_completo.split()
    if not partes:
        return []

    prefixos: List[str] = []
    acumulado: List[str] = []
    for i, parte in enumerate(partes):
        acumulado.append(parte)
        prefixo = " ".join(acumulado)
        prefixos.append(prefixo)
        # Heurística adicional: primeira palavra + inicial da segunda
        if i == 1:  # após adicionar a segunda palavra
            prefixos.append(f"{partes[0]} {partes[1][0]}")
    return prefixos
