# Fase 6 e 7 — Interface Web e Validação Ponta a Ponta (E2E)

As etapas de execução compreendem:

### Planejamento da Fase 6 & 7

1\. **Setup da Interface Web (Streamlit):** Instalação da biblioteca no ambiente virtual Python (`venv`) e criação da estrutura do módulo `frontend/`.

2\. **Construção do Dashboard (`frontend/app.py`):**

* **Barra Lateral (Sidebar):** Health check em tempo real conectando à rota `GET /health` e controle deslizante (*slider*) para o parâmetro $Top-K$.

* **Área Principal de Chat:** Interface interativa de perguntas e respostas com retenção do histórico de conversa na sessão.

* **Cartão de Evidências (Rastreabilidade):** Exibição das fontes documentais (nome do arquivo PDF e número da página) abaixo de cada resposta.

3\. **Validação E2E (Ponta a Ponta):** Execução conjunta do backend (FastAPI/Uvicorn) e frontend (Streamlit) com testes práticos de perguntas com e sem evidências no banco.

### ️ Passo 1: Instalar Dependências do Frontend

Instalação das dependências via terminal com o ambiente virtual `venv` ativado: o `streamlit` e a biblioteca `requests` para comunicação HTTP com a API FastAPI:

```powershell

pip install streamlit requests

```

### Passo 2: Criar o Código da Interface Web

Estrutura do arquivo `frontend/app.py`:

```python

"""

Interface Web em Streamlit para o KnowledgeHub AI.

Conecta-se ao serviço FastAPI na porta 8000 para consulta RAG e exibição de fontes.

"""

import streamlit as st

import requests

\# Configuração visual e título da aplicação

st.set\_page\_config(

&#x20; page\_title="KnowledgeHub AI",

&#x20; page\_icon="🧠",

&#x20; layout="wide"

)

API\_BASE\_URL = "http://localhost:8000"

st.title("🧠 KnowledgeHub AI — Assistente Corporativo")

st.caption("Consulte a base de conhecimento interna com respostas fundamentadas em evidências documentais.")

\# --- BARRA LATERAL: Status da API e Parâmetros ---

with st.sidebar:

&#x20; st.header("️ Status \& Configurações")

&#x20;

&#x20; # Validação do Health Check da API FastAPI

&#x20; try:

&#x20; health\_resp = requests.get(f"{API\_BASE\_URL}/health", timeout=3)

&#x20; if health\_resp.status\_code == 200:

&#x20; health\_data = health\_resp.json()

&#x20; st.success("🟢 API Conectada")

&#x20; st.metric(label="Documentos Indexados", value=health\_data.get("documents\_indexed", 0))

&#x20; st.info(f"\*\*Provedor LLM:\*\*\\n{health\_data.get('llm\_provider', 'N/A')}")

&#x20; else:

&#x20; st.error("🔴 API com Instabilidade")

&#x20; except Exception:

&#x20; st.error("🔴 API Offline\\n\\nCertifique-se de que o Uvicorn está rodando na porta 8000.")

&#x20; st.divider()

&#x20;

&#x20; # Parâmetro Top-K para controle de recuperação

&#x20; top\_k = st.slider(

&#x20; "Quantidade de fontes a recuperar (Top-K):",

&#x20; min\_value=1,

&#x20; max\_value=10,

&#x20; value=3,

&#x20; help="Quantidade de trechos (chunks) que o ChromaDB buscará para montar o contexto do LLM."

&#x20; )

\# --- HISTÓRICO DE CHAT DA SESSÃO ---

if "messages" not in st.session\_state:

&#x20; st.session\_state.messages = \[]

\# Exibe o histórico de mensagens

for message in st.session\_state.messages:

&#x20; with st.chat\_message(message\["role"]):

&#x20; st.markdown(message\["content"])

&#x20; if "sources" in message and message\["sources"]:

&#x20; with st.expander(" Fontes Consultadas"):

&#x20; for idx, src in enumerate(message\["sources"], 1):

&#x20; st.write(f"\*\*{idx}.\*\* Documento: `{src.get('source')}` | Página: `{src.get('page')}`")

\# --- ENTRADA DA PERGUNTA DO USUÁRIO ---

if prompt := st.chat\_input("Faça uma pergunta sobre as políticas corporativas..."):

&#x20; # 1. Registra e exibe a pergunta do usuário

&#x20; st.session\_state.messages.append({"role": "user", "content": prompt})

&#x20; with st.chat\_message("user"):

&#x20; st.markdown(prompt)

&#x20; # 2. Chama a API RAG FastAPI e exibe a resposta

&#x20; with st.chat\_message("assistant"):

&#x20; with st.spinner("Buscando no banco vetorial e sintetizando a resposta..."):

&#x20; try:

&#x20; payload = {"query": prompt, "top\_k": top\_k}

&#x20; response = requests.post(f"{API\_BASE\_URL}/api/v1/query", json=payload, timeout=30)

&#x20;

&#x20; if response.status\_code == 200:

&#x20; data = response.json()

&#x20; answer = data.get("answer", "Sem resposta do servidor.")

&#x20; sources = data.get("sources", \[])

&#x20;

&#x20; st.markdown(answer)

&#x20;

&#x20; if sources:

&#x20; with st.expander(" Fontes Consultadas"):

&#x20; for idx, src in enumerate(sources, 1):

&#x20; st.write(f"\*\*{idx}.\*\* Documento: `{src.get('source')}` | Página: `{src.get('page')}`")

&#x20;

&#x20; # Salva a resposta no histórico da sessão

&#x20; st.session\_state.messages.append({

&#x20; "role": "assistant",

&#x20; "content": answer,

&#x20; "sources": sources

&#x20; })

&#x20; else:

&#x20; st.error(f"Erro da API ({response.status\_code}): {response.text}")

&#x20;

&#x20; except requests.exceptions.ConnectionError:

&#x20; st.error("Não foi possível conectar à API. Verifique se o servidor FastAPI (Uvicorn) está rodando em http://localhost:8000.")

&#x20; except Exception as e:

&#x20; st.error(f"Erro inesperado: {str(e)}")

```

### Passo 3: Como Executar a Aplicação Completa

Para execução da aplicação completa, são necessários dois terminais simultâneos:

1\. **Terminal 1 — Backend (FastAPI):**

```powershell

uvicorn backend.app.main:app --reload --port 8000

```

2\. **Terminal 2 — Frontend (Streamlit):**

```powershell

streamlit run frontend/app.py

```

O navegador abrirá automaticamente a interface em `http://localhost:8501`.

A execução dos comandos acima inicializa o backend e o frontend simultaneamente.
