from typing import List

from fastapi import HTTPException

from app.domain.entities import Organization
from app.domain.abc_repositories import AbstractBuildingRepository, AbstractActivityRepository, AbstractOrganizationRepository

class OrganizationService:
    def __init__(self, org_repo: AbstractOrganizationRepository, activity_repo: AbstractActivityRepository, building_repo: AbstractBuildingRepository):
        self.org_repo = org_repo
        self.activity_repo = activity_repo
        self.building_repo = building_repo

    async def get_all(self) -> List[Organization]:
        return await self.org_repo.get_all()

    async def get_by_id(self, org_id: int) -> Organization | None:
        return await self.org_repo.get_by_id(org_id)

    async def get_by_building(self, building_id: int) -> List[Organization]:
        return await self.org_repo.get_by_building(building_id)

    async def get_by_activity(self, activity_id: int) -> List[Organization]:
        sub_activities = await self.activity_repo.get_sub_activities(activity_id)
        result = await self.org_repo.get_by_activity([sub_activity.id for sub_activity in sub_activities])
        return result

    async def get_in_radius(self, lat: float, lon: float, radius_km: float) -> List[Organization]:
        return await self.org_repo.get_in_radius(lat, lon, radius_km)

    async def get_in_rect(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> List[Organization]:
        return await self.org_repo.get_in_rect(min_lat, max_lat, min_lon, max_lon)

    async def search_by_name(self, name: str) -> List[Organization]:
        return await self.org_repo.search_by_name(name)

    async def create(self, name: str, phones: list[str], building_id: int, activity_ids: list[int]) -> Organization:
        if not await self.building_repo.get_by_id(building_id):
            raise HTTPException(status_code=400, detail=f"Здание с id {building_id} не найдено")
        for aid in activity_ids:
            if not await self.activity_repo.get_by_id(aid):
                raise ValueError(f"Activity {aid} not found")
        return await self.org_repo.create(name=name, phones=phones, building_id=building_id, activity_ids=activity_ids)

    async def update(self, org: Organization, name: str = None, phones: list[str] = None, building_id: int = None, activity_ids: list[int] = None) -> Organization:
        if building_id is not None:
            if not await self.building_repo.get_by_id(building_id):
                raise HTTPException(status_code=400, detail=f"Здание с id {building_id} не найдено")
        if activity_ids is not None:
            for aid in activity_ids:
                if not await self.activity_repo.get_by_id(aid):
                    raise ValueError(f"Не обнаружена активность с id {aid}")
        return await self.org_repo.update(org, name=name, phones=phones, building_id=building_id, activity_ids=activity_ids)

    async def delete(self, org: Organization) -> None:
        await self.org_repo.delete(org)
