# Plano de Implementação — KnowledgeHub AI

## 1. Visão Geral do Plano

Este documento estabelece o roteiro detalhado e sequencial de implementação do **KnowledgeHub AI**. A construção segue estritamente a abordagem **uma etapa por vez**, garantindo que cada componente seja testado e compreendido antes de avançar para a fase seguinte.

---

## 2. Fases de Desenvolvimento

```
[Fase 1: Setup & Ambiente] ➔ [Fase 2: Processamento PDF & Chunking] ➔ [Fase 3: Embeddings & ChromaDB]
                                                                                │
[Fase 6: Interface Web] ◄─── [Fase 5: Pipeline RAG & Gemini API] ◄──────────────┘
         │
         ▼
[Fase 7: Validação & Portfólio]
```

---

## 3. Detalhamento Sequencial por Fase

### Fase 1 — Configuração do Ambiente e Estrutura Backend
* **Objetivo:** Preparar a infraestrutura básica de código em Python 3.12 e a estrutura do monólito modular.
* **Tarefas:**
  1. Criar ambiente virtual (`venv`) e arquivo de dependências (`requirements.txt`).
  2. Configurar ferramentas de qualidade (`Ruff`, `.gitignore`, `.env.example`).
  3. Criar a estrutura de pastas do backend (`src/app/modules/...`).
  4. Subir o container PostgreSQL via `docker-compose.yml`.
  5. Inicializar o FastAPI com uma rota de *healthcheck* (`GET /api/v1/health`).
* **Critério de Aceite:** API rodando na porta 8000, container Postgres ativo e testes básicos passando com `pytest`.

---

### Fase 2 — Ingestão de PDFs e Chunking Estruturado
* **Objetivo:** Processar os PDFs locais da empresa fictícia (ABC Indústria), extraindo o texto página a página sem perder metadados.
* **Tarefas:**
  1. Implementar o extrator de PDF utilizando `PyMuPDF` (`fitz`).
  2. Criar a lógica de limpeza de texto (remoção de caracteres nulos, espaços duplicados).
  3. Implementar a estratégia de *chunking* recursivo em Python puro (tamanho fixo de caracteres/tokens com *overlap*).
  4. Vincular metadados obrigatórios a cada chunk (nome do arquivo, página, departamento, versão, data).
* **Critério de Aceite:** Script que lê um PDF de teste e gera uma lista de chunks tipados com metadados preservados.

---

### Fase 3 — Embeddings Locais e Banco Vetorial ChromaDB
* **Objetivo:** Gerar representações vetoriais dos chunks e armazená-los para consulta de alta performance.
* **Tarefas:**
  1. Integrar o modelo local `intfloat/multilingual-e5-large` via `sentence-transformers`.
  2. Implementar a regra de prefixos obrigatórios (`passage:` para indexação e `query:` para busca).
  3. Configurar a instância do `ChromaDB` em modo persistente local.
  4. Criar rotas/scripts de ingestão para gravar os chunks e vetores no ChromaDB.
  5. Implementar testes de recuperação por similaridade de cosseno ($k\text{-NN}$).
* **Critério de Aceite:** Consultar uma frase de teste no ChromaDB e retornar os chunks mais semelhantes acompanhados dos metadados corretos.

---

### Fase 4 — Persistência Relacional de Metadados e Histórico
* **Objetivo:** Salvar informações estruturadas de documentos, coleções e histórico de perguntas no PostgreSQL.
* **Tarefas:**
  1. Configurar o `SQLAlchemy 2.0` (modo `asyncio`) e gerenciar migrações com `Alembic`.
  2. Criar modelos relacionais (`Document`, `ChunkMetadata`, `QueryLog`).
  3. Sincronizar o status da ingestão entre o banco relacional e o ChromaDB.
* **Critério de Aceite:** Ingestão registrada com sucesso no PostgreSQL e rastreabilidade gravada no banco de dados.

---

### Fase 5 — Pipeline RAG e Integração com LLM (Google Gemini)
* **Objetivo:** Orquestrar o fluxo completo de busca por contexto e geração da resposta com evidências rastreáveis.
* **Tarefas:**
  1. Configurar o cliente da API do **Google Gemini** isolado em um módulo (`services/llm.py`).
  2. Construir a montagem dinâmica do *prompt* de contexto injetando os chunks resgatados pelo ChromaDB.
  3. Implementar a regra rigorosa: responder **somente** com base no contexto fornecido e indicar explicitamente quando a informação não for encontrada.
  4. Estruturar a resposta da API para retornar o texto da LLM + a lista explicita de fontes/evidências (Documento, Página, Trecho, Departamento).
  5. Tratar erros, limites de API (*rate limits*) e exceções.
* **Critério de Aceite:** Endpoint `POST /api/v1/query` recebendo uma pergunta e retornando uma resposta fundamentada com citações verificáveis.

---

### Fase 6 — Interface Web (Frontend Next.js)
* **Objetivo:** Criar uma interface web amigável e reativa para interação do usuário.
* **Tarefas:**
  1. Inicializar o projeto `Next.js` com TypeScript e `Tailwind CSS`.
  2. Instalar e configurar componentes do `shadcn/ui`.
  3. Criar a tela de Chat (input de pergunta, histórico de mensagens).
  4. Criar o componente de **Cartão de Evidência** para exibir as fontes resgatadas (nome do documento, página e trecho).
  5. Integrar com a API via `TanStack Query`.
* **Critério de Aceite:** Usuário realiza uma pergunta na interface, visualiza a resposta digitada/gerada e pode expandir os detalhes de cada evidência.

---

### Fase 7 — Testes, Documentação Final e Portfólio
* **Objetivo:** Consolidar o repositório open-source com qualidade profissional.
* **Tarefas:**
  1. Executar testes de ponta a ponta (E2E) com as perguntas de demonstração do cenário empresarial.
  2. Validar métricas de consumo de memória (RAM/VRAM) e tempo de resposta.
  3. Atualizar a documentação do GitHub (`README.md`, instrução de instalação local via Docker).
  4. Gravar a demonstração do sistema funcional para apresentação de portfólio.
* **Critério de Aceite:** Projeto completamente executável localmente a partir de um comando e documentação 100% alinhada com o código final.

---

## 4. Próxima Etapa Imediata

Conforme definido no planejamento, o próximo passo é dar início à **Fase 1 (Setup & Ambiente)**, criando a estrutura básica do projeto Python, o ambiente virtual e as dependências fundamentais.