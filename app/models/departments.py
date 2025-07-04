from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types.ltree import LtreeType
from typing import Optional, TYPE_CHECKING

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.roles import RoleAssignmentModel
    from app.models.companies import CompanyModel


class DepartmentModel(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(LtreeType, index=True, nullable=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    company: Mapped["CompanyModel"] = relationship("Company", back_populates="departments")
    manager: Mapped[Optional["UserModel"]] = relationship(
        "User", back_populates="managed_departments", foreign_keys=[manager_id]
    )
    employees: Mapped[list["UserModel"]] = relationship(
        "User", back_populates="department", foreign_keys="User.department_id"
    )
    role_assignments: Mapped[list["RoleAssignmentModel"]] = relationship(
        "RoleAssignment", back_populates="department"
    )
