from typing import List

from sqlalchemy import select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domain.abc_repositories import AbstractActivityRepository
from app.domain.entities import Activity
from app.infrastructure.repositories.base import BaseSqlAlchemyRepository


class ActivityRepository(BaseSqlAlchemyRepository[Activity], AbstractActivityRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Activity)

    async def get_by_name(self, name: str) -> Activity | None:
        result = await self.session.execute(select(Activity).filter(Activity.name == name))
        return result.scalars().first()

    async def get_sub_activities(self, activity_id: int, depth: int = 3) -> List[Activity]:
        if depth <= 0:
            return []

        root = await self.get_by_id(activity_id)
        if not root:
            return []

        base = select(
            Activity.id,
            Activity.parent_id,
            func.cast(0, Integer).label("level")
        ).where(Activity.id == activity_id).cte(name="activity_tree", recursive=True)

        activity_alias = aliased(Activity)
        recursive = select(
            activity_alias.id,
            activity_alias.parent_id,
            (base.c.level + 1).label("level")
        ).select_from(activity_alias).where(
            activity_alias.parent_id == base.c.id
        ).where(base.c.level < depth)

        cte = base.union_all(recursive)

        stmt = select(Activity).where(Activity.id.in_(select(cte.c.id)))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_depth(self, activity_id: int) -> int:
        if activity_id is None:
            return 0

        base = select(
            Activity.id,
            Activity.parent_id,
            func.cast(0, Integer).label("depth")
        ).where(Activity.id == activity_id)

        cte = base.cte(name="activity_path", recursive=True)

        activity_alias = aliased(Activity)

        recursive = select(
            activity_alias.id,
            activity_alias.parent_id,
            (cte.c.depth + 1).label("depth")
        ).select_from(
            activity_alias
        ).where(
            activity_alias.id == cte.c.parent_id
        )

        cte = cte.union_all(recursive)

        stmt = select(func.coalesce(func.max(cte.c.depth), 0))
        result = await self.session.execute(stmt)
        return result.scalar()
