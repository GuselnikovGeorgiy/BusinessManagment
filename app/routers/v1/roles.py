from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from app.auth.auth_utils import get_current_user
from app.schemas.user import UserToken
from app.services.role import RoleService

roles_router = APIRouter(prefix="/v1/roles", tags=["Roles"])


@roles_router.post("/{user_id}/assign-role/")
async def assign_role(
    user_id: int,
    department_id: int,
    role_name: str,
    service: RoleService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.assign_role(
        user_id,
        department_id,
        role_name,
        current_user=current_user
    )


@cache(expire=100)
@roles_router.get("/{user_id}/roles/")
async def get_roles(
    user_id: int,
    service: RoleService = Depends(),
    current_user: UserToken = Depends(get_current_user),
):
    return await service.get_roles(user_id, current_user=current_user)
