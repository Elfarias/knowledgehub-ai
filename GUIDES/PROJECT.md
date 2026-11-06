# PROJECT.md

# KnowledgeHub AI

### Assistente Corporativo de Conhecimento

**Open-source enterprise document intelligence platform powered by RAG.**

| Informação | Definição |

|---|---|

| Projeto | KnowledgeHub AI |

| Tipo | Plataforma de inteligência documental corporativa |

| Categoria | Inteligência Artificial / RAG |

| Versão inicial | MVP 0.1 |

| Licença | Apache License 2.0 |

| Idioma principal | Português (Brasil) |

| Ambiente | Execução local |

| LLM | Serviço externo, inicialmente Google Gemini |

## 1. Visão do Projeto

O KnowledgeHub AI é uma plataforma de inteligência documental corporativa que utiliza técnicas de Retrieval-Augmented Generation (RAG) para permitir que colaboradores consultem documentos empresariais utilizando linguagem natural.

O sistema transforma documentos corporativos em uma base de conhecimento pesquisável, permitindo localizar informações, compreender políticas e consultar procedimentos sem precisar procurar manualmente em diversos arquivos.

O objetivo não é construir apenas um chatbot que responde perguntas sobre PDFs, mas uma aplicação que permita recuperar informações corporativas com rastreabilidade e evidências documentais.

Toda resposta deverá, sempre que possível, apresentar:

- Resposta em linguagem natural.

- Documento utilizado como fonte.

- Página de origem.

- Trecho que sustenta a resposta.

- Versão e data do documento.

## 2. Problema de Negócio

Empresas possuem documentos distribuídos entre departamentos, áreas e diferentes responsáveis.

Quando um colaborador precisa encontrar uma informação, frequentemente enfrenta dificuldades para:

- Identificar qual documento contém a informação.

- Encontrar a informação dentro de documentos extensos.

- Identificar a versão correta de um documento.

- Localizar a página onde a informação está registrada.

- Diferenciar informações oficiais de interpretações pessoais.

O KnowledgeHub AI busca resolver esse problema por meio de uma interface de consulta inteligente, conectada a uma base documental corporativa.

## 3. Objetivos

### 3.1 Objetivo principal

Construir uma plataforma funcional de consulta inteligente a documentos corporativos, utilizando arquitetura RAG, com respostas fundamentadas em fontes documentais.

### 3.2 Objetivos de aprendizagem

O projeto também possui finalidade educacional e de desenvolvimento técnico.

Durante sua construção, deverão ser explorados:

- Conceitos e arquitetura de RAG.

- Extração e processamento de documentos.

- Técnicas de chunking.

- Modelos de embeddings.

- Banco de dados vetorial.

- Busca semântica.

- Recuperação de contexto.

- Integração com LLM.

- Engenharia de prompts.

- Construção de APIs.

- Integração entre frontend e backend.

- Persistência de dados.

- Containerização com Docker.

- Versionamento e documentação no GitHub.

### 3.3 Objetivo de portfólio

Demonstrar capacidade de projetar, construir, executar, testar e documentar uma aplicação de inteligência artificial aplicada a um problema empresarial realista.

O GitHub deverá apresentar não apenas o código, mas também a arquitetura, as decisões técnicas, os experimentos e os resultados obtidos.

## 4. Cenário de Demonstração

A plataforma será demonstrada utilizando uma empresa fictícia.

**ABC Indústria e Serviços Ltda**

Departamentos:

| Código | Departamento |

|---|---|

| RH | Recursos Humanos |

| FIN | Financeiro |

| COM | Compras |

| TI | Tecnologia da Informação |

| QUA | Qualidade |

| PRD | Produção |

| JUR | Jurídico |

### 4.1 Base documental

A base de conhecimento será composta por aproximadamente 30 documentos corporativos, predominantemente em formato PDF.

Os documentos representam políticas, manuais, procedimentos, instruções de trabalho e controles internos.

