import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class RollRequestCreate(BaseModel):
    length: float = Field(..., gt=0, description="Roll length (must be greater than 0)")
    weight: float = Field(..., gt=0, description="Roll weight (must be greater than 0)")

class RollResponse(BaseModel):
    id: int
    length: float
    weight: float
    created_at: datetime.datetime
    removed_at: datetime.datetime | None

    model_config: ConfigDict = ConfigDict(from_attributes=True)

class FilterRollParams(BaseModel):
    id: list[int] | None = Field(None, max_length=2, alias="id_range")
    weight: list[float] | None = Field(None, max_length=2, alias="weight_range")
    length: list[float] | None = Field(None, max_length=2, alias="length_range")
    added_at: list[datetime.datetime] | None = Field(None, max_length=2, alias="added_range")
    removed_at: list[datetime.datetime] | None = Field(None, max_length=2, alias="removed_range")    
    model_config = {"extra": "forbid", "populate_by_name": True}

    @field_validator("added_at", "removed_at", mode="before")
    @classmethod
    def validate_datetime_format(cls, value: str | list[datetime.datetime] | None) -> str | list[datetime.datetime] | None:
        if value is None:
            return value
        if isinstance(value, list):
            for dt in value:
                if isinstance(dt, str) and dt.endswith("Z"):
                    raise ValueError(f"Invalid datetime format: {dt}. Remove 'Z' suffix.")
        elif isinstance(value, str) and value.endswith("Z"):
            raise ValueError(f"Invalid datetime format: {value}. Remove 'Z' suffix.")
        
        return value