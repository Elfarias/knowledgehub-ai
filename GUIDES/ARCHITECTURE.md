\# ARCHITECTURE.md



\# KnowledgeHub AI — Arquitetura da Solução



\## 1. Visão Geral



O KnowledgeHub AI utiliza uma arquitetura de \*\*monólito modular\*\*, organizada em componentes com responsabilidades bem definidas.



A aplicação será executada localmente, utilizando Docker Compose para inicialização e gerenciamento dos serviços.



A única dependência externa obrigatória será o provedor de LLM, inicialmente Google Gemini.



A arquitetura foi projetada considerando três objetivos:



\- Simplicidade de implementação e manutenção.

\- Aprendizado dos conceitos envolvidos em aplicações RAG.

\- Possibilidade de evolução sem necessidade de reconstruir toda a aplicação.



\### 1.1 Estilo arquitetural



\*\*Monólito modular (Modular Monolith).\*\*



O backend será uma única aplicação FastAPI, internamente organizada em módulos.



Não serão utilizados microserviços no MVP.



Essa abordagem permite separar responsabilidades sem adicionar complexidade de comunicação, infraestrutura e implantação.



\---



\## 2. Diagrama da Arquitetura



```mermaid

flowchart TB

&#x20;   USER\[Usuário]



&#x20;   subgraph LOCAL\["Ambiente Local - Docker Compose"]

&#x20;       FRONT\[Frontend<br/>Next.js]



&#x20;       API\[Backend<br/>FastAPI]



&#x20;       subgraph MODULES\["Módulos do Backend"]

&#x20;           DOC\[Gestão Documental]

&#x20;           ING\[Ingestão e Processamento]

&#x20;           RAG\[Motor RAG]

&#x20;           CHAT\[Chat e Histórico]

&#x20;       end



&#x20;       PG\[(PostgreSQL)]

&#x20;       CH\[(ChromaDB)]

&#x20;       FS\[(Filesystem<br/>Documentos)]



&#x20;       EMB\[Modelo de Embeddings<br/>Multilingual E5]

&#x20;   end



&#x20;   LLM\[Google Gemini<br/>LLM Externa]



&#x20;   USER --> FRONT

&#x20;   FRONT <-->|REST API| API



&#x20;   API --> MODULES



&#x20;   DOC --> PG

&#x20;   DOC --> FS



&#x20;   ING --> FS

&#x20;   ING --> EMB

&#x20;   ING --> CH

&#x20;   ING --> PG



&#x20;   RAG --> EMB

&#x20;   RAG --> CH

&#x20;   RAG --> LLM



&#x20;   CHAT --> PG

&#x20;   CHAT --> RAG



&#x20;   LLM --> RAG

&#x20;   RAG --> CHAT

&#x20;   CHAT --> API

```



\---



\## 3. Componentes da Arquitetura



\### 3.1 Frontend — Next.js



Responsável pela interface de interação com o usuário.



Principais responsabilidades:



\- Apresentar a interface de chat.

\- Permitir envio de perguntas.

\- Exibir respostas da IA.

\- Apresentar documentos utilizados como fontes.

\- Exibir páginas e trechos de evidência.

\- Disponibilizar histórico de consultas.

\- Apresentar informações básicas da base documental.



O frontend não deverá acessar diretamente os bancos de dados ou o provedor de LLM.



Toda comunicação será realizada por meio da API do backend.



\### 3.2 Backend — FastAPI



Responsável pela lógica de negócio e integração dos componentes.



O backend será o ponto central da aplicação.



Principais responsabilidades:



\- Receber requisições do frontend.

\- Gerenciar documentos e metadados.

\- Executar o processamento documental.

\- Coordenar o pipeline RAG.

\- Consultar o banco vetorial.

\- Integrar com o provedor de LLM.

\- Registrar consultas e respostas.

\- Retornar respostas e evidências ao frontend.



\### 3.3 Módulo de Gestão Documental



