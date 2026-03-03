"""Análise de eventos."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Event:
    """Representa um evento para análise."""

    nome: str
    data: date
    local: str
    publico_estimado: int
    descricao: str = ""
    tema: Optional[str] = None
    formato: Optional[str] = None  # presencial, híbrido, online


def analyze_event(event: Event) -> dict:
    """
    Analisa um evento e retorna métricas resumidas.
    """
    return {
        "nome": event.nome,
        "data": event.data.isoformat(),
        "local": event.local,
        "publico_estimado": event.publico_estimado,
        "tema": event.tema,
        "formato": event.formato,
        "tem_publico_significativo": event.publico_estimado >= 100,
    }
