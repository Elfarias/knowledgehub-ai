# 🧠 KnowledgeHub AI — Assistente Corporativo de Conhecimento

> **Plataforma open-source de inteligência documental corporativa baseada em RAG (Retrieval-Augmented Generation), projetada para consulta em linguagem natural com rastreabilidade total de evidências.**

## 📌 Visão Geral do Projeto

O **KnowledgeHub AI** foi desenvolvido para resolver o desafio corporativo de localização rápida e precisa de informações em bases documentais extensas. O sistema extrai e indexa políticas, manuais e procedimentos internos de uma empresa fictícia (*ABC Indústria e Serviços Ltda.*), permitindo que colaboradores tirem dúvidas em linguagem natural.

Diferente de sistemas convencionais de chat sobre PDFs, o KnowledgeHub AI prioriza a **rastreabilidade e a transparência**: toda resposta gerada apresenta as **fontes exatas**, indicando o nome do documento original, o número da página e o trecho de evidência utilizado.

## 🏗️ Arquitetura da Solução

O sistema adota o padrão de **Monólito Modular (Modular Monolith)**, executado localmente via Docker Compose (PostgreSQL) e scripts Python. A arquitetura foi concebida sem frameworks de abstração "caixa-preta" (sem LangChain ou LlamaIndex), garantindo total visibilidade e controle sobre cada etapa do pipeline RAG.

```mermaid
flowchart TD
    USER[👤 Usuário / Colaborador]

    subgraph APP ["🏢 Ambiente Local (Python / Docker)"]
        direction TB
        FRONT[🖥️ Frontend Web — Streamlit]
        API[⚡ Backend REST API — FastAPI]
        
        subgraph MODULES ["⚙️ Módulos de Negócio (Backend)"]
            direction LR
            DOC[📁 Gestão Documental]
            ING[⚙️ Ingestão & Chunking]
            RAG[🧠 Motor RAG]
            CHAT[💬 Chat & Histórico]
        end
        
        subgraph STORAGE ["💾 Persistência & Embeddings"]
            direction LR
            PG[(🗄️ PostgreSQL<br/>Logs & Auditoria)]
            CH[(🔍 ChromaDB<br/>Banco Vetorial)]
            FS[(📄 Filesystem<br/>PDFs Originais)]
            EMB[🔤 Embeddings<br/>multilingual-e5-large]
        end
    end

    LLM[🤖 Google Gemini API<br/>Provedor LLM]

    USER <--> FRONT
    FRONT <--> API
    API --> MODULES

    ING --> FS
    ING --> EMB
    ING --> CH

    RAG --> CH
    RAG --> LLM

    CHAT --> PG
    CHAT --> RAG

    classDef userStyle fill:#4A90E2,stroke:#1C5296,stroke-width:2px,color:#fff,font-weight:bold;
    classDef apiStyle fill:#2E7D32,stroke:#1B5E20,stroke-width:2px,color:#fff,font-weight:bold;
    classDef moduleStyle fill:#FFF3E0,stroke:#E65100,stroke-width:1px,color:#000;
    classDef dataStyle fill:#E1F5FE,stroke:#0288D1,stroke-width:1px,color:#000;
    classDef llmStyle fill:#7B1FA2,stroke:#4A148C,stroke-width:2px,color:#fff,font-weight:bold;

    class USER userStyle;
    class API apiStyle;
    class DOC,ING,RAG,CHAT moduleStyle;
    class PG,CH,FS,EMB dataStyle;
    class LLM llmStyle;
```

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Função no Sistema | 
| ----- | ----- | ----- | 
| **Backend & API** | Python 3.12 + FastAPI | API RESTful assíncrona responsável pela orquestração do pipeline RAG. | 
| **Frontend Web** | Streamlit | Interface interativa de chat com painel de métricas e suporte a $Top-K$. | 
| **Banco Vetorial** | ChromaDB (Local/Embedded) | Armazenamento persistente de embeddings e busca por similaridade de cosseno. | 
| **Embeddings** | `intfloat/multilingual-e5-large` | Modelo aberto de 1024 dimensões executado 100% localmente via PyTorch. | 
| **Provedor LLM** | Google Gemini API | Geração de respostas sintetizadas fundamentadas no contexto fornecido. | 
| **Banco Relacional** | PostgreSQL 16 | Auditoria assíncrona e registro de logs de consultas. | 
| **Processamento PDF** | PyMuPDF (`fitz`) | Extração estruturada de texto com rastreabilidade por número de página. | 

## ☁️ Execução Instantânea via GitHub Codespaces

Para experimentar o projeto imediatamente sem a necessidade de instalar Python, Docker ou dependências na sua máquina local, utilize o **GitHub Codespaces**:

1. Instancie o ambiente virtual em nuvem pelo GitHub Codespaces no repositório.
2. O ambiente configurará automaticamente o contêiner Python 3.12 e instalará os pacotes de `requirements.txt`.
3. Defina sua variável `GEMINI_API_KEY` no terminal ou arquivo `.env`.
4. As portas **8000** (API FastAPI) e **8501** (Interface Streamlit) serão abertas automaticamente para acesso no navegador.

## 🗺️ Guia Sequencial de Construção por Fases (`GUIDES/`)

Para desenvolvedores e entusiastas que desejam entender ou reproduzir o processo de construção do KnowledgeHub AI, cada etapa do MVP foi documentada em detalhes na pasta `GUIDES/`:

| Fase | Descrição da Etapa | Documento de Guia Passo a Passo | Status | 
| ----- | ----- | ----- | ----- | 
| **01** | Setup do Ambiente, Infraestrutura & Backend | 📜 [**PROJECT.md**](GUIDES/PROJECT.md) & ⚙️ [**TECHNOLOGY_STACK.md**](GUIDES/TECHNOLOGY_STACK.md) | 🟢 Concluída | 
| **02** | Ingestão, Extração de PDFs & Chunking | 📑 [**DOCUMENT_PROCESSING.md**](GUIDES/DOCUMENT_PROCESSING.md) | 🟢 Concluída | 
| **03** | Embeddings Locais & Motor de Recuperação | 🔍 [**Fase 3 — Motor de Recuperação**](GUIDES/PHASE-3-RETRIEVAL.md) | 🟢 Concluída | 
| **04** | Pipeline RAG & Integração LLM Gemini | 🤖 [**Geração RAG com Google Gemini**](GUIDES/Geração%20RAG%20com%20Google%20Gemini.md) | 🟢 Concluída | 
| **05** | Exposição via FastAPI Production-Grade | ⚡ [**Resumo de Execução - Fase 5: FastAPI**](GUIDES/PHASE_5_FastAPI.md) | 🟢 Concluída | 
| **06 & 07** | Interface Web (Streamlit) & Validação E2E | 🖥️ [**Fase 6 & 7 — Interface Web e Validação E2E**](GUIDES/PHASE%206_7.MD) | 🟢 Concluída | 
| **FASE 2** | Roadmap de RAG Avançado & Avaliação Corporativa | 🗺️ [**Roadmap de Implantação - Fase 2**](GUIDES/ROADMAP_PHASE_2.md) | 🟡 Em Planejamento |

## 🚀 Como Executar Localmente (Quick Start)

### 1. Pré-requisitos
* Python 3.11 ou 3.12 instalado.
* Docker Desktop ativo (para o PostgreSQL).
* Chave de API do Google Gemini (`GEMINI_API_KEY`).

### 2. Clonar o Repositório e Configurar o Ambiente Virtual
```bash
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
  ```bash
  docker compose up -d
  ```

* **Terminal 2 — Processamento de Ingestão (Popular ChromaDB com os PDFs de `Docs/`):**
  ```bash
  cd backend
  python ingest.py
  ```

* **Terminal 3 — Servidor API Backend (FastAPI):**
  ```bash
  cd backend
  uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
  ```

* **Terminal 4 — Interface Web (Streamlit):**
  ```bash
  streamlit run frontend/app.py
  ```

Acesse a interface no seu navegador em: **`http://localhost:8501`**

## 🔮 Próximos Passos (Roadmap de Evolução — Fase 2)

Com a entrega do MVP funcional da Fase 1, a próxima etapa de desenvolvimento está detalhada no [**Roadmap de Implantação — Fase 2**](GUIDES/ROADMAP_PHASE_2.md), englobando as seguintes evoluções de engenharia:

1. **Busca Híbrida (Dense + Sparse Retrieval):** Combinação do motor vetorial ChromaDB com busca por palavras-chave via **BM25** e fusão por *Reciprocal Rank Fusion (RRF)* para garantir recuperação exata de códigos e siglas corporativas.
2. **Filtros Dinâmicos por Metadados:** Filtragem pré-busca por departamento (ex: `RH`, `Financeiro`, `Jurídico`) garantindo isolamento de contexto.
3. **Avaliação Automatizada (*LLM as a Judge* / *Ragas*):** Criação de dataset de teste de referência (*Gold Standard*) para medição contínua de fidelidade (*faithfulness*), relevância (*answer relevance*) e precisão de contexto.
4. **Auto-Correção e Fallback (Self-Corrective RAG):** Verificação de limiares de relevância para acionamento de guardrails quando a base documental não contiver a resposta desejada.

Para conferir o plano detalhado de tarefas, consulte o [**GUIDES/ROADMAP_PHASE_2.md**](GUIDES/ROADMAP_PHASE_2.md).

## 📚 Documentação Técnica Completa (`GUIDES/`)

* 📜 [**PROJECT.md**](GUIDES/PROJECT.md) — Visão do produto, problema de negócio e cenário corporativo fictício.
* 🏛️ [**ARCHITECTURE.md**](GUIDES/ARCHITECTURE.md) — Especificação arquitetural do Monólito Modular e diagramas de fluxo.
* ⚙️ [**TECHNOLOGY_STACK.md**](GUIDES/TECHNOLOGY_STACK.md) — Decisões e justificativas técnicas detalhadas da stack.
* 📊 [**PROGRESS.md**](GUIDES/PROGRESS.md) — Matriz de acompanhamento de progresso e histórico das entregas.
* 📑 [**DOCUMENT_PROCESSING.md**](GUIDES/DOCUMENT_PROCESSING.md) — Guia de capacidade e expansão da ingestão multiformato.
* 🚀 [**Guia de Execução & Troubleshooting**](GUIDES/Guia%20de%20Execução%20%26%20Troubleshooting%20—%20KnowledgeHub%20AI.md) — Resolução detalhada de erros comuns de execução.
* 🗺️ [**ROADMAP_PHASE_2.md**](GUIDES/ROADMAP_PHASE_2.md) — Plano de execução auto-contido para a evolução RAG da Fase 2.

## 👨‍💻 Autor & Desenvolvimento

O **KnowledgeHub AI** foi concebido e implementado por **Elon de Farias Pereira**, com foco em engenharia de software aplicada, clareza arquitetural e domínio sobre o pipeline RAG.

A solução prioriza o controle explícito sobre todas as etapas do fluxo RAG (chunking, vetorização, prompt grounding e rastreabilidade de evidências), evitando dependências de frameworks de alta abstração.

## 📄 Licença

Este projeto é disponibilizado sob a licença [Apache License 2.0](LICENSE).