from typing import Optional

from fastapi import HTTPException

from app.schemas.user import UserToken
from app.services.base import BaseService
from app.uow.unit_of_work import transaction_mode


class PositionService(BaseService):
    @transaction_mode
    async def create_position(
            self,
            name: str,
            description: Optional[str],
            company_id: int,
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        position_id = await self.uow.position.add_one_and_get_id(
            name=name, description=description, company_id=company_id
        )
        return {"message": "Position created successfully.", "position_id": position_id}

    @transaction_mode
    async def update_position(
            self,
            position_id: int,
            name: Optional[str],
            description: Optional[str],
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        updates = {"name": name, "description": description}
        updates = {k: v for k, v in updates.items() if v is not None}

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update.")

        await self.uow.position.update_one_by_id(obj_id=position_id, **updates)
        return {"message": "Position updated successfully."}

    @transaction_mode
    async def delete_position(
            self,
            position_id: int,
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        await self.uow.position.delete_one_by_id(obj_id=position_id)
        return {"message": "Position deleted successfully."}

    @transaction_mode
    async def assign_position_to_department(
            self,
            position_id: int,
            department_id: int,
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        position = await self.uow.position.get_by_query_one_or_none(id=position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found.")

        await self.uow.position.update_one_by_id(
            obj_id=position_id, department_id=department_id
        )

        updated_position = await self.uow.position.get_by_query_one_or_none(
            id=position_id
        )

        return {
            "message": "Position assigned to department successfully.",
            "position_id": updated_position.id,
            "department_id": updated_position.department_id,
        }

    @transaction_mode
    async def assign_position_to_user(
            self,
            position_id: int,
            user_id: int,
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        position = await self.uow.position.get_by_id(position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found.")

        user = await self.uow.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        if position.company_id != user.company_id:
            raise HTTPException(
                status_code=400,
                detail="Position and user must belong to the same company.",
            )

        await self.uow.position.update_one_by_id(obj_id=position_id, user_id=user_id)

        return {"message": "Position assigned to user successfully"}

    @transaction_mode
    async def get_subordinates(
            self,
            user_id: int,
            current_user: UserToken,
    ) -> list:
        if not current_user.is_admin and current_user.user_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        subordinates = await self.uow.user.get_all_subordinates(user_id)
        return [sub.dict() for sub in subordinates]
