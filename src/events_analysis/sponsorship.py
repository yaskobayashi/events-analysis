"""Pontuação do potencial de patrocínio."""

from typing import Union

from .events import Event, analyze_event
from .projects import Project, analyze_project


def score_sponsorship_potential(item: Union[Event, Project]) -> float:
    """
    Calcula uma pontuação de 0 a 100 para o potencial de patrocínio
    de um evento ou projeto.
    """
    if isinstance(item, Event):
        analysis = analyze_event(item)
        # Fatores: público, formato, local
        score = 0.0
        if analysis["publico_estimado"] >= 500:
            score += 40
        elif analysis["publico_estimado"] >= 100:
            score += 25
        elif analysis["publico_estimado"] >= 50:
            score += 10
        if analysis.get("formato") in ("presencial", "híbrido"):
            score += 20
        elif analysis.get("formato") == "online":
            score += 10
        # Bônus por ter tema definido (mais segmentado = mais atrativo)
        if analysis.get("tema"):
            score += 15
        return min(100.0, score + 15)  # base 15

    if isinstance(item, Project):
        analysis = analyze_project(item)
        score = 30.0  # base para projetos
        if analysis.get("tem_parceiros"):
            score += min(30, analysis["quantidade_parceiros"] * 10)
        if analysis.get("duracao_meses") and analysis["duracao_meses"] >= 6:
            score += 20
        if analysis.get("publico_alvo"):
            score += 20
        return min(100.0, score)

    return 0.0
