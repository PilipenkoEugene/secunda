from typing import List

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException

from app.adapters.schemas.organization import (
    OrganizationCreateSchema,
    OrganizationFullSchema,
    OrganizationSchema,
    OrganizationUpdateSchema,
    RadiusSearchSchema,
    RectangleSearchSchema,
)
from app.services.organiztion import OrganizationService

router = APIRouter(prefix='/organizations', tags=['Организация'])


@router.get('/', response_model=List[OrganizationFullSchema])
@inject
async def get_all(service: FromDishka[OrganizationService]) -> List[OrganizationFullSchema]:
    return await service.get_all()


@router.post('/', response_model=OrganizationSchema)
@inject
async def create(
    organization: OrganizationCreateSchema, service: FromDishka[OrganizationService]
) -> OrganizationSchema:
    return await service.create(**organization.model_dump())


@router.get(
    '/search', response_model=List[OrganizationFullSchema], summary='Поиск организации по названию'
)
@inject
async def search_by_name(
    service: FromDishka[OrganizationService], name: str
) -> List[OrganizationFullSchema]:
    return await service.search_by_name(name)


@router.get(
    '/by_building/{building_id}',
    response_model=List[OrganizationFullSchema],
    summary='Список всех организаций находящихся в конкретном здании',
)
@inject
async def get_by_building(
    building_id: int, service: FromDishka[OrganizationService]
) -> List[OrganizationFullSchema]:
    return await service.get_by_building(building_id)


@router.get(
    '/by_activity/{activity_id}',
    response_model=List[OrganizationFullSchema],
    summary='Поиск по деятельности (с учетом поддеятельностей)',
)
@inject
async def get_by_activity(
    activity_id: int, service: FromDishka[OrganizationService]
) -> List[OrganizationFullSchema]:
    return await service.get_by_activity(activity_id)


@router.get(
    '/by_radius',
    response_model=List[OrganizationFullSchema],
    summary='Список организаций, которые находятся в заданном радиусе',
)
@inject
async def get_in_radius(
    service: FromDishka[OrganizationService], params: RadiusSearchSchema = Depends()
) -> List[OrganizationFullSchema]:
    return await service.get_in_radius(params.lat, params.lon, params.radius_km)


@router.get(
    '/by_rectangle',
    response_model=List[OrganizationFullSchema],
    summary='Список организаций, которые находятся в заданной прямоугольной области',
)
@inject
async def get_in_rect(
    service: FromDishka[OrganizationService], params: RectangleSearchSchema = Depends()
) -> List[OrganizationFullSchema]:
    return await service.get_in_rect(
        params.min_lat, params.max_lat, params.min_lon, params.max_lon
    )


@router.get(
    '/{org_id}',
    response_model=OrganizationFullSchema,
    summary='Вывод информации об организации по её идентификатору',
)
@inject
async def get_by_id(
    org_id: int, service: FromDishka[OrganizationService]
) -> OrganizationFullSchema:
    org = await service.get_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail=f'Организация с id {org_id} не найдена')
    return org


@router.put('/{org_id}', response_model=OrganizationSchema)
@inject
async def update(
    org_id: int, organization: OrganizationUpdateSchema, service: FromDishka[OrganizationService]
) -> OrganizationSchema:
    org = await service.get_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail=f'Организация с id {org_id} не найдена')
    return await service.update(org, **organization.model_dump(exclude_unset=True))


@router.delete('/{org_id}', status_code=204)
@inject
async def delete(org_id: int, service: FromDishka[OrganizationService]):
    org = await service.get_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail=f'Организация с id {org_id} не найдена')
    await service.delete(org)
