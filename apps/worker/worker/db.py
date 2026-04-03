from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from worker.config import settings

engine = create_async_engine(settings.database_url, future=True, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

