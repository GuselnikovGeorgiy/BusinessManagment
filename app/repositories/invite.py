from app.models.invites import InviteModel
from app.repositories.base import SqlAlchemyRepository


class InviteRepository(SqlAlchemyRepository):
    model = InviteModel