Responsável pelo gerenciamento dos documentos corporativos.



Funções:



\- Identificar documentos disponíveis.

\- Registrar metadados.

\- Identificar departamento.

\- Controlar informações de versão.

\- Disponibilizar documentos para processamento.

\- Recuperar informações dos documentos.



Os arquivos originais serão preservados no armazenamento local.



\### 3.4 Módulo de Ingestão e Processamento



Responsável por transformar documentos em informações que possam ser utilizadas pelo mecanismo RAG.



Fluxo:



1\. Receber ou identificar o documento.

2\. Extrair o texto do PDF.

3\. Preservar a identificação das páginas.

4\. Dividir o conteúdo em chunks.

5\. Associar metadados aos chunks.

6\. Gerar embeddings.

7\. Armazenar vetores e metadados no ChromaDB.



O processamento utilizará o modelo de embeddings executado localmente.



\### 3.5 Motor RAG



Responsável por recuperar informações relevantes e construir o contexto utilizado pela LLM.



Funções:



\- Receber a pergunta do usuário.

\- Gerar embedding da pergunta.

\- Consultar o ChromaDB.

\- Recuperar os chunks mais relevantes.

\- Preparar o contexto documental.

\- Encaminhar contexto e pergunta para a LLM.

\- Processar a resposta.

\- Associar as evidências utilizadas.



O motor RAG deverá utilizar somente informações recuperadas da base documental como fundamento das respostas sobre políticas e procedimentos da empresa.



Quando não houver evidências suficientes, deverá informar que não encontrou informações suficientes para responder.



\### 3.6 Módulo de Chat e Histórico



Responsável por gerenciar as interações entre usuários e a plataforma.



Funções:



\- Receber perguntas.

\- Acionar o motor RAG.

\- Registrar perguntas e respostas.

\- Armazenar data e hora das consultas.

\- Recuperar histórico.

\- Associar as respostas às respectivas fontes.



\---



\## 4. Camada de Persistência



A arquitetura utilizará dois bancos de dados com responsabilidades distintas, além do armazenamento local dos documentos originais.



\### 4.1 PostgreSQL — Banco Relacional



Responsável pelos dados estruturados da aplicação.



Armazenará:



| Informação | Descrição |

|---|---|

| Usuários | Identificação dos usuários |

| Departamentos | Departamentos da empresa |

| Documentos | Metadados documentais |

| Versões | Informações de versões dos documentos |

| Consultas | Perguntas realizadas |

| Respostas | Respostas geradas |

| Histórico | Registro das interações |



O PostgreSQL será a fonte principal de informações cadastrais e administrativas.



\### 4.2 ChromaDB — Banco Vetorial



Responsável pela recuperação semântica dos conteúdos documentais.



Armazenará:



\- Embeddings dos chunks.

\- Identificadores dos chunks.

\- Conteúdo textual associado.

\- Metadados documentais.

\- Identificação do documento.

\- Identificação da página.

\- Departamento.

\- Identificação da versão.



O ChromaDB será utilizado para encontrar conteúdos semanticamente relacionados às perguntas dos usuários.



\### 4.3 Filesystem — Armazenamento de Arquivos



Os documentos originais serão armazenados localmente.



Responsabilidades:



\- Preservar os PDFs originais.

\- Disponibilizar arquivos para processamento.

\- Permitir recuperação dos documentos.

\- Manter os arquivos independentes dos bancos de dados.



Os documentos originais não serão armazenados diretamente no ChromaDB.



\---



\## 5. Fluxo de Ingestão Documental



A ingestão é o processo responsável por transformar documentos corporativos em uma base pesquisável.



