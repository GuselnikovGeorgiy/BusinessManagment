from typing import Optional

from fastapi import HTTPException
from sqlalchemy_utils import Ltree

from app.schemas.user import UserToken
from app.services.base import BaseService
from app.uow.unit_of_work import transaction_mode


class DepartmentService(BaseService):
    @transaction_mode
    async def create_department(
            self,
            name: str,
            company_id: int,
            current_user: UserToken,
            parent_id: Optional[int] = None,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")

        department_id = await self.uow.department.add_one(
            name=name, company_id=company_id, parent_id=parent_id
        )
        visualized_path = await self.uow.department.get_visualized_path(department_id)

        return {
            "message": "Department created successfully",
            "department_id": department_id,
            "visualized_path": visualized_path,
        }

    @transaction_mode
    async def get_descendants(
            self,
            department_id: int,
            current_user: UserToken,
    ) -> list:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        descendants = await self.uow.department.get_descendants_with_names(department_id)
        return descendants

    @transaction_mode
    async def get_ancestors(
            self,
            department_id: int,
            current_user: UserToken,
    ) -> list:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        ancestors = await self.uow.department.get_ancestors_with_names(department_id)
        return ancestors

    @transaction_mode
    async def move_department(
            self,
            department_id: int,
            new_parent_id: int,
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        new_parent = await self.uow.department.get_by_id(new_parent_id)
        if not new_parent:
            raise HTTPException(
                status_code=404, detail="New parent department not found"
            )

        await self.uow.department.move_department_with_descendants(
            department_id, new_parent.path
        )
        visualized_path = await self.uow.department.get_visualized_path(department_id)

        return {
            "message": "Department moved successfully",
            "new_visualized_path": visualized_path,
        }

    @transaction_mode
    async def update_department(
            self,
            department_id: int,
            name: Optional[str],
            parent_id: Optional[int],
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")

        department = await self.uow.department.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        updates = {}
        if name is not None:
            updates["name"] = name

        old_path = department.path

        if parent_id is not None:
            new_parent = await self.uow.department.get_by_id(parent_id)
            if not new_parent:
                raise HTTPException(status_code=404, detail="New parent department not found")
            if not new_parent.path:
                raise HTTPException(status_code=400, detail="New parent path is not set")

            new_path = f"{new_parent.path}.{department.id}"
            updates["path"] = new_path

            department.path = Ltree(new_path)
            self.uow.department.session.add(department)

            descendants = await self.uow.department.get_descendants(department_id)
            for descendant in descendants:
                relative_path = descendant.path[len(old_path) + 1:]
                descendant.path = Ltree(f"{new_path}.{relative_path}")
                self.uow.department.session.add(descendant)

        if updates:
            await self.uow.department.update_one_by_id(obj_id=department_id, **updates)
        await self.uow.department.session.commit()
        return {"message": "Department updated successfully."}

    @transaction_mode
    async def delete_department(
            self,
            department_id: int,
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")

        department = await self.uow.department.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        await self.uow.department.delete_by_query(department_id=department_id)
        return {"message": "Department deleted successfully"}

    @transaction_mode
    async def assign_manager(
            self,
            department_id: int,
            user_id: int,
            current_user: UserToken,
    ) -> dict:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        department = await self.uow.department.get_by_id(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        await self.uow.department.update_one_by_id(department_id, manager_id=user_id)
        return {"message": "Manager assigned successfully"}
