from typing import List

from fastapi import HTTPException

from app.domain.abc_repositories import AbstractBuildingRepository
from app.domain.entities import Building


class BuildingService:
    def __init__(self, building_repo: AbstractBuildingRepository):
        self.building_repo = building_repo

    async def get_all(self) -> List[Building]:
        return await self.building_repo.get_all()

    async def get_by_id(self, building_id: int) -> Building | None:
        return await self.building_repo.get_by_id(building_id)

    async def create(self, address: str, latitude: float, longitude: float) -> Building:
        return await self.building_repo.create(
            address=address, latitude=latitude, longitude=longitude
        )

    async def update(
        self,
        building: Building,
        address: str = None,
        latitude: float = None,
        longitude: float = None,
    ) -> Building:
        return await self.building_repo.update(
            building, address=address, latitude=latitude, longitude=longitude
        )

    async def delete(self, building_id: int) -> None:
        building = await self.get_by_id(building_id)
        if not building:
            raise HTTPException(status_code=400, detail=f'Здание с id {building_id} не найдено')
        await self.building_repo.delete(building)
