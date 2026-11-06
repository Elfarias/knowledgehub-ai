from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import os

# Exemplo de URL de conexão assíncrona para PostgreSQL (ajuste conforme as suas variáveis de ambiente se necessário)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/knowledgehub"
)

# Criar motor assíncrono do SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Fábrica de sessões assíncronas
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base declarativa para os modelos
Base = declarative_base()

async def get_db() -> AsyncSession:
    """
    Dependência assíncrona do FastAPI para obter a sessão da base de dados.
    Garante que a sessão é fechada corretamente após o uso.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()