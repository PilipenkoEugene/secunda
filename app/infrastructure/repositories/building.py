from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.abc_repositories import AbstractBuildingRepository
from app.domain.entities import Building
from app.infrastructure.repositories.base import BaseSqlAlchemyRepository


class BuildingRepository(BaseSqlAlchemyRepository[Building], AbstractBuildingRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Building)
