# events-analysis

Analisa eventos e projetos e pontua o potencial de patrocínio.

## Sobre

- **Eventos**: análise por data, local, público estimado, tema e formato (presencial/híbrido/online).
- **Projetos**: análise por objetivo, público-alvo, duração e parceiros.
- **Patrocínio**: pontuação de 0 a 100 para eventos e projetos.

## Site (front end)

- **Proponente** (qualquer pessoa): envia os dados do evento ou projeto pela web. **Não vê a análise** — apenas uma mensagem de confirmação de que os dados foram recebidos.
- **CW (equipe)**: acesso restrito com login. Após entrar com conta CW, é possível ver todas as análises enviadas (pontuação de patrocínio e resumo).

### Rodar o site localmente

```bash
git clone https://github.com/yaskobayashi/events-analysis.git
cd events-analysis
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Abra no navegador: **http://localhost:8000**

- **Página inicial**: aba Evento ou Projeto, preencha os campos e clique em **Enviar**. O proponente só vê a confirmação; a análise fica disponível apenas para a equipe CW.
- **Login CW**: em **http://localhost:8000/login** (ou pelo link “Acesso CW” no rodapé), entre com usuário e senha CW para acessar **http://localhost:8000/analises** e verificar as análises.

### Contas CW

O login aceita apenas contas CW. Configure usuário e senha por variáveis de ambiente:

```bash
export CW_USER=seu_usuario_cw
export CW_PASSWORD=sua_senha_cw
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Se não definir `CW_USER` e `CW_PASSWORD`, o padrão de desenvolvimento é usuário e senha **cw** (apenas para testes).

### Base de conhecimento (KB) e análise por IA

A análise detalhada dos projetos (pontos positivos, pontos negativos, riscos, probabilidade de patrocínio) usa o PDF **Guide CloudWalk Social 2025** como base de conhecimento. O arquivo fica em `knowledge_base/Guide_CloudWalk_Social_2025.pdf`.

Para ativar a análise por IA (OpenAI), defina a variável de ambiente:

```bash
export OPENAI_API_KEY=sua_chave_aqui
```

Opcional: `OPENAI_MODEL` (padrão: `gpt-4o-mini`).

Sem `OPENAI_API_KEY`, o envio continua funcionando; apenas o resumo automático (sem IA) é exibido na área CW.

## Instalação

```bash
git clone https://github.com/yaskobayashi/events-analysis.git
cd events-analysis
pip install -r requirements.txt
```

## Uso (Python)

```python
from datetime import date
from src.events_analysis import Event, analyze_event, score_sponsorship_potential

evento = Event(
    nome="Tech Meetup",
    data=date(2025, 4, 15),
    local="São Paulo",
    publico_estimado=200,
    tema="tecnologia",
    formato="presencial",
)
print(analyze_event(evento))
print("Potencial:", score_sponsorship_potential(evento))
```

Rodar o exemplo:

```bash
python example.py
```

## Estrutura

```
events-analysis/
├── README.md
├── requirements.txt
├── example.py
├── app/
│   └── main.py            # API FastAPI e servidor do site
├── static/
│   ├── index.html         # Página do proponente (envio, sem análise)
│   ├── login.html         # Login CW
│   ├── analises.html      # Lista de análises (após login)
│   ├── style.css
│   ├── app.js
│   ├── login.js
│   └── analises.js
└── src/
    └── events_analysis/
        ├── __init__.py
        ├── events.py      # análise de eventos
        ├── projects.py    # análise de projetos
        └── sponsorship.py # pontuação de patrocínio
```

## Licença

MIT
