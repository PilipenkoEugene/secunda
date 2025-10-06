from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.adapters.schemas import Activity, ActivityCreate, ActivityUpdate
from dishka.integrations.fastapi import FromDishka, inject

from app.services.activity import ActivityService

router = APIRouter(prefix="/activities", tags=["Деятельность"])

@router.get("/", response_model=List[Activity])
@inject
async def get_all(service: FromDishka[ActivityService]) -> List[Activity]:
    return await service.get_all()

@router.get("/{activity_id}", response_model=Activity)
@inject
async def get_by_id(activity_id: int, service: FromDishka[ActivityService]) -> Activity:
    activity = await service.get_by_id(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail=f"Деятельность с id {activity_id} не найдена")
    return activity

@router.post("/", response_model=Activity, summary="Создание Деятельности. Ограничено 3 уровнем вложенности")
@inject
async def create(activity: ActivityCreate, service: FromDishka[ActivityService]) -> Activity:
    return await service.create(**activity.model_dump())

@router.put("/{activity_id}", response_model=Activity)
@inject
async def update(service: FromDishka[ActivityService], activity_id: int, activity: ActivityUpdate = Depends()) -> Activity:
    activity_obj = await service.get_by_id(activity_id)
    if not activity_obj:
        raise HTTPException(status_code=404, detail=f"Деятельность с id {activity_id} не найдена")
    return await service.update(activity_obj, **activity.model_dump(exclude_unset=True))

@router.delete("/{activity_id}", status_code=204)
@inject
async def delete(activity_id: int, service: FromDishka[ActivityService]):
    activity = await service.get_by_id(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail=f"Деятельность с id {activity_id} не найдена")
    await service.delete(activity_id)
