import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.chat.models import QueryLogModel

logger = logging.getLogger(__name__)

async def create_query_log(
    db: AsyncSession, 
    user_query: str, 
    llm_response: str, 
    sources: list = None
) -> None:
    """
    Regista a consulta RAG na base de dados de forma segura.
    Se ocorrer um erro, regista-o nos logs do servidor mas não interrompe o fluxo principal.
    """
    try:
        db_log = QueryLogModel(
            query=user_query,
            answer=llm_response,  # Corrigido de 'response' para 'answer' (nome real da coluna)
            sources=sources       # Adicionado o campo JSON de fontes
        )
        db.add(db_log)
        await db.commit()
    except Exception as e:
        # Garante o rollback da transação em caso de erro para não corromper a sessão
        await db.rollback()
        logger.error(f"Falha ao gravar o log de auditoria da query RAG: {e}")