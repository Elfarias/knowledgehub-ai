# 🧠 KnowledgeHub AI — Assistente Corporativo de Conhecimento

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/SEU_USUARIO/knowledgehub-ai)
![Apache 2.0 License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)
![Python 3.12](https://img.shields.io/badge/Python-3.12-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)

> **Plataforma open-source de inteligência documental corporativa baseada em RAG (Retrieval-Augmented Generation), projetada para consulta em linguagem natural com rastreabilidade total de evidências.**

---

## 📌 Visão Geral do Projeto

O **KnowledgeHub AI** foi desenvolvido para resolver o desafio corporativo de localização rápida e precisa de informações em bases documentais extensas. O sistema extrai e indexa políticas, manuais e procedimentos internos, permitindo que colaboradores tirem dúvidas em linguagem natural.

Diferente de sistemas convencionais de chat sobre PDFs, o KnowledgeHub AI prioriza a **rastreabilidade e a transparência**: toda resposta gerada apresenta as **fontes exatas**, indicando o nome do documento original, o número da página e o trecho de evidência utilizado.

---

## 🏗️ Arquitetura da Solução

O sistema adota o padrão de **Monólito Modular (Modular Monolith)**, executado localmente via Docker Compose (PostgreSQL) e scripts Python. A arquitetura foi concebida sem frameworks de abstração "caixa-preta" (sem LangChain ou LlamaIndex), garantindo total visibilidade de cada etapa do pipeline RAG.

```mermaid
flowchart TB
    USER[Usuário / Colaborador]

    subgraph LOCAL["Ambiente Local (Python / Docker Compose)"]
        FRONT[Frontend Web<br/>Streamlit]
        API[Backend REST API<br/>FastAPI]

        subgraph MODULES["Módulos Internos do Backend"]
            DOC[Gestão Documental]
            ING[Ingestão & Chunking]
            RAG[Motor RAG]
            CHAT[Chat & Histórico]
        end

        PG[(PostgreSQL<br/>Logs & Auditoria)]
        CH[(ChromaDB<br/>Banco Vetorial)]
        FS[(Filesystem / Docs<br/>Documentos PDF)]

        EMB[Modelo de Embeddings<br/>multilingual-e5-large]
    end

    LLM[Google Gemini API<br/>LLM Externa]

    USER --> FRONT
    FRONT <-->|HTTP REST| API
    API --> MODULES

    DOC --> PG
    DOC --> FS

    ING --> FS
    ING --> EMB
    ING --> CH

    RAG --> EMB
    RAG --> CH
    RAG --> LLM

    CHAT --> PG
    CHAT --> RAG
```

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Função no Sistema |
| :--- | :--- | :--- |
| **Backend & API** | Python 3.12 + FastAPI | API RESTful assíncrona responsável pela orquestração do pipeline RAG. |
| **Frontend Web** | Streamlit | Interface interativa de chat com painel de métricas e suporte a $Top-K$. |
| **Banco Vetorial** | ChromaDB (Local/Embedded) | Armazenamento persistente de embeddings e busca por similaridade de cosseno. |
| **Embeddings** | `intfloat/multilingual-e5-large` | Modelo aberto de 1024 dimensões executado 100% localmente via PyTorch. |
| **Provedor LLM** | Google Gemini API | Geração de respostas sintetizadas fundamentadas no contexto fornecido. |
| **Banco Relacional** | PostgreSQL 16 | Auditoria assíncrona e registro de logs de consultas. |
| **Processamento PDF** | PyMuPDF (`fitz`) | Extração estruturada de texto com rastreabilidade por número de página. |

---

## ☁️ Execução Instantânea via GitHub Codespaces

Para experimentar o projeto imediatamente sem a necessidade de instalar Python, Docker ou dependências na sua máquina local, utilize o **GitHub Codespaces**:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/SEU_USUARIO/knowledgehub-ai)

1. Clique no botão acima para instanciar o ambiente virtual em nuvem.
2. O ambiente configurará automaticamente o contêiner Python 3.12 e instalará os pacotes de `requirements.txt`.
3. Defina sua variável `GEMINI_API_KEY` no terminal ou arquivo `.env`.
4. As portas **8000** (API FastAPI) e **8501** (Interface Streamlit) serão abertas automaticamente para acesso no navegador.

---

## 🗺️ Guia Sequencial de Construção por Fases (`GUIDES/`)

