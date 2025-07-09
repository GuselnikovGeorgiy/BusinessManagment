from typing import Optional

from sqlalchemy import select, delete, text, Sequence
from sqlalchemy_utils.types.ltree import Ltree

from app.models.departments import DepartmentModel
from app.repositories.base import SqlAlchemyRepository


class DepartmentRepository(SqlAlchemyRepository):
    model = DepartmentModel

    async def add_one(self, name: str, company_id: int, parent_id: Optional[int] = None) -> int:
        department = self.model(name=name, path=None, company_id=company_id)
        self.session.add(department)
        await self.session.flush()

        if parent_id:
            parent = await self.get_by_id(parent_id)
            if not parent:
                raise ValueError(f"Parent department not found")
            if not parent.path:
                raise ValueError("Parent path is not set")

            department.path = Ltree(f"{parent.path}.{department.id}")

        else:
            department.path = Ltree(f"{department.id}")

        self.session.add(department)
        await self.session.commit()

        return department.id

    async def get_ancestors(self, department_id: int) -> list[DepartmentModel]:
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError(f"Department not found")
        query = select(self.model).where(self.model.path.op("@>")(department.path))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_descendants(self, department_id: int) -> list[DepartmentModel]:
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError(f"Department not found")
        query = select(self.model).where(self.model.path.op("<@")(department.path))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_visualized_path(self, department_id: int) -> str:
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")

        path_ids = [int(part) for part in str(department.path).split(".")]

        query = select(self.model.id, self.model.name).where(self.model.id.in_(path_ids))
        result = await self.session.execute(query)
        id_name_map = {row.id: row.name for row in result.fetchall()}

        path_names = [id_name_map.get(dep_id, f"<missing:{dep_id}>") for dep_id in path_ids]

        return ".".join(path_names)

    async def get_ancestors_with_names(self, department_id: int) -> list[str]:
        ancestors = await self.get_ancestors(department_id)
        result = []
        for department in ancestors:
            visualized_path = self.get_visualized_path(department.id)
            result.append(visualized_path)
        return result

    async def get_descendants_with_names(self, department_id: int) -> list[str]:
        descendants = await self.get_descendants(department_id)
        result = []
        for department in descendants:
            visualized_path = self.get_visualized_path(department.id)
            result.append(visualized_path)
        return result

    async def move_department(self, department_id: int, new_parent_path: str):
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")
        department.path = f"{new_parent_path}.{department.name}"
        self.session.add(department)
        await self.session.commit()

    async def move_department_with_descendants(self, department_id: int, new_parent_path: str):
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")

        old_path = str(department.path)
        new_path = f"{new_parent_path}.{department.id}"

        department.path = Ltree(new_path)
        self.session.add(department)

        query = select(self.model).where(
            self.model.path.op("<@")(old_path),
            self.model.path != old_path
        )

        result = await self.session.execute(query)
        descendants = result.scalars().all()

        for descendant in descendants:
            descendant_old_path = str(descendant.path)
            relative_path = descendant_old_path[len(old_path) + 1:]
            descendant.path = Ltree(f"{new_path}.{relative_path}")
            self.session.add(descendant)

        await self.session.commit()

    async def delete_by_query(self, department_id: int):
        department = await self.get_by_id(department_id)
        if not department:
            raise ValueError("Department not found")

        query = delete(self.model).where(self.model.path.op("<@")(department.path))
        await self.session.execute(query)
        await self.session.commit()
