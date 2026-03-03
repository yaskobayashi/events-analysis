"""
Análise por IA usando a KB (PDF Guide CloudWalk Social 2025) e os dados do formulário.
Retorna: pontos positivos, pontos negativos, riscos, probabilidade de patrocínio.
"""

import json
import os
from typing import Any

from knowledge_base.loader import get_kb_text


def _format_dados(dados: dict) -> str:
    """Formata os dados do formulário para o prompt."""
    lines = []
    for k, v in dados.items():
        if k in ("certificado_base64", "certificado_path"):
            continue
        if isinstance(v, list):
            v = ", ".join(str(x) for x in v) if v else ""
        if v is None or v == "":
            continue
        if isinstance(v, bool):
            v = "Sim" if v else "Não"
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)


def analisar_com_ia(dados: dict) -> dict[str, Any] | None:
    """
    Chama a API OpenAI com a KB (PDF) e os dados do projeto.
    Retorna dict com: pontos_positivos, pontos_negativos, riscos, probabilidade_patrocinio, resumo_ai.
    Retorna None se OPENAI_API_KEY não estiver configurada.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    kb_text = get_kb_text()
    if not kb_text:
        kb_text = "(Base de conhecimento não disponível.)"
    # Limitar tamanho da KB no prompt para caber no contexto (ex.: ~12k chars)
    if len(kb_text) > 14_000:
        kb_text = kb_text[:14_000] + "\n\n[... documento truncado ...]"

    dados_str = _format_dados(dados)

    system = """Você é um analista de responsabilidade social da CloudWalk. Sua tarefa é analisar projetos enviados por proponentes com base no guia de impacto e responsabilidade social da CW (base de conhecimento fornecida).

Analise o projeto de forma objetiva e estruturada. Responda em português brasileiro. Sua resposta deve ser um único objeto JSON válido, sem markdown, com exatamente as chaves:
- "pontos_positivos": lista de strings (até 5 itens) com os principais pontos positivos do projeto em relação ao alinhamento com a CW.
- "pontos_negativos": lista de strings (até 5 itens) com pontos fracos ou desalinhamentos.
- "riscos": lista de strings (até 5 itens) com riscos identificados para a parceria ou para o projeto.
- "probabilidade_patrocinio": um número entre 0 e 100 (inteiro) indicando a probabilidade de o projeto ser apoiado pela CW, considerando o guia.
- "resumo_ai": uma string com 2 a 4 frases resumindo a análise e a recomendação."""

    user = f"""Use a seguinte base de conhecimento (guia CloudWalk Social) para avaliar o projeto:

--- BASE DE CONHECIMENTO (PDF) ---
{kb_text}

--- DADOS DO PROJETO ENVIADO PELO PROPONENTE ---
{dados_str}

---
Gere o objeto JSON com a análise (apenas o JSON, sem texto antes ou depois)."""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
        )
        content = (resp.choices[0].message.content or "").strip()
        # Remover blocos de código se a API envolver em ```json
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        return json.loads(content)
    except json.JSONDecodeError as e:
        return {
            "pontos_positivos": [],
            "pontos_negativos": ["Erro ao interpretar análise da IA."],
            "riscos": [],
            "probabilidade_patrocinio": 0,
            "resumo_ai": f"Análise gerada mas formato inválido: {e}",
        }
    except Exception as e:
        return {
            "pontos_positivos": [],
            "pontos_negativos": [],
            "riscos": [str(e)],
            "probabilidade_patrocinio": 0,
            "resumo_ai": f"Erro na análise por IA: {e}",
        }


def analisar_pdf_projeto(
    texto_pdf_projeto: str,
    nome_proponente: str = "",
    email_proponente: str = "",
) -> dict[str, Any] | None:
    """
    Analisa um projeto a partir do texto extraído do PDF enviado pelo proponente.
    Usa a KB (Guide CloudWalk Social) como referência.
    Retorna: pontos_positivos, pontos_negativos, riscos, probabilidade_patrocinio,
             resumo_ai, dados_faltantes (lista do que falta para analisar melhor).
    Retorna None se OPENAI_API_KEY não estiver configurada.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    kb_text = get_kb_text()
    if not kb_text:
        kb_text = "(Base de conhecimento não disponível.)"
    if len(kb_text) > 14_000:
        kb_text = kb_text[:14_000] + "\n\n[... documento truncado ...]"

    # Limitar tamanho do PDF do projeto (ex.: 20k chars)
    if len(texto_pdf_projeto) > 20_000:
        texto_pdf_projeto = texto_pdf_projeto[:20_000] + "\n\n[... documento do projeto truncado ...]"

    contexto = []
    if nome_proponente:
        contexto.append(f"Nome do proponente: {nome_proponente}")
    if email_proponente:
        contexto.append(f"E-mail: {email_proponente}")
    contexto_str = "\n".join(contexto) if contexto else "(Não informado)"

    system = """Você é um analista de responsabilidade social da CloudWalk. Sua tarefa é analisar projetos enviados em PDF por proponentes, usando o guia de impacto e responsabilidade social da CW (base de conhecimento fornecida).

Analise o conteúdo do PDF do projeto de forma objetiva. Responda em português brasileiro. Sua resposta deve ser um único objeto JSON válido, sem markdown, com exatamente as chaves:
- "pontos_positivos": lista de strings (até 5 itens) com os principais pontos positivos do projeto em relação ao alinhamento com a CW.
- "pontos_negativos": lista de strings (até 5 itens) com pontos fracos ou desalinhamentos.
- "riscos": lista de strings (até 5 itens) com riscos identificados para a parceria ou para o projeto.
- "probabilidade_patrocinio": um número entre 0 e 100 (inteiro) indicando a probabilidade de o projeto ser apoiado pela CW.
- "resumo_ai": uma string com 2 a 4 frases resumindo a análise e a recomendação.
- "dados_faltantes": lista de strings com as informações ou dados que FALTAM no documento para que a análise possa ser mais completa e precisa (ex.: "CNPJ da organização", "Valor total solicitado", "Público beneficiário quantificado"). Se o documento estiver completo, retorne lista vazia. Seja objetivo e prático."""

    user = f"""Use a base de conhecimento (guia CloudWalk Social) abaixo para avaliar o projeto cujo conteúdo (extraído do PDF enviado) está na seção seguinte.

--- BASE DE CONHECIMENTO (GUIA CW SOCIAL) ---
{kb_text}

--- CONTATO DO PROPONENTE ---
{contexto_str}

--- CONTEÚDO DO PDF DO PROJETO (TEXTO EXTRAÍDO) ---
{texto_pdf_projeto or "(Nenhum texto extraído do PDF.)"}

---
Gere o objeto JSON com a análise (apenas o JSON, sem texto antes ou depois)."""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
        )
        content = (resp.choices[0].message.content or "").strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        out = json.loads(content)
        if "dados_faltantes" not in out:
            out["dados_faltantes"] = []
        return out
    except json.JSONDecodeError as e:
        return {
            "pontos_positivos": [],
            "pontos_negativos": ["Erro ao interpretar análise da IA."],
            "riscos": [],
            "probabilidade_patrocinio": 0,
            "resumo_ai": f"Análise gerada mas formato inválido: {e}",
            "dados_faltantes": [],
        }
    except Exception as e:
        return {
            "pontos_positivos": [],
            "pontos_negativos": [],
            "riscos": [str(e)],
            "probabilidade_patrocinio": 0,
            "resumo_ai": f"Erro na análise por IA: {e}",
            "dados_faltantes": [],
        }
