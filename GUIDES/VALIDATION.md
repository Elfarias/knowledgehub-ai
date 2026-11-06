# Estratégia de Testes e Validação — KnowledgeHub AI

## 1. Visão Geral

Este documento define como cada entrega do **KnowledgeHub AI** deve ser testada e validada antes de ser considerada concluída.

A validação no projeto possui dois pilares fundamentais:
1. **Validação Técnica (Integridade & Qualidade):** Garantir que o código funciona, não consome recursos excessivos e passa pelos testes automatizados.
2. **Validação de Negócio (Rastreabilidade & Acurácia):** Garantir que as respostas da LLM estejam fundamentadas em evidências reais extraídas dos documentos, sem alucinações.

## 2. Critérios de Aceite por Fase (Quality Gates)

Para avançar no `IMPLEMENTATION-PLAN.md`, a entrega da fase atual precisa cumprir 100% dos critérios abaixo.

### Fase 1: Setup & Ambiente
- [ ] Container PostgreSQL rodando via `docker compose up -d` e respondendo na porta 5432.
- [ ] Ambiente virtual Python ativado (`venv`) com dependências instaladas sem conflitos.
- [ ] Endpoint `GET /api/v1/health` retornando `{"status": "ok"}` com código HTTP 200.
- [ ] Linter `Ruff` executando sem erros (`ruff check .`).

### Fase 2: Processamento de PDF & Chunking
- [ ] Extração de texto por página via `PyMuPDF` preservando metadados (`documento`, `página`, `departamento`, `versão`).
- [ ] Função de *chunking* dividindo o texto mantendo o *overlap* configurado.
- [ ] Teste unitário (`pytest`) validando se nenhum metadado é perdido ou sobrescrito durante o fatiamento.
- [ ] Verificação visual de amostra de chunks (conferir se não há caracteres corrompidos ou quebras indevidas).

### Fase 3: Embeddings & ChromaDB
- [ ] Modelo `intfloat/multilingual-e5-large` carregado localmente com sucesso.
- [ ] Prefixos `passage: ` e `query: ` aplicados corretamente nos pontos de ingestão e busca.
- [ ] ChromaDB persistindo os vetores em disco na pasta local (`./chroma_db`).
- [ ] Teste de recuperação por similaridade ($k\text{-NN}$) retornando os chunks mais relevantes para uma pergunta de teste.
- [ ] Medição do uso de memória RAM/VRAM durante o processo de geração dos vetores.

### Fase 4: Persistência Relacional (PostgreSQL)
- [ ] Migrações do `Alembic` executadas com sucesso (`alembic upgrade head`).
- [ ] Metadados de documentos e logs de consulta inseridos e recuperados no PostgreSQL via SQLAlchemy.
- [ ] Sincronismo mantido: todo chunk no ChromaDB possui referência ao documento registrado no PostgreSQL.

### Fase 5: Pipeline RAG & API Gemini
- [ ] Endpoint `POST /api/v1/query` operacional.
- [ ] Prompt de contexto montado corretamente injetando os chunks recuperados pelo ChromaDB.
- [ ] Resposta sintetizada pela LLM acompanhada explicitamente da lista de fontes e evidências (Documento, Página, Trecho, Departamento).
- [ ] **Teste de Alucinação (Resistência):** Ao fazer uma pergunta cujo tema **não** consta na base de PDFs, o sistema deve responder expressamente que não encontrou a informação.

### Fase 6: Interface Web (Next.js)
- [ ] Frontend conectando à API backend via TanStack Query.
- [ ] Chat interativo exibindo respostas em tempo real ou com indicador de carregamento.
- [ ] Componente **Cartão de Evidência** permitindo expandir e inspecionar o trecho exato do PDF, a página e a fonte.
- [ ] Linter ESLint e testes de componente Vitest executando sem erros.

## 3. Roteiro de Testes Manuais com Perguntas de Demonstração

Para validar a qualidade da acurácia e da rastreabilidade do RAG na empresa fictícia (ABC Indústria e Serviços Ltda.), utilizaremos a seguinte suíte de testes manuais:

| ID | Pergunta de Teste | Departamento | Evidência Esperada (Validação) |
| --- | --- | --- | --- |
| **T01** | Qual é o prazo para solicitar férias? | RH | Nome da política de RH + número da página + trecho com o prazo. |
| **T02** | Como funciona o reembolso de combustível? | Financeiro | Procedimento financeiro + página + regra de valor/km. |
| **T03** | Qual é o tamanho mínimo exigido para uma senha? | TI | Política de segurança da informação + norma de complexidade. |
| **T04** | Qual é a frequência dos backups? | TI | Procedimento de TI + rotina (diária, semanal, etc.). |
| **T05** | Como registrar uma não conformidade? | Qualidade | Manual da qualidade + formulário ou instrução de registro. |
| **T06** | Qual é o torque especificado na etapa 3 da montagem? | Produção | Instrução de trabalho técnica da produção + valor exato do torque. |
| **T07** | Qual é a política da empresa sobre viagem a Marte? | *Nenhum (Teste de Ausência)* | O sistema deve informar claramente: *"Informação não encontrada nos documentos disponíveis."* |

## 4. Comandos para Execução dos Testes Automatizados

### Backend (Python)
```bash
# Executar verificação de código e estilo
ruff check .

# Executar suíte de testes unitários e de integração
pytest -v

# Executar testes com cobertura de código
pytest --cov=src
```

### Frontend (Next.js)
```bash
# Executar verificação do linter
npm run lint

# Executar testes de componentes
npm run test
```

## 5. Protocolo de Aprovação

Uma etapa só é considerada **CONCLUÍDA** quando:
1. Todos os checkboxes de critérios de aceite da fase estiverem marcados.
2. Os testes automatizados passarem sem falhas.
3. O usuário testar e aprovar manualmente a execução no ambiente local.
4. Os arquivos de documentação (`PROJECT.md`, `ARCHITECTURE.md`, `TECHNOLOGY-STACK.md`, `IMPLEMENTATION-PLAN.md`) forem atualizados para refletir eventuais ajustes feitos durante a fase.
