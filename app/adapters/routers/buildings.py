from typing import List

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException

from app.adapters.schemas.building import (
    BuildingCreateSchema,
    BuildingSchema,
    BuildingUpdateSchema,
)
from app.services.building import BuildingService

router = APIRouter(prefix='/buildings', tags=['Здание'])


@router.get('/', response_model=List[BuildingSchema])
@inject
async def get_all(service: FromDishka[BuildingService]):
    return await service.get_all()


@router.get('/{building_id}', response_model=BuildingSchema)
@inject
async def get_by_id(building_id: int, service: FromDishka[BuildingService]):
    building = await service.get_by_id(building_id)
    if not building:
        raise HTTPException(status_code=404, detail=f'Здание с id {building_id} не найдено')
    return building


@router.post('/', response_model=BuildingSchema)
@inject
async def create(building: BuildingCreateSchema, service: FromDishka[BuildingService]):
    return await service.create(**building.model_dump())


@router.put('/{building_id}', response_model=BuildingSchema)
@inject
async def update(
    building_id: int, building: BuildingUpdateSchema, service: FromDishka[BuildingService]
):
    building_obj = await service.get_by_id(building_id)
    if not building_obj:
        raise HTTPException(status_code=404, detail=f'Здание с id {building_id} не найдено')
    return await service.update(building_obj, **building.model_dump(exclude_unset=True))


@router.delete('/{building_id}', status_code=204)
@inject
async def delete(building_id: int, service: FromDishka[BuildingService]):
    building = await service.get_by_id(building_id)
    if not building:
        raise HTTPException(status_code=404, detail=f'Здание с id {building_id} не найдено')
    await service.delete(building_id)