Para desenvolvedores e entusiastas que desejam entender ou reproduzir o processo de construção do KnowledgeHub AI do zero, cada etapa do MVP foi documentada em detalhes na pasta `GUIDES/`:

| Fase | Descrição da Etapa | Documento de Guia Passo a Passo | Status |
| :---: | :--- | :--- | :---: |
| **01** | Setup do Ambiente, Infraestrutura & Backend | 📜 [**PROJECT.md**](GUIDES/PROJECT.md) & ⚙️ [**TECHNOLOGY_STACK.md**](GUIDES/TECHNOLOGY_STACK.md) | 🟢 Concluída |
| **02** | Ingestão, Extração de PDFs & Chunking | 📑 [**DOCUMENT_PROCESSING.md**](GUIDES/DOCUMENT_PROCESSING.md) | 🟢 Concluída |
| **03** | Embeddings Locais & Motor de Recuperação | 🔍 [**Fase 3 — Motor de Recuperação**](GUIDES/Fase%203%20—%20Motor%20de%20Recuperação%20(Retrieval).txt) | 🟢 Concluída |
| **04** | Pipeline RAG & Integração LLM Gemini | 🤖 [**Geração RAG com Google Gemini**](GUIDES/Geração%20RAG%20com%20Google%20Gemini.md) | 🟢 Concluída |
| **05** | Exposição via FastAPI Production-Grade | ⚡ [**Resumo de Execução - Fase 5: FastAPI**](GUIDES/PHASE_5_FastAPI.md) | 🟢 Concluída |
| **06 & 07** | Interface Web (Streamlit) & Validação E2E | 🖥️ [**Fase 6 & 7 — Interface Web e Validação E2E**](GUIDES/PHASE%206_7.MD) | 🟢 Concluída |

---

## 🚀 Como Executar Localmente (Quick Start)

### 1. Pré-requisitos
* Python 3.11 ou 3.12 instalado.
* Docker Desktop ativo (para o PostgreSQL).
* Chave de API do Google Gemini (`GEMINI_API_KEY`).

### 2. Clonar o Repositório e Configurar o Ambiente Virtual
```powershell
git clone https://github.com/SEU_USUARIO/knowledgehub-ai.git
cd knowledgehub-ai

# Criar e ativar o ambiente virtual (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r backend/requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto a partir do modelo `.env.example`:
```env
GEMINI_API_KEY=sua_chave_api_aqui
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/knowledgehub
```

### 4. Inicializar Serviços (Ordem Recomendada)

Execute os seguintes comandos em terminais distintos:

* **Terminal 1 — Banco de Dados (PostgreSQL):**
  ```powershell
  docker compose up -d
  ```

* **Terminal 2 — Processamento de Ingestão (Popular ChromaDB com os PDFs de `Docs/`):**
  ```powershell
  cd backend
  python ingest.py
  ```

* **Terminal 3 — Servidor API Backend (FastAPI):**
  ```powershell
  cd backend
  uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
  ```

* **Terminal 4 — Interface Web (Streamlit):**
  ```powershell
  streamlit run frontend/app.py
  ```

Acesse a interface no seu navegador em: **`http://localhost:8501`**

---

## 📚 Documentação Técnica Completa (`GUIDES/`)

* 📜 [**PROJECT.md**](GUIDES/PROJECT.md) — Visão do produto, problema de negócio e cenário corporativo fictício.
* 🏛️ [**ARCHITECTURE.md**](GUIDES/ARCHITECTURE.md) — Especificação arquitetural do Monólito Modular e diagramas de fluxo.
* ⚙️ [**TECHNOLOGY_STACK.md**](GUIDES/TECHNOLOGY_STACK.md) — Decisões e justificativas técnicas detalhadas da stack.
* 📊 [**PROGRESS.md**](GUIDES/PROGRESS.md) — Matriz de acompanhamento de progresso e histórico das entregas.
* 📑 [**DOCUMENT_PROCESSING.md**](GUIDES/DOCUMENT_PROCESSING.md) — Guia de capacidade e expansão da ingestão multiformato.
* 🚀 [**Guia de Execução & Troubleshooting**](GUIDES/Guia%20de%20Execução%20%26%20Troubleshooting%20—%20KnowledgeHub%20AI.md) — Resolução detalhada de erros comuns de execução.

---

## 📄 Licença

Este projeto é disponibilizado sob a licença [Apache License 2.0](LICENSE).