import math

from fastapi import HTTPException
from sqlalchemy import select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, aliased

from app.domain.entities import Building, Activity, Organization
from app.domain.repositories import AbstractRepository, AbstractBuildingRepository, AbstractActivityRepository
from typing import Type, TypeVar, List

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


class BuildingRepository(BaseSqlAlchemyRepository[Building], AbstractBuildingRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Building)


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


class OrganizationRepository(BaseSqlAlchemyRepository[Organization]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Organization)

    def _with_relations(self, stmt):
        return stmt.options(
            joinedload(Organization.building),
            joinedload(Organization.activities)
        )

    async def get_all(self) -> List[Organization]:
        stmt = self._with_relations(select(Organization))
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_id(self, org_id: int) -> Organization | None:
        stmt = self._with_relations(select(Organization)).where(Organization.id == org_id)
        result = await self.session.execute(stmt)
        return result.unique().scalars().first()

    async def create(
        self,
        name: str,
        phones: list[str],
        building_id: int,
        activity_ids: list[int]
    ) -> Organization:
        if activity_ids and len(activity_ids) != len(set(activity_ids)):
            raise HTTPException(status_code=400, detail="Обнаружены дубликаты id организаций")

        building = await self.session.get(Building, building_id)
        if not building:
            raise HTTPException(status_code=400, detail=f"Здание с id {building_id} не найдено")

        activities = []
        if activity_ids:
            result = await self.session.execute(
                select(Activity).where(Activity.id.in_(activity_ids))
            )
            activities = list(result.scalars().all())
            if len(activities) != len(activity_ids):
                raise HTTPException(status_code=400, detail="Один или более id организаций невалидны")

        organization = Organization(
            name=name,
            phones=phones,
            building=building,
            activities=activities
        )

        self.session.add(organization)
        await self.session.commit()
        await self.session.refresh(
            organization,
            attribute_names=["id", "name", "phones", "building", "activities"]
        )
        return organization

    async def update(self, organization: Organization, **kwargs) -> Organization:
        if "activity_ids" in kwargs and kwargs["activity_ids"] is not None:
            activity_ids = kwargs.pop("activity_ids")
            if activity_ids:
                if len(activity_ids) != len(set(activity_ids)):
                    raise HTTPException(status_code=400, detail="Обнаружены дубликаты id организаций")
                result = await self.session.execute(
                    select(Activity).where(Activity.id.in_(activity_ids))
                )
                activities = list(result.scalars().all())
                if len(activities) != len(activity_ids):
                    raise HTTPException(status_code=400, detail="Один или более id организаций невалидны")
                organization.activities = activities
            else:
                organization.activities = []

        for key, value in kwargs.items():
            if value is not None:
                setattr(organization, key, value)

        await self.session.commit()
        await self.session.refresh(
            organization,
            attribute_names=["id", "name", "phones", "building", "activities"]
        )
        return organization

    async def delete(self, organization: Organization):
        await self.session.delete(organization)
        await self.session.commit()

    async def search_by_name(self, name: str) -> List[Organization]:
        stmt = self._with_relations(select(Organization)).where(Organization.name.ilike(f"%{name}%"))
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_building(self, building_id: int) -> List[Organization]:
        stmt = self._with_relations(select(Organization)).where(Organization.building_id == building_id)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_activity(self, activity_id: int) -> List[Organization]:
        stmt = (
            self._with_relations(select(Organization))
            .join(Organization.activities)
            .where(Activity.id == activity_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_in_radius(self, lat: float, lon: float, radius_km: float) -> List[Organization]:
        lat_delta = radius_km / 111.0
        cos_lat = math.cos(math.radians(lat))
        if abs(cos_lat) < 1e-6:
            lon_delta = radius_km / 111.0
        else:
            lon_delta = radius_km / (111.0 * cos_lat)

        stmt = (
            self._with_relations(select(Organization))
            .join(Organization.building)
            .where(
                Building.latitude.between(lat - lat_delta, lat + lat_delta) &
                Building.longitude.between(lon - lon_delta, lon + lon_delta)
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_in_rect(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> List[Organization]:
        stmt = (
            self._with_relations(select(Organization))
            .join(Organization.building)
            .where(
                Building.latitude.between(min_lat, max_lat) &
                Building.longitude.between(min_lon, max_lon)
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
