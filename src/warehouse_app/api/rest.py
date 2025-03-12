from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from warehouse_app.api.dependecies import get_roll_service
from warehouse_app.api.schemas import (
    FilterRollParams,
    FilterRoolRangeDateParams,
    RollRequestCreate,
    RollResponse,
    RollStatisticsResponse,
)
from warehouse_app.service.roll import RollService

router = APIRouter()


@router.get("/", response_model=list[RollResponse], status_code=status.HTTP_200_OK)
async def get_rolls(
    filter_query: Annotated[FilterRollParams, Query()],
    roll_service: Annotated[RollService, Depends(get_roll_service)],
) -> Any:
    rolls = await roll_service.get_rolls(filter_query.model_dump())
    return [RollResponse.model_validate(roll) for roll in rolls]


@router.get("/statistics/", response_model=RollStatisticsResponse, status_code=status.HTTP_200_OK)
async def get_roll_statistics(
    date_params: Annotated[FilterRoolRangeDateParams, Query()],
    roll_service: Annotated[RollService, Depends(get_roll_service)],
) -> Any:
    date_range = date_params.model_dump()
    roll_statistic = await roll_service.get_statistic(date_range)

    return roll_statistic


@router.post("/", response_model=RollResponse, status_code=status.HTTP_201_CREATED)
async def add_roll(
    roll_data: RollRequestCreate,
    roll_service: Annotated[RollService, Depends(get_roll_service)],
) -> Any:
    roll = await roll_service.add_roll(roll_data)
    return RollResponse.model_validate(roll)


@router.delete("/{roll_id}", response_model=RollResponse, status_code=status.HTTP_200_OK)
async def delete_roll(
    roll_id: int,
    roll_service: Annotated[RollService, Depends(get_roll_service)],
) -> Any:
    roll = await roll_service.delete_roll(roll_id)
    if not roll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Roll with ID {roll_id} not found.",
        )
    return RollResponse.model_validate(roll)