```mermaid

flowchart TD

&#x20;   A\[Documento PDF] --> B\[Leitura do arquivo]

&#x20;   B --> C\[Extração de texto com PyMuPDF]

&#x20;   C --> D\[Identificação das páginas]

&#x20;   D --> E\[Chunking]

&#x20;   E --> F\[Associação de metadados]

&#x20;   F --> G\[Modelo de Embeddings]

&#x20;   G --> H\[ChromaDB]

&#x20;   F --> I\[PostgreSQL]

&#x20;   A --> J\[Filesystem]

```



\### Regras da ingestão



Cada documento deverá manter sua identificação original.



Cada chunk deverá possuir informações suficientes para identificar sua origem.



Metadados mínimos:



\- ID do documento.

\- Título do documento.

\- Departamento.

\- Número da página.

\- Identificador do chunk.

\- Versão documental, quando disponível.



O processamento deverá permitir identificar quais conteúdos foram extraídos de cada documento.



\---



\## 6. Fluxo de Consulta RAG



O fluxo de consulta será responsável por responder às perguntas dos usuários utilizando a base documental.



```mermaid

flowchart TD

&#x20;   A\[Pergunta do usuário] --> B\[FastAPI]

&#x20;   B --> C\[Gerar embedding da pergunta]

&#x20;   C --> D\[Consulta ao ChromaDB]

&#x20;   D --> E\[Recuperar Top K chunks]

&#x20;   E --> F\[Preparar contexto]

&#x20;   F --> G\[Enviar contexto e pergunta]

&#x20;   G --> H\[Google Gemini]

&#x20;   H --> I\[Resposta gerada]

&#x20;   I --> J\[Associar evidências]

&#x20;   J --> K\[Registrar consulta no PostgreSQL]

&#x20;   K --> L\[Retornar resposta e fontes]

```



\### Regras da consulta



1\. A pergunta deverá ser convertida em embedding utilizando o mesmo modelo empregado na ingestão.

2\. O ChromaDB deverá recuperar os conteúdos mais relevantes.

3\. Os conteúdos recuperados serão utilizados para construir o contexto.

4\. A pergunta e o contexto serão enviados à LLM.

5\. A resposta deverá apresentar as fontes documentais correspondentes.

6\. As consultas e respostas deverão ser registradas no PostgreSQL.



A aplicação deverá preservar a relação entre cada evidência apresentada e seu documento de origem.



A LLM não deverá inventar referências, páginas ou trechos documentais.



\---



\## 7. Integração entre Componentes



A comunicação seguirá um modelo simples.



| Origem | Destino | Comunicação |

|---|---|---|

| Usuário | Frontend | Navegador |

| Frontend | FastAPI | HTTP/REST |

| FastAPI | PostgreSQL | SQLAlchemy |

| FastAPI | ChromaDB | API/Cliente Python |

| FastAPI | Filesystem | Acesso local |

| FastAPI | Embeddings | Execução local |

| FastAPI | Gemini | API HTTPS |



O frontend não terá acesso direto aos bancos de dados.



A comunicação com serviços externos ficará concentrada no backend.



\---



\## 8. Ambiente de Execução



Toda a infraestrutura da aplicação será executada localmente.



O Docker Compose será utilizado para inicializar e organizar os serviços.



| Componente | Execução |

|---|---|

| Frontend | Container Docker |

| Backend | Container Docker |

| PostgreSQL | Container Docker |

| ChromaDB | Container Docker |

| Embeddings | Execução local pelo backend |

| Documentos | Volume local persistente |

| Gemini | Serviço externo |



\### Persistência



Os dados deverão permanecer disponíveis mesmo após a interrupção dos containers.



Serão utilizados volumes persistentes para:



\- PostgreSQL.

\- ChromaDB.

\- Documentos originais.



Os arquivos de configuração deverão utilizar variáveis de ambiente.



Chaves de API e credenciais não deverão ser armazenadas no GitHub.



\---



\## 9. Segurança e Controle de Acesso



No MVP, a segurança deverá considerar:



\- Proteção das credenciais da LLM.

\- Separação entre frontend e backend.

\- Validação dos arquivos enviados.

