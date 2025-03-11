from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from warehouse_app.api.schemas import RollRequestCreate, RollResponse, FilterRollParams
from warehouse_app.api.dependecies import get_roll_repository
from warehouse_app.database.repository import RollAbstractReposity

router = APIRouter()

@router.get("/", 
             response_model=list[RollResponse], 
             status_code=status.HTTP_200_OK)
async def get_rolls(
    filter_query: Annotated[FilterRollParams, Query()],
    repo: Annotated[RollAbstractReposity, Depends(get_roll_repository)],
) -> Any:
    
    rolls = await repo.get_all(filter_query.model_dump())
    return [RollResponse.model_validate(roll) for roll in rolls]

@router.post("/", 
             response_model=RollResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_roll(
    roll_data: RollRequestCreate,
    repo: Annotated[RollAbstractReposity, Depends(get_roll_repository)],
) -> Any:
    roll = await repo.add(roll_data)
    return RollResponse.model_validate(roll)

@router.delete("/{roll_id}",
               response_model=RollResponse,
               status_code=status.HTTP_200_OK)
async def delete_roll(
    roll_id: int,
    repo: Annotated[RollAbstractReposity, Depends(get_roll_repository)],
) -> Any:
    roll = await repo.delete(roll_id)
    if not roll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Рулон с ID {roll_id} не найден.",
        )
    return RollResponse.model_validate(roll)
