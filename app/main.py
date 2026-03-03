"""
API e servidor do site events-analysis.
Proponente envia dados e não vê a análise; apenas contas CW podem fazer login e ver as análises.
"""

import os
import secrets
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from src.events_analysis import (
    Event,
    Project,
    analyze_event,
    analyze_project,
    score_sponsorship_potential,
)

app = FastAPI(
    title="Events Analysis",
    description="Envio de eventos/projetos por proponentes; análise visível apenas para CW.",
)

# Armazenamento em memória (em produção use DB)
SUBMISSIONS: list[dict] = []
SESSIONS: dict[str, str] = {}  # token -> username

COOKIE_NAME = "cw_session"
COOKIE_MAX_AGE = 86400 * 7  # 7 dias


# Contas CW permitidas: env (CW_USER, CW_PASSWORD) ou usuários fixos
CW_ALLOWED = [
    ("yasmin.kobayashi@cloudwalk.io", "1234"),
]


def _check_cw_login(username: str, password: str) -> bool:
    """Verifica se usuário e senha são de uma conta CW permitida."""
    if os.environ.get("CW_USER") and os.environ.get("CW_PASSWORD"):
        if username == os.environ["CW_USER"] and password == os.environ["CW_PASSWORD"]:
            return True
    for user, pwd in CW_ALLOWED:
        if username == user and password == pwd:
            return True
    return False


def _get_current_user(request: Request) -> str:
    """Dependency: retorna o username se sessão CW válida."""
    token = request.cookies.get(COOKIE_NAME)
    if not token or token not in SESSIONS:
        raise HTTPException(status_code=401, detail="Acesso restrito a contas CW. Faça login.")
    return SESSIONS[token]


# Modelo de entrada da API (formulário antigo, mantido para compatibilidade)
class AnaliseInput(BaseModel):
    tipo: str = Field(..., description="evento ou projeto")
    nome: str
    descricao: str = ""
    data: str = ""
    local: str = ""
    publico_estimado: int = 0
    tema: str = ""
    formato: str = ""
    objetivo: str = ""
    publico_alvo: str = ""
    duracao_meses: int | None = None
    parceiros: str = ""


# Formulário Seleção de Projetos CW
class ProjetoCWInput(BaseModel):
    # Institucional
    nome_organizacao: str = ""
    cnpj: str = ""
    nome_responsavel: str = ""
    cargo_funcao: str = ""
    email: str = ""
    celular_telefone: str = ""
    # Projeto
    nome_projeto: str = ""
    area_focal: list[str] = Field(default_factory=list)  # múltipla escolha
    publico_atendido: list[str] = Field(default_factory=list)  # múltipla escolha
    local_estado: str = ""
    local_cidades: str = ""
    # Objetivos
    objetivo_geral: str = ""
    objetivo_1: str = ""
    resultado_1: str = ""
    objetivo_2: str = ""
    resultado_2: str = ""
    objetivo_3: str = ""
    resultado_3: str = ""
    objetivo_4: str = ""
    resultado_4: str = ""
    objetivo_5: str = ""
    resultado_5: str = ""
    objetivo_6: str = ""
    resultado_6: str = ""
    # Investimento
    lei_incentivo: bool = False  # True = Sim, False = Não
    valor_direto: str = ""
    leis: list[str] = Field(default_factory=list)  # quais leis se sim
    valor_total_captacao: str = ""
    data_limite_captacao: str = ""
    certificado_base64: str = ""  # arquivo em base64 (opcional)
    certificado_nome: str = ""


class LoginInput(BaseModel):
    username: str
    password: str


