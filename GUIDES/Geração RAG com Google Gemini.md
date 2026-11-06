## Fase 4 — Geração RAG com Google Gemini (Sprint 4)

Nesta fase, integra-se o **Motor de Recuperação (Fase 3)** à **Geração de Linguagem (LLM)**. O objetivo é pegar os chunks e metadados retornados pelo ChromaDB, injetá-los em um prompt estruturado e enviá-los ao Google Gemini para produzir respostas precisas e fundamentadas.

### Conceitos Fundamentais desta Fase

1\. **Prompt Grounding (Embasamento):** A LLM é instruída a responder **apenas** com base nas informações contidas no contexto fornecido. Se a resposta não estiver nos documentos corporativos, ela deve declarar que não possui essa informação.

2\. **Rastreabilidade Integrada:** O prompt força a LLM a citar explicitamente o documento de origem e a página correspondente (ex.: `[TI-004 - Uso Aceitável de Recursos.pdf, Pág. 1]`) ao final das afirmações.

3\. **Isolamento de Responsabilidade:** O `GeminiService` fica responsável apenas por formatar as mensagens e interagir com a API da Google.

### Passo 1: Criar o Serviço do Gemini (`backend/app/services/gemini_service.py`)

Certifique-se de que a variável de ambiente `GEMINI_API_KEY` esteja configurada no seu arquivo `.env` ou no seu ambiente.

Crie o arquivo **`backend/app/services/gemini_service.py`**:

```python

"""

Serviço de Integração com o Google Gemini.

Responsável por formatar o prompt grounded (com contexto) e gerar respostas com citações.

"""

import os

from typing import List, Dict, Any

import google.generativeai as genai

class GeminiService:

&#x20;   def \_\_init\_\_(self, model\_name: str = "gemini-1.5-flash"):

&#x20;       api\_key = os.getenv("GEMINI\_API\_KEY")

&#x20;       if not api\_key:

&#x20;           raise ValueError("A variável de ambiente GEMINI\_API\_KEY não foi encontrada.")

&#x20;       

&#x20;       genai.configure(api\_key=api\_key)

&#x20;       self.model = genai.GenerativeModel(model\_name)

&#x20;   def \_build\_context\_prompt(self, query: str, context\_chunks: List\[Dict\[str, Any]]) -> str:

&#x20;       """

&#x20;       Monta o prompt final injetando os trechos recuperados do ChromaDB.

&#x20;       """

&#x20;       formatted\_context = ""

&#x20;       for idx, chunk in enumerate(context\_chunks, start=1):

&#x20;           source = chunk\["metadata"].get("source", "Desconhecido")

&#x20;           page = chunk\["metadata"].get("page", "N/A")

&#x20;           text = chunk\["text"]

&#x20;           formatted\_context += f"--- DOCUMENTO \[{idx}] ---\\nFonte: {source} (Página {page})\\nConteúdo:\\n{text}\\n\\n"

&#x20;       prompt = f"""Você é o KnowledgeHub AI, um assistente especialista em responder dúvidas corporativas com base estrita nos documentos fornecidos.

DIRETRIZES OBRIGATÓRIAS:

1\. Responda à pergunta do usuário utilizando APENAS as informações presentes no CONTEXTO abaixo.

2\. Para cada afirmação principal, cite a fonte exata e a página indicadas no documento (exemplo: \[Nome\_do\_Arquivo.pdf, Pág. X]).

3\. Se o contexto não contiver informações suficientes para responder à pergunta, declare claramente que não possui essa informação nos documentos internos.

4\. Mantenha um tom profissional, direto e conciso.

CONTEXTO RECUPERADO:

{formatted\_context}

PERGUNTA DO USUÁRIO:

{query}

RESPOSTA FUNDAMENTADA:"""

&#x20;       return prompt

&#x20;   def generate\_answer(self, query: str, context\_chunks: List\[Dict\[str, Any]]) -> str:

&#x20;       """

&#x20;       Gera a resposta fundamentada enviando o prompt estruturado para o Gemini.

&#x20;       """

&#x20;       prompt = self.\_build\_context\_prompt(query, context\_chunks)

&#x20;       response = self.model.generate\_content(prompt)

&#x20;       return response.text

```

### Passo 2: Criar o Pipeline RAG Completo (`scripts/test_rag.py`)

A integração dos componentes é consolidada no script a seguir: **Consulta no ChromaDB + Geração com Gemini**.

Crie o arquivo **`scripts/test_rag.py`**:

```python

"""

Script de Validação do Pipeline RAG Completo (Fase 4).

Realiza a busca semântica dos trechos mais relevantes e gera a resposta fundamentada via Gemini.

"""

from pathlib import Path

import sys

\# Adiciona a pasta backend ao path para importações dos módulos

sys.path.append(str(Path(\_\_file\_\_).resolve().parent.parent / "backend"))

from app.vectorstore.chroma\_manager import ChromaManager

from app.services.gemini\_service import GeminiService

def main():

&#x20;   # Pergunta para testar a pipeline RAG

&#x20;   query = "Quais são as regras para o uso de mídias removíveis e trabalho remoto?"

&#x20;   print("🔄 Inicializando o banco vetorial ChromaDB...")

&#x20;   chroma\_mgr = ChromaManager()

&#x20;   print("🔄 Conectando ao serviço do Google Gemini...")

&#x20;   gemini\_svc = GeminiService()

&#x20;   print(f"\\n🔍 Buscando contexto relevante para a pergunta:\\n   ➡️ \\"{query}\\"")

&#x20;   results = chroma\_mgr.query\_similarity(query, n\_results=3)

&#x20;   documents = results.get("documents", \[\[]])\[0]

&#x20;   metadatas = results.get("metadatas", \[\[]])\[0]

&#x20;   # Estrutura os trechos recuperados em um formato limpo para o GeminiService

&#x20;   context\_chunks = \[]

&#x20;   for doc, meta in zip(documents, metadatas):

&#x20;       context\_chunks.append({

&#x20;           "text": doc,

&#x20;           "metadata": meta

&#x20;       })

&#x20;   print(f"✅ {len(context\_chunks)} chunks recuperados com sucesso.")

&#x20;   print("\\n🤖 Enviando contexto e pergunta ao Google Gemini...\\n")

&#x20;   print("=" \* 70)

&#x20;   # Geração da resposta

&#x20;   answer = gemini\_svc.generate\_answer(query, context\_chunks)

&#x20;   print("💬 RESPOSTA DO KNOWLEDGEHUB AI:\\n")

&#x20;   print(answer)

&#x20;   print("=" \* 70)

if \_\_name\_\_ == "\_\_main\_\_":

&#x20;   main()

```

### Passo 3: Execução no Terminal

Certifique-se de que a variável `GEMINI_API_KEY` esteja visível no terminal antes de executar o script:

```powershell

$env:GEMINI\_API\_KEY="sua\_chave\_aqui"

python scripts/test\_rag.py

```

Após a criação dos arquivos de serviço e teste, a validação é executada no terminal.
