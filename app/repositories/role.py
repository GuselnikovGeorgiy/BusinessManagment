from app.models.roles import RoleAssignmentModel
from app.repositories.base import SqlAlchemyRepository


class RoleAssignmentRepository(SqlAlchemyRepository):
    model = RoleAssignmentModel
