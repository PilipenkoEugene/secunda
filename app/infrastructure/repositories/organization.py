import math
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.abc_repositories import AbstractOrganizationRepository
from app.domain.entities import Activity, Building, Organization
from app.infrastructure.repositories.base import BaseSqlAlchemyRepository


class OrganizationRepository(
    BaseSqlAlchemyRepository[Organization], AbstractOrganizationRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Organization)

    def _with_relations(self, stmt):
        return stmt.options(joinedload(Organization.building), joinedload(Organization.activities))

    async def get_all(self) -> List[Organization]:
        stmt = self._with_relations(select(Organization))
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_id(self, org_id: int) -> Organization | None:
        stmt = self._with_relations(select(Organization)).where(Organization.id == org_id)
        result = await self.session.execute(stmt)
        return result.unique().scalars().first()

    async def create(
        self, name: str, phones: list[str], building_id: int, activity_ids: list[int]
    ) -> Organization:
        if activity_ids and len(activity_ids) != len(set(activity_ids)):
            raise HTTPException(status_code=400, detail='Обнаружены дубликаты id организаций')

        building = await self.session.get(Building, building_id)
        if not building:
            raise HTTPException(status_code=400, detail=f'Здание с id {building_id} не найдено')

        activities = []
        if activity_ids:
            result = await self.session.execute(
                select(Activity).where(Activity.id.in_(activity_ids))
            )
            activities = list(result.scalars().all())
            if len(activities) != len(activity_ids):
                raise HTTPException(
                    status_code=400, detail='Один или более id организаций невалидны'
                )

        organization = Organization(
            name=name, phones=phones, building=building, activities=activities
        )

        self.session.add(organization)
        await self.session.commit()
        await self.session.refresh(
            organization, attribute_names=['id', 'name', 'phones', 'building', 'activities']
        )
        return organization

    async def update(self, organization: Organization, **kwargs) -> Organization:
        if 'activity_ids' in kwargs and kwargs['activity_ids'] is not None:
            activity_ids = kwargs.pop('activity_ids')
            if activity_ids:
                if len(activity_ids) != len(set(activity_ids)):
                    raise HTTPException(
                        status_code=400, detail='Обнаружены дубликаты id организаций'
                    )
                result = await self.session.execute(
                    select(Activity).where(Activity.id.in_(activity_ids))
                )
                activities = list(result.scalars().all())
                if len(activities) != len(activity_ids):
                    raise HTTPException(
                        status_code=400, detail='Один или более id организаций невалидны'
                    )
                organization.activities = activities
            else:
                organization.activities = []

        for key, value in kwargs.items():
            if value is not None:
                setattr(organization, key, value)

        await self.session.commit()
        await self.session.refresh(
            organization, attribute_names=['id', 'name', 'phones', 'building', 'activities']
        )
        return organization

    async def delete(self, organization: Organization):
        await self.session.delete(organization)
        await self.session.commit()

    async def search_by_name(self, name: str) -> List[Organization]:
        stmt = self._with_relations(select(Organization)).where(
            Organization.name.ilike(f'%{name}%')
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_building(self, building_id: int) -> List[Organization]:
        stmt = self._with_relations(select(Organization)).where(
            Organization.building_id == building_id
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_activity(self, activity_ids: list[int]) -> List[Organization]:
        stmt = (
            self._with_relations(select(Organization))
            .join(Organization.activities)
            .where(Activity.id.in_(activity_ids))
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
                Building.latitude.between(lat - lat_delta, lat + lat_delta)
                & Building.longitude.between(lon - lon_delta, lon + lon_delta)
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_in_rect(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> List[Organization]:
        stmt = (
            self._with_relations(select(Organization))
            .join(Organization.building)
            .where(
                Building.latitude.between(min_lat, max_lat)
                & Building.longitude.between(min_lon, max_lon)
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
