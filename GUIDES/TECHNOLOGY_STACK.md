# Stack Tecnológica — KnowledgeHub AI

## 1. Visão Geral da Stack

O **KnowledgeHub AI** adota uma arquitetura de monólito modular simples, robusta e orientada à facilidade de execução local e aprendizado prático.

| Camada | Tecnologia | Descrição e Função |
| :--- | :--- | :--- |
| **Interface (Frontend)** | Next.js (React + TypeScript) | Interface web moderna, tipada e reativa para interação via chat e visualização de evidências. |
| **Estilização** | Tailwind CSS + shadcn/ui | Sistema de design e componentes flexíveis, responsivos e acessíveis. |
| **Gerenciamento de Estado/API** | TanStack Query (React Query) | Gerenciamento eficiente de chamadas à API, cache local e estados de carregamento. |
| **Backend & API** | Python 3.12 + FastAPI | API RESTful assíncrona, rápida e leve, responsável pela orquestração do pipeline RAG. |
| **Validação de Dados** | Pydantic v2 | Validação rigorosa de schemas de dados de entrada/saída no backend. |
| **Persistência Relacional** | PostgreSQL 16 + SQLAlchemy 2.0 | Armazenamento de metadados de documentos, histórico de consultas, usuários e logs. |
| **Migrações de Banco** | Alembic | Gerenciamento e versionamento de schemas de banco de dados relacional. |
| **Banco Vetorial** | ChromaDB (modo local/embedded) | Armazenamento persistente de embeddings e execução de busca por similaridade de cosseno. |
| **Processamento de PDF** | PyMuPDF (fitz) | Extração rápida e precisa de texto por página mantendo índice e metadados. |
| **Modelo de Embedding** | `intfloat/multilingual-e5-large` | Modelo aberto de 1024 dimensões executado localmente (PyTorch / SentenceTransformers). |
| **Provedor LLM** | Google Gemini API | Geração de respostas sintetizadas em linguagem natural fundamentadas nas evidências recuperadas. |
| **Infraestrutura Local** | Docker & Docker Compose | Padronização dos serviços dependentes (PostgreSQL) para ambiente de desenvolvimento local. |
| **Qualidade e Testes** | Ruff + pytest (Backend) / ESLint + Vitest (Frontend) | Linting, formatação e suíte de testes unitários e de integração. |

## 2. Detalhemento e Justificativas Técnicas

### 2.1 Backend & Linguagem Base: Python 3.12 + FastAPI
* **Função:** Núcleo do sistema, orquestrando o fluxo entre extração, geração de embeddings, busca vetorial e chamada à LLM.
* **Justificativa:** Python é o ecossistema padrão para IA e Ciência de Dados. FastAPI entrega desempenho assíncrono (ASGI), documentação automática OpenAPI (Swagger) e integração nativa com Pydantic.
* **Alternativas consideradas:**
* *Node.js/Express:* Ecossistema de IA menos maduro para modelos locais de embedding.
* *Django:* Excesso de abstrações ("batteries included") desnecessárias para um monólito modular focado em API REST.

### 2.2 Extração de Documentos: PyMuPDF (`fitz`)
* **Função:** Ler os arquivos PDF corporativos da pasta local e extrair o texto limpo mantendo a rastreabilidade por número de página.
* **Justificativa:** Extremamente rápido, baixo uso de CPU/memória em comparação com outras bibliotecas Python e alta fidelidade na ordenação de texto por página.
* **Alternativas consideradas:**
* *pdfplumber:* para tabelas, porém significativamente mais lento para volume médio de documentos.
* *pypdf / PyPDF2:* Menos preciso na extração e parsing de layout.

### 2.3 Modelo de Embeddings: `intfloat/multilingual-e5-large`
* **Função:** Converter trechos de texto (*chunks*) e perguntas em vetores numéricos densos de 1024 dimensões.
* **Justificativa:** Modelo open-source multilíngue com estado da arte em suporte ao português. Permite execução 100% local sem custos por chamada de API.
* **Observação de Uso:** Requer o uso estrito dos prefixos de instrução:
* Passagens de documentos: `passage: <texto>`
* Perguntas de busca: `query: <texto>`
* **Alternativas consideradas:**
* *OpenAI text-embedding-3-small:* Exige envio de dados para API externa e custo recorrente.
* *sentence-transformers/all-MiniLM-L6-v2:* Muito leve, porém fraco para a língua portuguesa.

### 2.4 Banco Vetorial: ChromaDB (Embedded)
* **Função:** Armazenar os vetores de embedding e seus metadados (documento, página, departamento) e realizar busca por k-NN (k-Nearest Neighbors).
* **Justificativa:** Pode ser executado de forma embarcada (in-process) salvando dados no sistema de arquivos local, sem a necessidade de gerenciar um cluster complexo no MVP.
* **Alternativas consideradas:**
* *pgvector (extensão PostgreSQL):* opção, mas ChromaDB simplifica o isolamento do aprendizado de busca vetorial no início do projeto.
* *Pinecone / Qdrant Cloud:* Dependências de SaaS gerenciados fora do escopo open-source/local.

