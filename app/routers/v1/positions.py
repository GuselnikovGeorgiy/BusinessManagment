from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from app.auth.auth_utils import get_current_user
from app.schemas.user import UserToken
from app.services.position import PositionService


positions_router = APIRouter(prefix="/v1/positions", tags=["Positions"])


@positions_router.post("/")
async def create_position(
    name: str,
    description: Optional[str] = None,
    current_user: UserToken = Depends(get_current_user),
    service: PositionService = Depends(),
):
    return await service.create_position(
        name=name,
        description=description,
        company_id=current_user.company_id,
        current_user=current_user,
    )


@positions_router.patch("/{position_id}")
async def update_position(
    position_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    service: PositionService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.update_position(
        position_id=position_id,
        name=name,
        description=description,
        current_user=current_user,
    )


@positions_router.delete("/{position_id}")
async def delete_position(
    position_id: int,
    service: PositionService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.delete_position(
        position_id=position_id,
        current_user=current_user
    )


@positions_router.post("/{position_id}/assign-department/")
async def assign_position_to_department(
    position_id: int,
    department_id: int,
    service: PositionService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.assign_position_to_department(
        position_id=position_id,
        department_id=department_id,
        current_user=current_user,
    )


@positions_router.post("/{position_id}/assign-user/")
async def assign_position_to_user(
    position_id: int,
    user_id: int,
    service: PositionService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.assign_position_to_user(
        position_id=position_id,
        user_id=user_id,
        current_user=current_user,
    )


@cache(expire=100)
@positions_router.get("/{user_id}/subordinates/")
async def get_subordinates(
    user_id: int,
    service: PositionService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.get_subordinates(
        user_id=user_id,
        current_user=current_user
    )