def _gerar_resumo_ai_evento(analise: dict, pontuacao: float) -> str:
    partes = []
    nome = analise.get("nome", "Este evento")
    partes.append(f"{nome} foi analisado com foco em potencial de patrocínio.")
    if analise.get("publico_estimado", 0) >= 100:
        partes.append(f"O público estimado de {analise['publico_estimado']} pessoas é um ponto forte para atrair patrocinadores.")
    elif analise.get("publico_estimado", 0) > 0:
        partes.append(f"Considerar estratégias para ampliar o alcance além das {analise['publico_estimado']} pessoas estimadas.")
    if analise.get("formato") in ("presencial", "híbrido"):
        partes.append("O formato presencial ou híbrido tende a ser mais atrativo para marcas que buscam visibilidade presencial.")
    if analise.get("tema"):
        partes.append(f"A segmentação por tema ({analise['tema']}) facilita o match com patrocinadores do setor.")
    partes.append(f"Pontuação de potencial de patrocínio: {pontuacao:.0f}/100.")
    return " ".join(partes)


def _gerar_resumo_ai_projeto(analise: dict, pontuacao: float) -> str:
    partes = []
    nome = analise.get("nome", "Este projeto")
    partes.append(f"{nome} foi analisado quanto ao potencial de patrocínio.")
    if analise.get("tem_parceiros"):
        n = analise.get("quantidade_parceiros", 0)
        partes.append(f"A existência de {n} parceiro(s) reforça a credibilidade e o interesse de outras instituições.")
    if analise.get("duracao_meses") and analise["duracao_meses"] >= 6:
        partes.append("Projetos de maior duração permitem parcerias de longo prazo, o que costuma ser valorizado por patrocinadores.")
    if analise.get("publico_alvo"):
        partes.append(f"Ter um público-alvo definido ({analise['publico_alvo']}) ajuda a comunicar o valor da parceria.")
    partes.append(f"Pontuação de potencial de patrocínio: {pontuacao:.0f}/100.")
    return " ".join(partes)


