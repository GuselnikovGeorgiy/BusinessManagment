from app.models.tasks import TaskModel
from app.repositories.base import SqlAlchemyRepository


class TaskRepository(SqlAlchemyRepository):
    model = TaskModel
