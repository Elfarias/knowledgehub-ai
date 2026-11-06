# Guia Prático: Fase 1 — Setup e Ambiente de Desenvolvimento

Este documento detalha o passo a passo executado para configurar a fundação técnica do **KnowledgeHub AI**, um sistema RAG corporativo modular desenvolvido em Python.

## 1\. Visão Geral da Fase

Antes de escrever qualquer lógica de Inteligência Artificial ou processamento de documentos, o objetivo desta fase foi estruturar a "casa":

* Criar uma arquitetura limpa e organizada (**Monólito Modular**).
* Isolar o ambiente de desenvolvimento Python para evitar conflitos de dependências.
* Garantir compatibilidade entre bibliotecas de IA e processamento matemático.

## 2\. Passo a Passo da Execução

### Passo 2.1: Estruturação do Monólito Modular

Para manter o código organizado por responsabilidades, criamos a árvore de diretórios oficial do projeto. No terminal do VS Code (PowerShell), executamos:

```powershell
mkdir backend\\app\\api, backend\\app\\core, backend\\app\\services, backend\\app\\models, backend\\app\\schemas, backend\\app\\vectorstore, backend\\app\\utils, data\\pdfs, scripts -Force
```

**O que cada pasta significa?**

* `backend/app/services/`: Onde ficarão as regras de negócio (leitura de PDFs, embeddings).
* `backend/app/api/`: Rotas da API web (FastAPI).
* `data/pdfs/`: Onde armazenamos os documentos corporativos locais da empresa fictícia *ABC Indústria*.

Em seguida, criamos os arquivos base de controle:

```powershell
New-Item -ItemType File -Path backend\\app\\\_\_init\_\_.py, backend\\app\\main.py, backend\\app\\core\\config.py, backend\\requirements.txt, .env.example, .gitignore -Force
```

### Passo 2.2: Definição das Dependências (`requirements.txt`)

Declaramos as ferramentas e bibliotecas que sustentam o MVP. No arquivo `backend/requirements.txt`, definimos:

```text
# Web Framework \& Servidor
fastapi==0.110.0
uvicorn\[standard]==0.28.0
pydantic==2.6.4
pydantic-settings==2.2.1

# Extração de texto de PDFs
pymupdf==1.24.1

# Matemática e Vetores (Compatibilidade essencial)
numpy==1.26.4

# Embeddings e Banco Vetorial (Execução Local)
sentence-transformers==2.5.1
torch==2.2.1 --extra-index-url https://download.pytorch.org/whl/cpu
chromadb==0.4.24

# Integração com LLM
google-genai>=1.0.0

# Ferramentas de Qualidade e Testes
pytest==8.1.1
httpx==0.27.0
ruff==0.3.3
```

### Passo 2.3: Isolamento com Ambiente Virtual (`venv`)

Para impedir que bibliotecas do projeto afetem o sistema operacional, criamos e ativamos uma "caixa isolada" do Python:

1. **Criar o ambiente virtual:**

```powershell
python -m venv venv
```

2. **Ativar o ambiente virtual (PowerShell):**

```powershell
.\\venv\\Scripts\\Activate.ps1
```

*(Caso encontre restrições de execução no Windows, liberamos temporariamente com: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*.

### Passo 2.4: Instalação e Resolução de Desafios Técnicos

Com o terminal exibindo o prefixo `(venv)`, atualizamos o gerenciador e instalamos os pacotes:

```powershell
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

> **Nota de Engenharia & Aprendizado (O Desafio do NumPy):**
> Durante a instalação de bibliotecas de Machine Learning (como PyTorch e Sentence-Transformers), identificamos que versões recentes do NumPy (2.x) removem funções legadas (`np.float_`), gerando erros de compilação em módulos antigos.
> * **Solução aplicada:** Fixamos explicitamente a versão do NumPy em `numpy==1.26.4` no `requirements.txt`, garantindo estabilidade matemática total para o pipeline de embeddings.

### Passo 2.5: Validação Final do Ambiente

Para certificar que tudo foi instalado perfeitamente, executamos um teste de carga rápida de bibliotecas:

```powershell
python -c "import fitz, sentence\_transformers, chromadb, fastapi; print('✅ Sucesso! Todas as bibliotecas da Fase 1 foram carregadas perfeitamente.')"
```

**Resultado esperado:**

```text
✅ Sucesso! Todas as bibliotecas da Fase 1 foram carregadas perfeitamente.
```
