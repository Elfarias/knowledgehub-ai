"""
Serviço de Integração com LLM via OpenRouter.
Responsável por formatar o prompt grounded (com contexto) e gerar respostas com citações.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Carrega as variáveis de ambiente do arquivo .env da raiz
load_dotenv()


class GeminiService:
    def __init__(self, model_name: str = "nvidia/nemotron-3.5-super-vl:free", api_key: str = None):
        resolved_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not resolved_key:
            raise ValueError(
                "A variável OPENROUTER_API_KEY não foi encontrada no arquivo .env."
            )
        
        # Configuração oficial para o OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=resolved_key.strip(),
        )
        self.model_name = model_name

    def _build_context_prompt(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        formatted_context = ""
        for idx, chunk in enumerate(context_chunks, start=1):
            source = chunk["metadata"].get("source", "Desconhecido")
            page = chunk["metadata"].get("page", "N/A")
            text = chunk["text"]
            formatted_context += f"--- DOCUMENTO [{idx}] ---\nFonte: {source} (Página {page})\nConteúdo:\n{text}\n\n"

        prompt = f"""Você é o KnowledgeHub AI, um assistente especialista em responder dúvidas corporativas com base estrita nos documentos fornecidos.

DIRETRIZES OBRIGATÓRIAS:
1. Responda à pergunta do usuário utilizando APENAS as informações presentes no CONTEXTO abaixo.
2. Para cada afirmação principal, cite a fonte exata e a página indicadas no documento (exemplo: [Nome_do_Arquivo.pdf, Pág. X]).
3. Se o contexto não contiver informações suficientes para responder à pergunta, declare claramente que não possui essa informação nos documentos internos.
4. Mantenha um tom profissional, direto e conciso.

CONTEXTO RECUPERADO:
{formatted_context}

PERGUNTA DO USUÁRIO:
{query}

RESPOSTA FUNDAMENTADA:"""
        return prompt

    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        prompt = self._build_context_prompt(query, context_chunks)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            extra_headers={
                "HTTP-Referer": "https://github.com/knowledgehub-ai",
                "X-Title": "KnowledgeHub AI",
            }
        )
        return response.choices[0].message.content