from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.departments import DepartmentModel


class CompanyModel(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    employees: Mapped[list["UserModel"]] = relationship(back_populates="company")
    departments: Mapped[list["DepartmentModel"]] = relationship("Department", back_populates="company")
