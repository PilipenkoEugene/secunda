import re

from pydantic import BaseModel, Field, field_validator

from app.adapters.schemas.activity import ActivitySchema
from app.adapters.schemas.building import BuildingSchema


class OrganizationBaseSchema(BaseModel):
    name: str
    phones: list[str]
    building_id: int | None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str):
        if not v.strip():
            raise ValueError('Имя не может быть пустым')
        return v

    @field_validator('phones')
    @classmethod
    def validate_phones(cls, v: list[str]):
        phone_regex = re.compile(
            r'^'
            r'(?:'
            # +79991234567
            r'\+7\d{10}'
            r'|'
            # X-XXX-XXX
            r'[238](?:[-.\s]\d{3}){2}'
            r'|'
            # X-XXX-XXX-XX-XX
            r'[238](?:[-.\s]\d{3}){2}(?:[-.\s]\d{2}){2}'
            r')'
            r'$'
        )
        for phone in v:
            if not phone_regex.match(phone):
                raise ValueError(f'Неверный формат номера телефона: {phone}')
        return v


class OrganizationCreateSchema(OrganizationBaseSchema):
    activity_ids: list[int]

    @field_validator('activity_ids')
    @classmethod
    def validate_activity_ids(cls, v: list[int]):
        if not v:
            raise ValueError('Необходимо указать хотя бы один вид деятельности')
        return v


class OrganizationUpdateSchema(BaseModel):
    name: str | None = None
    phones: list[str] | None = None
    building_id: int | None = None
    activity_ids: list[int] | None = None

    @field_validator('activity_ids')
    @classmethod
    def validate_activity_ids(cls, v: list[int] | None):
        if v is not None and not v:
            raise ValueError('Необходимо указать хотя бы один вид деятельности')
        return v


class OrganizationSchema(OrganizationBaseSchema):
    id: int
    model_config = {'from_attributes': True}


class OrganizationFullSchema(OrganizationSchema):
    building: BuildingSchema | None
    activities: list[ActivitySchema]


class SearchByNameSchema(BaseModel):
    name: str = Field(min_length=1)


class RadiusSearchSchema(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    radius_km: float = Field(gt=0)


class RectangleSearchSchema(BaseModel):
    min_lat: float = Field(ge=-90, le=90)
    max_lat: float = Field(ge=-90, le=90)
    min_lon: float = Field(ge=-180, le=180)
    max_lon: float = Field(ge=-180, le=180)
