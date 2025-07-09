from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.users import UserModel
from app.repositories.base import SqlAlchemyRepository


class UserRepository(SqlAlchemyRepository):
    model = UserModel

    async def get_all_subordinates(self, user_id: int) -> list[dict]:
        # Загружаем всех пользователей, у которых есть менеджер
        result = await self.session.execute(select(self.model))
        all_users = result.scalars().all()

        # Создаем отображение: manager_id -> list of subordinates
        manager_map = {}
        for user in all_users:
            if user.manager_id is not None:
                manager_map.setdefault(user.manager_id, []).append(user)

        # Найти корневого пользователя
        root_user = next((u for u in all_users if u.id == user_id), None)
        if not root_user:
            raise ValueError("User not found")

        # Рекурсивный обход иерархии
        def collect_subordinates(user):
            subordinates = manager_map.get(user.id, [])
            result = []
            for sub in subordinates:
                result.append(sub)
                result.extend(collect_subordinates(sub))
            return result

        subordinates = collect_subordinates(root_user)
        return [self._serialize_user(user) for user in subordinates]

    def _serialize_user(self, user: UserModel) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "manager_id": user.manager_id,
            "department_id": user.department_id,
        }
