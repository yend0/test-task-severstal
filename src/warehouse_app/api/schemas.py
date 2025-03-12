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


class RollStatisticsResponse(BaseModel):
    total_added: int
    total_removed: int
    avg_length: float
    avg_weight: float
    total_weight: float
    min_max_roll_length: dict[str, float]
    min_max_roll_weight: dict[str, float]
    min_max_time_gap: dict[str, datetime.timedelta]
    day_min_rolls_count: datetime.date | None = None
    day_max_rolls_count: datetime.date | None = None
    day_min_weight: datetime.date | None = None
    day_max_weight: datetime.date | None = None


class FilterRollBaseParams(BaseModel):
    model_config = {"extra": "forbid", "populate_by_name": True}


class FilterRollParams(FilterRollBaseParams):
    id: list[int] | None = Field(None, min_length=2, max_length=2, alias="id_range")
    weight: list[float] | None = Field(None, min_length=2, max_length=2, alias="weight_range")
    length: list[float] | None = Field(None, min_length=2, max_length=2, alias="length_range")
    added_at: list[datetime.datetime] | None = Field(None, min_length=2, max_length=2, alias="added_range")
    removed_at: list[datetime.datetime] | None = Field(None, min_length=2, max_length=2, alias="removed_range")

    @field_validator("added_at", "removed_at", mode="before")
    @classmethod
    def validate_dates(cls, value: str | list[datetime.datetime] | None) -> str | list[datetime.datetime] | None:
        return validate_datetime_format(value)


class FilterRoolRangeDateParams(FilterRollBaseParams):
    date_range: list[datetime.datetime] = Field(min_length=2, max_length=2)

    @field_validator("date_range", mode="before")
    @classmethod
    def validate_dates(cls, value: str | list[datetime.datetime] | None) -> str | list[datetime.datetime] | None:
        return validate_datetime_format(value)


def validate_datetime_format(value: str | list[datetime.datetime] | None) -> str | list[datetime.datetime] | None:
    if value is None:
        return value
    if isinstance(value, list):
        for dt in value:
            if isinstance(dt, str) and dt.endswith('Z'):
                msg: str = f'Invalid datetime format: {dt}. Remove "Z" suffix.'
                raise ValueError(msg)
    elif isinstance(value, str) and value.endswith('Z'):
        msg: str = f'Invalid datetime format: {value}. Remove "Z" suffix.'
        raise ValueError(msg)

    return value
