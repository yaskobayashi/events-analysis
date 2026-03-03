"""
events-analysis — Analisa eventos e projetos, pontua potencial de patrocínio.
"""

__version__ = "0.1.0"

from .events import Event, analyze_event
from .projects import Project, analyze_project
from .sponsorship import score_sponsorship_potential

__all__ = [
    "Event",
    "Project",
    "analyze_event",
    "analyze_project",
    "score_sponsorship_potential",
]
