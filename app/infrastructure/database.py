from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.ECHO)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
