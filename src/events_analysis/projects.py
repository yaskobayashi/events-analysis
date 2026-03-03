"""Análise de projetos."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Project:
    """Representa um projeto para análise."""

    nome: str
    descricao: str
    objetivo: str
    publico_alvo: str
    duracao_meses: Optional[int] = None
    parceiros: Optional[List[str]] = None


def analyze_project(project: Project) -> dict:
    """
    Analisa um projeto e retorna métricas resumidas.
    """
    return {
        "nome": project.nome,
        "objetivo": project.objetivo,
        "publico_alvo": project.publico_alvo,
        "duracao_meses": project.duracao_meses,
        "tem_parceiros": bool(project.parceiros),
        "quantidade_parceiros": len(project.parceiros or []),
    }
