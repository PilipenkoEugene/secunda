from typing import List, Dict

from fastapi import APIRouter, HTTPException, Depends
from app.adapters.schemas import Organization, OrganizationCreate, OrganizationUpdate, OrganizationFull, RadiusSearch, RectangleSearch

from dishka.integrations.fastapi import FromDishka, inject

from app.services.organiztion import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Организация"])

@router.get("/", response_model=List[OrganizationFull])
@inject
async def get_all(
        service: FromDishka[OrganizationService]
) -> List[OrganizationFull]:
    return await service.get_all()

@router.post("/", response_model=Organization, response_model_exclude_unset=True)
@inject
async def create(organization: OrganizationCreate, service: FromDishka[OrganizationService]) -> Organization:
    return await service.create(**organization.model_dump())

@router.get("/search", response_model=List[OrganizationFull])
@inject
async def search_by_name(service: FromDishka[OrganizationService], name: str) -> List[OrganizationFull]:
    return await service.search_by_name(name)

@router.get("/by_building/{building_id}", response_model=List[OrganizationFull], response_model_exclude_unset=True)
@inject
async def get_by_building(building_id: int, service: FromDishka[OrganizationService]) -> List[OrganizationFull]:
    return await service.get_by_building(building_id)

@router.get("/by_activity/{activity_id}", response_model=List[OrganizationFull], response_model_exclude_unset=True)
@inject
async def get_by_activity(activity_id: int, service: FromDishka[OrganizationService]) -> List[OrganizationFull]:
    return await service.get_by_activity(activity_id)

@router.get("/by_radius", response_model=List[OrganizationFull], response_model_exclude_unset=True)
@inject
async def get_in_radius(service: FromDishka[OrganizationService], params: RadiusSearch = Depends()) -> List[OrganizationFull]:
    return await service.get_in_radius(params.lat, params.lon, params.radius_km)

@router.get("/by_rectangle", response_model=List[OrganizationFull], response_model_exclude_unset=True)
@inject
async def get_in_rect(service: FromDishka[OrganizationService], params: RectangleSearch = Depends()) -> List[OrganizationFull]:
    return await service.get_in_rect(params.min_lat, params.max_lat, params.min_lon, params.max_lon)

@router.get("/{org_id}", response_model=OrganizationFull, response_model_exclude_unset=True)
@inject
async def get_by_id(org_id: int, service: FromDishka[OrganizationService]) -> OrganizationFull:
    org = await service.get_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Организация с id {org_id} не найдена")
    return org

@router.put("/{org_id}", response_model=Organization, response_model_exclude_unset=True)
@inject
async def update(org_id: int, organization: OrganizationUpdate, service: FromDishka[OrganizationService]) -> Organization:
    org = await service.get_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Организация с id {org_id} не найдена")
    return await service.update(org, **organization.model_dump(exclude_unset=True))

@router.delete("/{org_id}", response_model=Dict, status_code=204)
@inject
async def delete(org_id: int, service: FromDishka[OrganizationService]):
    org = await service.get_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Организация с id {org_id} не найдена")
    await service.delete(org)
