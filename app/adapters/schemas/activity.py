from pydantic import BaseModel, Field, field_validator

class ActivityBaseSchema(BaseModel):
    name: str
    parent_id: int | None = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str):
        if not v.strip():
            raise ValueError("Имя не может быть пустым")
        if len(v) > 100:
            raise ValueError("Имя слишком длинное")
        return v

class ActivityCreateSchema(ActivityBaseSchema):
    pass

class ActivityUpdateSchema(BaseModel):
    name: str | None = None
    parent_id: int | None = Field(ge=1, default=None)

class ActivitySchema(ActivityBaseSchema):
    id: int
    model_config = {"from_attributes": True}