Os arquivos já foram preparados e estão armazenados localmente.

Localização atual:

`C:\\Users\\Elon\\Documents\\Projeto_RAG\\Documentação`

Essa pasta representa a fonte documental original utilizada nos experimentos do projeto.

Os documentos deverão ser organizados por departamento durante a preparação da ingestão.

Os arquivos originais deverão ser preservados.

## 5. Funcionalidades do MVP

### 5.1 Gestão documental

- Disponibilizar documentos para ingestão.

- Extrair texto dos arquivos PDF.

- Identificar páginas e metadados.

- Processar e dividir documentos em chunks.

- Gerar embeddings.

- Indexar conteúdo no banco vetorial.

### 5.2 Consulta inteligente

- Permitir perguntas em linguagem natural.

- Gerar embeddings da pergunta.

- Recuperar trechos relevantes.

- Construir contexto para a LLM.

- Gerar respostas fundamentadas nos documentos.

### 5.3 Evidências e rastreabilidade

Cada resposta deverá apresentar:

- Documento de origem.

- Página correspondente.

- Trecho utilizado como evidência.

- Identificação da versão documental, quando disponível.

O sistema deverá evitar apresentar informações como fatos quando não houver evidências suficientes na base documental.

### 5.4 Interface

- Interface de chat.

- Visualização das respostas.

- Exibição das fontes.

- Identificação dos documentos.

- Histórico de consultas.

- Dashboard básico de utilização.

## 6. Escopo e Limites

### Incluído no MVP

- Processamento de documentos PDF.

- Extração de texto.

- Chunking.

- Embeddings locais.

- ChromaDB.

- Busca vetorial.

- Integração com LLM externa.

- Chat corporativo.

- Respostas com fontes e evidências.

- Interface web.

- PostgreSQL.

- Execução local com Docker Compose.

### Fora do escopo inicial

- Arquitetura de microserviços.

- Kubernetes.

- Multiempresa.

- Integração com SharePoint.

- Integração com Google Drive.

- OCR avançado.

- Workflow de aprovação documental.

- Single Sign-On.

- Infraestrutura em nuvem para execução da aplicação.

- Alta disponibilidade e escalabilidade distribuída.

Essas funcionalidades poderão ser avaliadas em versões futuras.

## 7. Arquitetura Tecnológica

O projeto utilizará uma arquitetura de monólito modular, mantendo frontend, backend, processamento RAG e integrações organizados em componentes independentes.

### Frontend

- Next.js

- React

- TypeScript

- Tailwind CSS

- shadcn/ui

Responsabilidade: interface de interação com o usuário.

### Backend

- Python 3.12

- FastAPI

- SQLAlchemy

- Alembic

- Pydantic

Responsabilidade: API, regras de negócio, processamento documental e orquestração RAG.

### Persistência

**PostgreSQL**

Armazenará:

- Usuários.

- Departamentos.

- Metadados documentais.

- Histórico de consultas.

- Informações de controle e auditoria.

**ChromaDB**

Armazenará:

- Embeddings.

- Vetores.

- Identificadores dos chunks.

- Metadados associados aos conteúdos indexados.

### Processamento documental

- PyMuPDF: extração de conteúdo PDF.

- Python: processamento e preparação dos textos.

- Chunking: divisão do conteúdo em unidades pesquisáveis.

### Embeddings

Modelo inicial:

`intfloat/multilingual-e5-large`

O modelo será executado localmente, evitando dependência de serviços externos para geração dos embeddings.

### LLM

A geração de respostas será realizada por um serviço externo.

Provedor inicial:

Google Gemini.

A integração deverá permitir substituir futuramente o provedor de LLM sem modificar toda a aplicação.

### Infraestrutura

- Docker.

- Docker Compose.

- Git.

- GitHub.

- GitHub Actions.

Todos os componentes da aplicação deverão executar localmente, com exceção do serviço externo de LLM.

