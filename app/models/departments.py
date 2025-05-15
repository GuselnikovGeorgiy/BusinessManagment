from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types.ltree import LtreeType
from typing import Optional

from app.models.base import Base



class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(LtreeType, index=True, nullable=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    company: Mapped["Company"] = relationship("Company", back_populates="departments")
    manager: Mapped[Optional["User"]] = relationship(
        "User", back_populates="managed_departments", foreign_keys=[manager_id]
    )
    employees: Mapped[list["User"]] = relationship(
        "User", back_populates="department", foreign_keys="User.department_id"
    )
    role_assignments: Mapped[list["RoleAssignment"]] = relationship(
        "RoleAssignment", back_populates="department"
    )
