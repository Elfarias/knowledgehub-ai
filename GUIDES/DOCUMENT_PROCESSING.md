# Guia de Processamento de Documentos e Capacidades de Ingestão — KnowledgeHub AI

## 1. Visão Geral da Arquitetura Atual de Ingestão

O **KnowledgeHub AI** foi projetado sob uma arquitetura de monólito modular simples e expansível. No estado atual (MVP), o pipeline RAG utiliza um fluxo de extração, limpeza, fatiamento (*chunking*), geração de embeddings e indexação vetorial no **ChromaDB**.

## 2. Capacidades Atuais vs. Expansíveis

### 2.1 Formato Suportado Nativamente no MVP (Nativo)

| Formato | Extensão | Biblioteca Utilizada | Como Funciona |
| :--- | :---: | :---: | :--- |
| **PDFs Textuais** | `.pdf` | `PyMuPDF` (`fitz`) / `pypdf` | Lê páginas nativas de texto, preserva a numeração de páginas como metadados e fatias em chunks pesquisáveis. |

> **Nota:** PDFs que consistem exclusivamente em digitalizações (imagens digitalizadas sem camada de texto) necessitam de uma etapa de OCR para extração de conteúdo.

### 2.2 Formatos Prontos para Expansão (Requer Adição de Extrator)

A arquitetura do KnowledgeHub AI é totalmente capaz de ingerir praticamente **qualquer tipo de arquivo corporativo**, desde que o conteúdo seja convertido em **texto estruturado** antes de ser enviado para o modelo de embeddings (`multilingual-e5-large`).

Abaixo estão os tipos de documentos adicionais e as bibliotecas necessárias para integrar o suporte:

| Categoria | Extensões | Biblioteca Python | Estratégia de Processamento & Metadados |
| :--- | :---: | :--- | :--- |
| **Apresentações** | `.pptx` | `python-pptx` | Extrai texto de caixas e notas de orador. Mapeia **Slide** como número de página. |
| **Documentos Word** | `.docx` | `python-docx` | Extrai parágrafos, títulos e tabelas mantendo a ordem do texto. |
| **Planilhas** | `.xlsx`, `.csv` | `pandas`, `openpyxl` | Converte tabelas em representações textuais (Markdown ou JSON por linha) para preservar o contexto relacional. |
| **Imagens (OCR)** | `.png`, `.jpg`, `.jpeg` | `pytesseract` + `Pillow` | Executa Reconhecimento Óptico de Caracteres (OCR) em português/inglês para extrair texto visual. |
| **Texto/Código** | `.txt`, `.md`, `.json` | Python nativo (`open`) | Lê diretamente o conteúdo e faz chunking por parágrafos ou seções de código. |
| **E-mails** | `.eml`, `.msg` | `extract_msg`, `email` | Extrai cabeçalhos (remetente, assunto, data) e o corpo do e-mail como texto. |
| **Áudio/Vídeo** | `.mp3`, `.wav`, `.mp4` | `openai-whisper` (local) | Transcreve a fala em texto legível para posteriormente ser indexada no banco vetorial. |

## 3. Procedimento para Ingestão dos PDFs Atuais

Caso você tenha colocado novos ficheiros PDF na pasta de documentos corporativos (`backend/data/docs/`), siga o procedimento simples abaixo para reprocessar a base vetorial.

### Passo 1: Garantir os ficheiros no local correto
Certifique-se de que todos os arquivos `.pdf` estão guardados dentro de:
```text
backend/data/docs/
```

### Passo 2: Executar o script de ingestão
No seu terminal com o ambiente virtual (`venv`) ativado, navegue para a pasta `backend` e execute o script:
```powershell
cd backend
python ingest.py
```

O script irá automaticamente:
1. Identificar todos os ficheiros `.pdf` novos.
2. Extrair o texto página por página.
3. Gerar os vetores de embedding usando o modelo local `intfloat/multilingual-e5-large`.
4. Armazenar/atualizar no **ChromaDB** mantendo os caminhos absolutos corretos.

## 4. Guia Passo a Passo para Adicionar Novos Formatos no `ingest.py`

Para permitir que o KnowledgeHub AI processe PPTs, Excels, Word ou Imagens, siga esta estrutura de expansão no script `backend/ingest.py`:

### Exemplo de Estrutura Modular de Ingestão Multiformato:

```python
import os
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from pptx import Presentation # pip install python-pptx
import pandas as pd # pip install pandas openpyxl
from docx import Document # pip install python-docx

def extract_pdf(file_path):
reader = PdfReader(file_path)
chunks = []
for page_num, page in enumerate(reader.pages, 1):
text = page.extract_text() or ""
if text.strip():
chunks.append({"page": page_num, "text": " ".join(text.split())})
return chunks

def extract_pptx(file_path):
prs = Presentation(file_path)
chunks = []
for slide_num, slide in enumerate(prs.slides, 1):
slide_text = []
for shape in slide.shapes:
if shape.has_text_frame:
slide_text.append(shape.text_frame.text)
text = " ".join(slide_text)
if text.strip():
chunks.append({"page": slide_num, "text": " ".join(text.split())})
return chunks

def extract_docx(file_path):
doc = Document(file_path)
full_text = [p.text for p in doc.paragraphs if p.text.strip()]
text = " ".join(full_text)
return [{"page": 1, "text": text}]

def extract_excel(file_path):
df_dict = pd.read_excel(file_path, sheet_name=None)
chunks = []
for sheet_name, df in df_dict.items():
# Converte a planilha em formato tabular inteligível para LLMs
text = df.to_string(index=False)
if text.strip():
chunks.append({"page": f"Aba: {sheet_name}", "text": text})
return chunks

# Mapeamento de extensões para manipuladores
EXTRACTORS = {
".pdf": extract_pdf,
".pptx": extract_pptx,
".docx": extract_docx,
".xlsx": extract_excel,
}
```

## 5. Resumo das Recomendações

1. **Simplicidade:** Para o MVP, a ingestão de PDFs cobre mais de 90% dos casos de uso de políticas corporativas.
2. **Qualidade dos Dados:** Ao adicionar tabelas (Excel) ou apresentações (PowerPoint), priorize estruturar o texto limpo com o mínimo de ruído visual para garantir alta acurácia nos embeddings semânticos.
3. **Escalabilidade:** A inclusão de novos formatos requer apenas adicionar uma função extratora dedicada sem necessidade de alterar a arquitetura do ChromaDB ou da API FastAPI.
