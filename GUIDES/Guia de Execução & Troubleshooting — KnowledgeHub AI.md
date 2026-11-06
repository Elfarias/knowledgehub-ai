# Guia de Execução & Troubleshooting — KnowledgeHub AI

Este guia orienta como inicializar todos os serviços do sistema (Banco de Dados PostgreSQL, API Backend FastAPI e Interface Web Streamlit), além de fornecer soluções para os problemas técnicos mais frequentes.

---

## Pré-requisitos
Antes de iniciar, certifique-se de que o seu ambiente atende aos requisitos básicos:
1. **Python 3.11 ou 3.12** instalado.
2. **Docker Desktop** instalado e em execução (para o PostgreSQL).
3. Ambiente virtual Python (`venv`) ativado no terminal.

---

## 1. Passo a Passo para Subir as Aplicações

Para garantir o funcionamento completo do fluxo RAG, a inicialização deve seguir uma ordem específica: **Banco de Dados Backend (API) Frontend (Streamlit)**.

### Passo 1: Subir o Container do PostgreSQL
Na raiz do projeto (`knowledgehub-ai`), abra o terminal e execute:
```powershell
docker compose up -d
```
* **O que faz:** Inicializa o PostgreSQL na porta `5432` em segundo plano.
* **Validação:** Execute `docker ps` para confirmar que o container do Postgres está ativo (`Up`).

---

### Passo 2: Inicializar o Backend (API FastAPI)
Em um novo terminal, certifique-se de ativar o ambiente virtual (`venv`) e **navegar para a pasta `backend`**:

```powershell
# Ativar o venv (PowerShell Windows)
.\venv\Scripts\Activate.ps1

# Entrar na pasta do backend (Obrigatório para evitar erros de importação)
cd backend

# Subir a API FastAPI
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **O que faz:** Sobe a API FastAPI na porta `8000` com recarregamento automático (`--reload`).
* **Validação:** Acesse no navegador `http://127.0.0.1:8000/docs` para ver a documentação interativa da API (Swagger).

---

### Passo 3: Inicializar a Interface Web (Frontend Streamlit)
Abra um **segundo terminal**, ative o ambiente virtual e execute o Streamlit a partir da raiz do projeto:

```powershell
# Ativar o venv
.\venv\Scripts\Activate.ps1

# Subir o painel web Streamlit
streamlit run frontend/app.py
```
* **O que faz:** Inicializa o painel interativo web em `http://localhost:8501`.
* **Validação:** O navegador abrirá automaticamente exibindo o indicador **` API Conectada`** na barra lateral.

---

## 2. Processamento e Ingestão de Documentos (Opcional/Manutenção)

Se adicionou novos arquivos PDF na pasta `backend/data/docs/` e deseja indexá-los no banco vetorial ChromaDB:

1. Com o `venv` ativado, navegue para a pasta `backend`:
```powershell
   cd backend
```
2. Execute o script de ingestão:
```powershell
   python ingest.py
```
* **O que faz:** Extrai o texto dos PDFs, divide em chunks, calcula os embeddings com o modelo `multilingual-e5-large` e armazena os vetores em `backend/data/chroma_db`.

---

## ️ 3. Troubleshooting & Resolução de Erros Comuns

### Erro 1: `ModuleNotFoundError: No module named 'app'` ao subir o Uvicorn
* **Causa:** O comando `uvicorn` foi executado a partir da raiz do projeto em vez de entrar na pasta `backend`.
* **Solução:** Navegue para a pasta `backend` antes de rodar o servidor:
```powershell
  cd backend
  uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

### Erro 2: `CouldNotAutoLoadModule` / `powershell\nuvicorn`
* **Causa:** Quebra de linha ou caractere estranho colado junto com o comando PowerShell.
* **Solução:** Execute o comando em uma linha limpa sem o prefixo `powershell\n`:
```powershell
  uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

### Erro 3: ` API Offline` ou `Não foi possível conectar à API` no Streamlit
* **Causa:** A API FastAPI no Backend não está rodando na porta 8000 ou caiu devido a algum erro.
* **Solução:**
 1. Verifique o terminal onde o `uvicorn` está rodando para checar se há erros no código Python.
 2. Garanta que o servidor backend está ouvindo em `http://127.0.0.1:8000`.
 3. Verifique se o container PostgreSQL está rodando (`docker ps`).

---

### Erro 4: Conexão recusada ao banco de dados PostgreSQL
* **Causa:** O container Docker do PostgreSQL não foi inicializado ou o arquivo `.env` possui credenciais incorretas.
* **Solução:**
 1. Verifique se o Docker Desktop está aberto e rodando.
 2. Reinicie o banco com:
```powershell
     docker compose restart
```
 3. Verifique se a variável `DATABASE_URL` no `.env` está configurada corretamente com a senha definida no `docker-compose.yml`.

---

### Erro 5: `chromadb.telemetry` ou falha ao carregar o ChromaDB
* **Causa:** Múltiplas instâncias tentando acessar o mesmo diretório de banco SQLite local do ChromaDB ou erro de permissão.
* **Solução:**
 1. Certifique-se de que não há múltiplos scripts de ingestão rodando simultaneamente.
 2. Verifique se a pasta `backend/data/chroma_db` possui permissões de escrita e leitura.

---

## Resumo Rápido dos Terminais

Para manter tudo rodando de forma organizada no dia a dia, utilize **2 terminais ativos**:

| Terminal | Diretório de Execução | Comando de Inicialização | Função |
| :--- | :--- | :--- | :--- |
| **Terminal 1** | `knowledgehub-ai/backend` | `uvicorn app.main:app --reload` | Servidor API REST (FastAPI) |
| **Terminal 2** | `knowledgehub-ai/` | `streamlit run frontend/app.py` | Interface Web (Streamlit) |