\- Controle dos tipos de arquivo aceitos.

\- Validação das entradas da API.

\- Proteção das configurações e variáveis de ambiente.

\- Não exposição direta dos bancos de dados ao frontend.



Os departamentos deverão ser registrados como metadados dos documentos.



O controle efetivo de acesso por usuário e departamento será implementado em uma etapa posterior, antes de qualquer utilização com informações corporativas reais.



A identificação de departamento nos metadados não deverá ser confundida com autorização de acesso.



\---



\## 10. Organização Arquitetural do Backend



O backend deverá ser organizado em módulos, mantendo responsabilidades separadas.



Estrutura conceitual:



```text

backend/

│

└── app/

&#x20;   │

&#x20;   ├── api/

&#x20;   │

&#x20;   ├── core/

&#x20;   │

&#x20;   ├── modules/

&#x20;   │   ├── documents/

&#x20;   │   ├── ingestion/

&#x20;   │   ├── rag/

&#x20;   │   └── chat/

&#x20;   │

&#x20;   ├── infrastructure/

&#x20;   │   ├── database/

&#x20;   │   ├── vector\_store/

&#x20;   │   ├── embeddings/

&#x20;   │   ├── llm/

&#x20;   │   └── storage/

&#x20;   │

&#x20;   └── main.py

```



Os módulos deverão manter responsabilidades claras, mas não serão aplicações independentes.



\---



\## 11. Decisões e Restrições Arquiteturais



As seguintes decisões deverão ser respeitadas durante o desenvolvimento:



| Decisão | Definição |

|---|---|

| Estilo arquitetural | Monólito modular |

| Comunicação frontend/backend | REST API |

| Backend | FastAPI |

| Frontend | Next.js |

| Banco relacional | PostgreSQL |

| Banco vetorial | ChromaDB |

| Embeddings | Multilingual E5 |

| LLM | Google Gemini inicialmente |

| Armazenamento documental | Filesystem local |

| Infraestrutura | Docker Compose |

| Ambiente | Máquina local |

| Processamento documental | PDF |

| Licenciamento | Apache 2.0 |



Não deverão ser introduzidos microserviços, Kubernetes, Kafka, Redis ou outros componentes de infraestrutura sem uma necessidade técnica comprovada e aprovação prévia.



\---



\## 12. Evolução da Arquitetura



A arquitetura deverá permitir evolução incremental.



| Evolução | Possibilidade |

|---|---|

| Busca híbrida | Combinar busca vetorial e BM25 |

| Filtros | Restringir consultas por departamento |

| Versionamento | Controlar versões documentais |

| Avaliação RAG | Medir qualidade da recuperação e respostas |

| Observabilidade | Monitorar consultas, prompts e desempenho |

| Segurança | Implementar autenticação e autorização |

| LLM | Substituir o provedor sem reescrever o motor RAG |



Essas evoluções não fazem parte da implementação inicial, salvo quando necessárias para preparar corretamente a arquitetura.



\---



\## 13. Princípios de Manutenção



Toda alteração arquitetural relevante deverá respeitar os seguintes princípios:



1\. Manter a arquitetura simples.

2\. Evitar duplicação de responsabilidades.

3\. Preservar a separação entre dados relacionais e vetoriais.

4\. Manter os documentos originais independentes da indexação.

5\. Preservar a rastreabilidade dos chunks até suas fontes.

6\. Evitar dependência excessiva de um provedor específico de LLM.

7\. Documentar mudanças que afetem a arquitetura.

8\. Priorizar soluções que possam ser executadas localmente.



\## 14. Resultado Esperado



A arquitetura deverá permitir que o KnowledgeHub AI processe documentos corporativos, construa uma base vetorial, recupere informações relevantes e produza respostas fundamentadas em evidências.



O sistema deverá ser simples de instalar, executar, compreender e evoluir.



\*\*A arquitetura não deve ser maior que o problema que pretende resolver.\*\*

