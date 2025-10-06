from typing import List, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.abc_repositories import AbstractRepository

T = TypeVar('T')


class BaseSqlAlchemyRepository(AbstractRepository[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_all(self) -> List[T]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def get_by_id(self, entity_id: int) -> T | None:
        result = await self.session.execute(select(self.model).filter(self.model.id == entity_id))
        return result.scalars().first()

    async def create(self, **kwargs) -> T:
        entity = self.model(**kwargs)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T, **kwargs) -> T:
        for key, value in kwargs.items():
            if value is not None:
                setattr(entity, key, value)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.commit()
