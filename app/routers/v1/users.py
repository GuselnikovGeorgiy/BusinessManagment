from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import EmailStr

from app.schemas.user import UserToken, UserUpdateRequest
from app.auth.auth_utils import get_current_user

from app.services.user import UserService


user_router = APIRouter(prefix="/v1/user", tags=["Users"])


@user_router.post("/create-employee")
async def create_employee(
    account: EmailStr,
    first_name: str,
    last_name: str,
    position_id: Optional[int] = None,
    current_user: UserToken = Depends(get_current_user),
    service: UserService = Depends(),
) -> dict:
    return await service.create_employee(
        email=account,
        first_name=first_name,
        last_name=last_name,
        company_id=current_user.company_id,
        position_id=position_id,
        current_user=current_user,
    )


@user_router.patch("/{user_id}")
async def update_user(
    user_id: int,
    schema: UserUpdateRequest,
    service: UserService = Depends(),
    current_user: UserToken = Depends(get_current_user)
) -> dict:
    return await service.update_user(
        user_id=user_id,
        schema=schema,
        current_user=current_user
    )


@user_router.patch("/{user_id}/update-email")
async def update_email(
    user_id: int,
    new_email: EmailStr,
    service: UserService = Depends(),
    current_user: UserToken = Depends(get_current_user)
) -> dict:
    return await service.update_email(
        user_id=user_id,
        new_email=new_email,
        current_user=current_user
    )
