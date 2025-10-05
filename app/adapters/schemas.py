from pydantic import BaseModel, Field, field_validator
import re

class BuildingBase(BaseModel):
    address: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str):
        if not v.strip():
            raise ValueError("Address cannot be empty")
        return v

class BuildingCreate(BuildingBase):
    pass

class BuildingUpdate(BaseModel):
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None

class Building(BuildingBase):
    id: int
    model_config = {"from_attributes": True}

class ActivityBase(BaseModel):
    name: str
    parent_id: int | None = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        if len(v) > 100:
            raise ValueError("Name too long")
        return v

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = Field(ge=1, default=None)

class Activity(ActivityBase):
    id: int
    model_config = {"from_attributes": True}

class OrganizationBase(BaseModel):
    name: str
    phones: list[str]
    building_id: int | None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str):
        if not v.strip():
            raise ValueError("Name cannot be empty")
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
                raise ValueError(f"Invalid phone format: {phone}")
        return v

class OrganizationCreate(OrganizationBase):
    activity_ids: list[int]

    @field_validator('activity_ids')
    @classmethod
    def validate_activity_ids(cls, v: list[int]):
        if not v:
            raise ValueError("At least one activity required")
        return v

class OrganizationUpdate(BaseModel):
    name: str | None = None
    phones: list[str] | None = None
    building_id: int | None = None
    activity_ids: list[int] | None = None

    @field_validator('activity_ids')
    @classmethod
    def validate_activity_ids(cls, v: list[int] | None):
        if v is not None and not v:
            raise ValueError("At least one activity required")
        return v

class Organization(OrganizationBase):
    id: int
    model_config = {"from_attributes": True}

class OrganizationFull(Organization):
    building: Building | None
    activities: list[Activity]

class SearchByName(BaseModel):
    name: str = Field(min_length=1)

class RadiusSearch(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    radius_km: float = Field(gt=0)

class RectangleSearch(BaseModel):
    min_lat: float = Field(ge=-90, le=90)
    max_lat: float = Field(ge=-90, le=90)
    min_lon: float = Field(ge=-180, le=180)
    max_lon: float = Field(ge=-180, le=180)