@app.post("/api/analyze")
def analisar(item: AnaliseInput):
    """Recebe dados do proponente, armazena e processa a análise. O proponente não recebe a análise."""
    try:
        if (item.tipo or "").strip().lower() == "evento":
            if not item.data:
                raise HTTPException(status_code=400, detail="Para evento, informe a data (YYYY-MM-DD).")
            try:
                data_parsed = date.fromisoformat(item.data.strip())
            except ValueError:
                raise HTTPException(status_code=400, detail="Data inválida. Use YYYY-MM-DD.")
            event = Event(
                nome=item.nome,
                data=data_parsed,
                local=item.local or "Não informado",
                publico_estimado=item.publico_estimado or 0,
                descricao=item.descricao or "",
                tema=item.tema or None,
                formato=item.formato or None,
            )
            analise = analyze_event(event)
            pontuacao = score_sponsorship_potential(event)
            resumo_ai = _gerar_resumo_ai_evento(analise, pontuacao)
        else:
            if not item.objetivo:
                raise HTTPException(status_code=400, detail="Para projeto, informe o objetivo.")
            parceiros = [p.strip() for p in (item.parceiros or "").split(",") if p.strip()]
            proj = Project(
                nome=item.nome,
                descricao=item.descricao or "",
                objetivo=item.objetivo,
                publico_alvo=item.publico_alvo or "",
                duracao_meses=item.duracao_meses,
                parceiros=parceiros if parceiros else None,
            )
            analise = analyze_project(proj)
            pontuacao = score_sponsorship_potential(proj)
            resumo_ai = _gerar_resumo_ai_projeto(analise, pontuacao)

        # Armazenar para CW consultar depois; proponente não vê nada disso
        submission = {
            "id": secrets.token_hex(8),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "tipo": item.tipo.strip().lower(),
            "dados": item.model_dump(),
            "analise": analise,
            "pontuacao_patrocinio": round(pontuacao, 1),
            "resumo_ai": resumo_ai,
        }
        SUBMISSIONS.append(submission)

        return {"success": True, "message": "Seus dados foram recebidos. Nossa equipe verificará a análise e entrará em contato se necessário."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _gerar_resumo_projeto_cw(dados: dict) -> str:
    """Gera resumo para exibição CW a partir dos dados do formulário."""
    partes = []
    if dados.get("nome_projeto"):
        partes.append(f"Projeto: {dados['nome_projeto']}.")
    if dados.get("nome_organizacao"):
        partes.append(f"Organização: {dados['nome_organizacao']}.")
    if dados.get("area_focal"):
        partes.append(f"Área focal: {', '.join(dados['area_focal'])}.")
    if dados.get("publico_atendido"):
        partes.append(f"Público: {', '.join(dados['publico_atendido'])}.")
    if dados.get("objetivo_geral"):
        partes.append(f"Objetivo geral: {dados['objetivo_geral'][:200]}{'...' if len(dados.get('objetivo_geral', '')) > 200 else ''}")
    if dados.get("lei_incentivo"):
        partes.append("Solicitação via lei de incentivo.")
    else:
        partes.append("Solicitação para aporte direto.")
    return " ".join(partes) if partes else "Projeto sem resumo."


@app.post("/api/submit-projeto-cw")
def submit_projeto_cw(item: ProjetoCWInput):
    """Recebe formulário de Seleção de Projetos CW. Proponente não vê análise."""
    try:
        dados = item.model_dump()
        # Salvar certificado em disco se enviado (opcional)
        certificado_path = None
        if dados.get("certificado_base64") and dados.get("certificado_nome"):
            import base64
            uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
            uploads_dir.mkdir(exist_ok=True)
            safe_name = "".join(c for c in dados["certificado_nome"] if c.isalnum() or c in "._- ")[:80]
            ext = Path(dados["certificado_nome"]).suffix or ".pdf"
            unique = secrets.token_hex(4)
            certificado_path = str(uploads_dir / f"{unique}_{safe_name}{ext}")
            raw = base64.b64decode(dados["certificado_base64"], validate=True)
            with open(certificado_path, "wb") as f:
                f.write(raw)
        # Não guardar base64 no JSON
        dados.pop("certificado_base64", None)
        dados["certificado_path"] = certificado_path

        resumo = _gerar_resumo_projeto_cw(dados)
        submission = {
            "id": secrets.token_hex(8),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "tipo": "projeto_cw",
            "dados": dados,
            "resumo_ai": resumo,
        }
        SUBMISSIONS.append(submission)
        return {"success": True, "message": "Seus dados foram recebidos. Nossa equipe verificará e entrará em contato se necessário."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/login")
def login(body: LoginInput):
    """Login apenas para contas CW. Define cookie de sessão."""
    if not _check_cw_login(body.username, body.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas. Acesso restrito a contas CW.")
    token = secrets.token_hex(32)
    SESSIONS[token] = body.username
    response = JSONResponse(content={"success": True})
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


@app.post("/api/logout")
def logout(request: Request):
    """Remove a sessão CW."""
    token = request.cookies.get(COOKIE_NAME)
    if token and token in SESSIONS:
        del SESSIONS[token]
    response = JSONResponse(content={"success": True})
    response.delete_cookie(COOKIE_NAME, path="/")
    return response


@app.get("/api/me")
def me(request: Request):
    """Indica se o usuário está logado (conta CW)."""
    token = request.cookies.get(COOKIE_NAME)
    if token and token in SESSIONS:
        return {"logged_in": True, "username": SESSIONS[token]}
    return {"logged_in": False}


@app.get("/api/submissions")
def listar_submissions(_: str = Depends(_get_current_user)):
    """Lista todos os envios com análise. Apenas para usuários CW logados."""
    return {"submissions": list(reversed(SUBMISSIONS))}


# Servir frontend (rotas de página primeiro, depois arquivos estáticos)
static_dir = Path(__file__).resolve().parent.parent / "static"


@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")


@app.get("/login")
def login_page():
    return FileResponse(static_dir / "login.html")


@app.get("/analises")
def analises_page():
    return FileResponse(static_dir / "analises.html")


if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
