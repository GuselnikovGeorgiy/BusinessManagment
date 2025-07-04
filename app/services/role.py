from fastapi import HTTPException

from app.schemas.user import UserToken
from app.services.base import BaseService
from app.uow.unit_of_work import transaction_mode


class RoleService(BaseService):
    @transaction_mode
    async def assign_role(
            self,
            user_id: int,
            department_id: int,
            role_name: str,
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        user = await self.uow.user.get_by_id(user_id)
        department = await self.uow.department.get_by_id(department_id)

        if not user or not department:
            raise HTTPException(status_code=404, detail="User or Department not found.")

        await self.uow.role_assignment.add_one(
            user_id=user_id, department_id=department_id, role_name=role_name
        )
        return {"message": "Role assigned successfully."}

    @transaction_mode
    async def get_roles(
            self,
            user_id: int,
            current_user: UserToken,
    ) -> list:
        if not current_user.is_admin and current_user.user_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        roles = await self.uow.role_assignment.get_by_query_all(user_id=user_id)
        return [
            {"department_id": role.department_id, "role_name": role.role_name}
            for role in roles
        ]
