from app.models.positions import PositionModel
from app.repositories.base import SqlAlchemyRepository


class PositionRepository(SqlAlchemyRepository):
    model = PositionModel