### 2.5 Modelo de Linguagem (LLM): Google Gemini API
* **Função:** Receber o contexto montado com as evidências resgatadas pelo ChromaDB e formular uma resposta precisa, direta e acompanhada das citações de fontes.
* **Justificativa:** suporte ao português, janela de contexto ampla, baixo custo (tier gratuito/acessível para dev) e API simples de integrar via pacote oficial `google-genai`.
* **Alternativas consideradas:**
* *Ollama / Local LLM (Llama 3, Mistral):* Requer alto consumo de VRAM/GPU local para inferência fluida.
* *OpenAI GPT-4o-mini:* Alternativa viável, mantida como opção secondary fallback.

### 2.6 Persistência Relacional: PostgreSQL + SQLAlchemy 2.0
* **Função:** Registrar a estrutura dos documentos ingestados, metadados formais, histórico de buscas executadas, usuários e logs do sistema.
* **Justificativa:** Banco de dados relacional padrão da indústria. SQLAlchemy 2.0 oferece suporte nativo a estilo assíncrono (`asyncio`) em Python.

### 2.7 Frontend: Next.js + Tailwind CSS + shadcn/ui
* **Função:** Interface rica onde o usuário digita perguntas, visualiza as respostas sintetizadas e inspeciona as evidências (cartões detalhando documento, página e trecho exato).
* **Justificativa:** React com Next.js (App Router) permite renderização eficiente e tipagem sólida com TypeScript. Tailwind CSS e shadcn/ui garantem agilidade no design.

## 3. Abordagem Sem Frameworks de Alto Nível no MVP

Para cumprir o objetivo educacional e de portfólio, **NÃO** serão utilizados frameworks de abstração RAG no MVP, tais como:
* **LangChain** (não utilizado no MVP)
* **LlamaIndex** (não utilizado no MVP)

### Raciocínio Técnico
Frameworks como LangChain escondem etapas cruciais sob abstrações ("black boxes"). No **KnowledgeHub AI**, a implementação das seguintes etapas será feita diretamente em código Python puro:
1. Divisão do texto em páginas e chunks (*chunking strategy* com overlap).
2. Cálculo manual e formatação de payloads para o modelo de embeddings.
3. Montagem do prompt de contexto estruturado para a LLM.
4. Mapeamento e vinculação direta da resposta final aos metadados de origem (*traceability*).

## 4. O que foi Deliberadamente Excluído do MVP

Para priorizar a simplicidade, facilidade de manutenção e aprendizado estruturado, os seguintes elementos **NÃO** fazem parte da fase atual:

1. **Arquitetura de Microserviços:** O sistema é um monólito modular simples.
2. **Filas e Processamento Assíncrono Complexo (Celery / RabbitMQ / Kafka):** O fluxo de ingestão será síncrono ou com background tasks leves nativas do FastAPI.
3. **Armazenamento em Nuvem (AWS S3 / Azure Blob Storage):** Os arquivos originais permanecem na pasta do sistema de arquivos local.
4. **Cache distribuído (Redis):** Sem necessidade de cacheamento em memória distribuído nesta fase.
5. **OCR (Reconhecimento Óptico de Caracteres):** Assume-se que os PDFs da empresa fictícia possuem camada de texto pesquisável.
6. **Orquestração de Containers em Produção (Kubernetes / Helm):** Apenas Docker Compose para ambiente dev local.
7. **Autenticação Complexa (SSO / OAuth2 / Keycloak):** O foco inicial está na acurácia do RAG.

## 5. Ferramentas de Desenvolvimento e Qualidade

* **Git & GitHub:** Versionamento com commits semânticos (`feat:`, `fix:`, `docs:`).
* **Ruff:** Linter e formatador de código Python ultrarrápido (substitui Flake8, Black e isort).
* **pytest + HTTPX:** Testes de integração das rotas FastAPI e testes unitários de chunking.
* **ESLint + Prettier:** Padronização e qualidade de código no frontend.
* **Docker Compose:** Execução em um comando (`docker compose up -d`) do PostgreSQL.

## 6. Política de Versionamento e Evolução da Stack

1. **Estabilidade em Primeiro Lugar:** As versões das bibliotecas principais serão fixadas no `requirements.txt` (Python) e `package.json` (Node.js).
2. **Atualização Justificada:** Novas bibliotecas só serão adicionadas se resolverem uma limitação real não atendida pelo código padrão.
3. **Documentação Viva:** Qualquer alteração na escolha de componentes nesta stack exige a atualização imediata deste documento.
