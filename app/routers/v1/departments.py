from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.auth_utils import get_current_user
from app.schemas.user import UserToken
from app.services.department import DepartmentService

from fastapi_cache.decorator import cache


department_router = APIRouter(prefix="/v1/department", tags=["Department"])


@department_router.post("/")
async def create_department(
    name: str,
    parent_id: Optional[int] = None,
    current_user: UserToken = Depends(get_current_user),
    service: DepartmentService = Depends(),
):
    return await service.create_department(
        name=name,
        company_id=current_user.company_id,
        parent_id=parent_id,
        current_user=current_user,
    )


@cache(expire=100)
@department_router.get("/{department_id}/descendants")
async def get_descendants(
    department_id: int,
    service: DepartmentService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.get_descendants(
        department_id,
        current_user=current_user
    )


@cache(expire=100)
@department_router.get("/{department_id}/ancestors")
async def get_ancestors(
    department_id: int,
    service: DepartmentService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.get_ancestors(
        department_id,
        current_user=current_user
    )


@department_router.patch("/{department_id}/move")
async def move_department(
    department_id: int,
    new_parent_id: int,
    service: DepartmentService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.move_department(
        department_id,
        new_parent_id,
        current_user=current_user
    )


@department_router.patch("/{department_id}")
async def update_department(
    department_id: int,
    name: Optional[str] = None,
    parent_id: Optional[int] = None,
    service: DepartmentService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.update_department(
        department_id=department_id,
        name=name,
        parent_id=parent_id,
        current_user=current_user,
    )


@department_router.delete("/{department_id}")
async def delete_department(
    department_id: int,
    service: DepartmentService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.delete_department(
        department_id=department_id,
        current_user=current_user
    )


@department_router.post("/{department_id}/assign-manager/")
async def assign_manager(
    department_id: int,
    user_id: int,
    current_user: UserToken = Depends(get_current_user),
    service: DepartmentService = Depends(),
):
    return await service.assign_manager(
        department_id=department_id,
        user_id=user_id,
        current_user=current_user
    )