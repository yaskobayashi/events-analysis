#!/usr/bin/env python3
"""Exemplo de uso do events-analysis."""

from datetime import date

from src.events_analysis import (
    Event,
    Project,
    analyze_event,
    analyze_project,
    score_sponsorship_potential,
)


def main():
    # Exemplo: evento
    evento = Event(
        nome="Tech Meetup SP",
        data=date(2025, 4, 15),
        local="São Paulo",
        publico_estimado=200,
        tema="tecnologia",
        formato="presencial",
    )
    print("Análise do evento:", analyze_event(evento))
    print("Potencial de patrocínio:", score_sponsorship_potential(evento), "/ 100\n")

    # Exemplo: projeto
    projeto = Project(
        nome="Academia de Devs",
        descricao="Programa de formação em programação.",
        objetivo="Capacitar 50 pessoas em 6 meses",
        publico_alvo="Iniciantes em TI",
        duracao_meses=6,
        parceiros=["Empresa X", "Universidade Y"],
    )
    print("Análise do projeto:", analyze_project(projeto))
    print("Potencial de patrocínio:", score_sponsorship_potential(projeto), "/ 100")


if __name__ == "__main__":
    main()