## 8. Princípios do Projeto

As seguintes diretrizes deverão orientar todas as decisões técnicas:

1\. **Simplicidade:** implementar somente o necessário para atingir os objetivos.

2\. **Aprendizado:** priorizar a compreensão dos conceitos, não apenas a entrega de código.

3\. **Open Source:** priorizar tecnologias e ferramentas de código aberto.

4\. **Execução local:** evitar dependências de infraestrutura em nuvem.

5\. **Modularidade:** manter responsabilidades separadas sem criar complexidade desnecessária.

6\. **Rastreabilidade:** respostas devem apresentar evidências documentais.

7\. **Documentação:** decisões e implementações relevantes devem ser registradas.

8\. **Evolução incremental:** implementar, testar e validar uma etapa antes de avançar.

9\. **Controle de escopo:** novas funcionalidades devem ser avaliadas antes de incorporadas.

10\. **Reprodutibilidade:** o ambiente deve poder ser reconstruído seguindo a documentação.

## 9. Evolução do Produto

O desenvolvimento será realizado incrementalmente.

| Etapa | Objetivo |

|---|---|

| Sprint 1 | Construção da base documental corporativa |

| Sprint 2 | Extração de texto, chunking e embeddings |

| Sprint 3 | Indexação e busca vetorial com ChromaDB |

| Sprint 4 | Chat, respostas e evidências |

| Sprint 5 | Frontend, dashboard e histórico |

### Evoluções futuras

Após a implementação do MVP, poderão ser avaliados:

- Busca híbrida (vetorial + BM25).

- Filtros por departamento.

- Controle de acesso.

- Versionamento documental.

- Reindexação de documentos.

- Avaliação de qualidade das respostas.

- Métricas de recuperação e relevância.

- Monitoramento de desempenho.

## 10. Critérios de Sucesso

O MVP será considerado funcional quando:

1\. Os documentos PDF puderem ser processados automaticamente.

2\. O conteúdo estiver indexado no ChromaDB.

3\. O usuário puder realizar perguntas em linguagem natural.

4\. A aplicação recuperar informações relevantes.

5\. A LLM gerar respostas utilizando o contexto recuperado.

6\. As respostas apresentarem documento, página e trecho de evidência.

7\. O sistema conseguir reconhecer quando não existem informações suficientes para responder.

8\. A aplicação funcionar localmente seguindo as instruções de instalação.

9\. O processo puder ser reproduzido a partir da documentação do GitHub.

## 11. Diretrizes de Desenvolvimento

O KnowledgeHub AI será construído com apoio de um agente de inteligência artificial, que deverá atuar como arquiteto, mentor técnico e instrutor.

O agente deverá:

- Consultar a documentação do projeto antes de propor alterações.

- Respeitar a arquitetura e as tecnologias definidas.

- Trabalhar uma etapa por vez.

- Explicar os conceitos antes da execução.

- Fornecer instruções práticas e comandos.

- Priorizar que o responsável pelo projeto execute e compreenda as atividades.

- Validar os resultados antes de avançar.

- Evitar implementações desnecessárias.

- Registrar decisões arquiteturais relevantes.

- Atualizar o progresso e a documentação.

O agente não deverá transformar o projeto em uma aplicação excessivamente complexa nem introduzir tecnologias sem justificativa.

## 12. Resultado Esperado

Ao final, o KnowledgeHub AI deverá ser uma aplicação funcional de inteligência documental corporativa, capaz de consultar políticas, procedimentos e documentos empresariais por meio de linguagem natural.

O resultado deverá demonstrar conhecimentos práticos de arquitetura de soluções, engenharia de dados, processamento documental, embeddings, bancos vetoriais, LLM e desenvolvimento de aplicações baseadas em RAG.

**O principal objetivo não é apenas ter uma aplicação funcionando, mas compreender como ela foi construída, por que cada tecnologia foi escolhida e como seus componentes trabalham juntos.**
