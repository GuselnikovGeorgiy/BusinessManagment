from typing import Optional

from fastapi import HTTPException
from pydantic import EmailStr

from app.schemas.user import UserUpdateRequest
from app.schemas.auth import UserToken
from app.services.base import BaseService
from app.uow.unit_of_work import transaction_mode
from app.auth.auth_utils import generate_invite_token, hash_password


class UserService(BaseService):

    @transaction_mode
    async def create_employee(
            self,
            email: EmailStr,
            first_name: str,
            last_name: str,
            company_id: int,
            current_user: UserToken,
            position_id: Optional[int] = None,
    ) -> dict:
        user_exists = await self.uow.user.get_by_query_one_or_none(email=email)
        if user_exists:
            raise HTTPException(status_code=400, detail="User already exists.")

        invite_exists = await self.uow.invite.get_by_query_one_or_none(email=email)
        if invite_exists and invite_exists.is_verified:
            raise HTTPException(status_code=400, detail="Invite already verified.")

        invite_token = generate_invite_token()

        temp_password = hash_password("temporary_password")

        await self.uow.user.add_one(
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=temp_password,
            is_admin=False,
            is_active=False,
            company_id=company_id,
            position_id=position_id,
        )

        await self.uow.invite.add_one(
            email=email, token=invite_token, company_id=company_id
        )

        return {
            "message": "Employee created and invite generated.",
            "invite_token": invite_token,
        }

    @transaction_mode
    async def update_user(
        self,
        user_id: int,
        schema: UserUpdateRequest,
        current_user: UserToken,
    ) -> dict:
        user = await self.uow.user.get_by_query_one_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        if user_id != current_user.user_id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied.")
        updates = schema.model_dump(exclude_unset=True)
        updates.pop("position_id", None)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update.")

        await self.uow.user.update_one_by_id(obj_id=user_id, **updates)
        return {
            "message": "User updated successfully.",
            "updated_fields": list(updates.keys()),
        }

    @transaction_mode
    async def update_email(
        self,
        user_id: int,
        new_email: EmailStr,
        current_user: UserToken,
    ) -> dict:
        existing_user = await self.uow.user.get_by_query_one_or_none(email=new_email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use.")
        if user_id != current_user.user_id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied.")

        await self.uow.user.update_one_by_id(obj_id=user_id, email=new_email)
        return {"message": "Email updated successfully."}
