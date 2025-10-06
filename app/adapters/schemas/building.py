from pydantic import BaseModel, Field, field_validator


class BuildingBaseSchema(BaseModel):
    address: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str):
        if not v.strip():
            raise ValueError('Адрес не может быть пустым')
        return v


class BuildingCreateSchema(BuildingBaseSchema):
    pass


class BuildingUpdateSchema(BaseModel):
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class BuildingSchema(BuildingBaseSchema):
    id: int
    model_config = {'from_attributes': True}
