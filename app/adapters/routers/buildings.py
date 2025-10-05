from typing import List, Dict

from fastapi import APIRouter, HTTPException
from app.adapters.schemas import Building, BuildingCreate, BuildingUpdate
from dishka.integrations.fastapi import FromDishka, inject

from app.services.building import BuildingService

router = APIRouter(prefix="/buildings", tags=["Buildings"])

@router.get("/", response_model=List[Building])
@inject
async def get_all(service: FromDishka[BuildingService]):
    return await service.get_all()

@router.get("/{building_id}", response_model=Building)
@inject
async def get_by_id(building_id: int, service: FromDishka[BuildingService]):
    building = await service.get_by_id(building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Здание с таким id не найдено")
    return building

@router.post("/", response_model=Building)
@inject
async def create(building: BuildingCreate, service: FromDishka[BuildingService]):
    return await service.create(**building.model_dump())

@router.put("/{building_id}", response_model=Building)
@inject
async def update(building_id: int, building: BuildingUpdate, service: FromDishka[BuildingService]):
    building_obj = await service.get_by_id(building_id)
    if not building_obj:
            raise HTTPException(status_code=404, detail="Здание с таким id не найдено")
    return await service.update(building_obj, **building.model_dump(exclude_unset=True))

@router.delete("/{building_id}", response_model=Dict)
@inject
async def delete(building_id: int, service: FromDishka[BuildingService]):
    building = await service.get_by_id(building_id)
    if not building:
            raise HTTPException(status_code=404, detail="Здание с таким id не найдено")
    await service.delete(building_id)
    return {"message": "Building deleted"}
