from app.models.companies import CompanyModel
from app.repositories.base import SqlAlchemyRepository


class CompanyRepository(SqlAlchemyRepository):
    model = CompanyModel
