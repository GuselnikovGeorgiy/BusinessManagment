from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.companies import Company
from app.models.departments import Department
from app.models.positions import Position
from app.models.roles import RoleAssignment
from app.models.tasks import Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship("Company", back_populates="employees")
    position_id: Mapped[int] = mapped_column(ForeignKey("position.id"), nullable=True)
    position: Mapped["Position"] = relationship("Position", back_populates="users")
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="employees", foreign_keys=[department_id]
    )
    managed_departments: Mapped[list["Department"]] = relationship(
        "Department", back_populates="manager", foreign_keys="Department.manager_id"
    )
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    manager: Mapped[Optional["User"]] = relationship(
        "User", remote_side="User.id", back_populates="subordinates"
    )
    subordinates: Mapped[list["User"]] = relationship("User", back_populates="manager", lazy="joined")
    role_assignments: Mapped[list["RoleAssignment"]] = relationship(
        "RoleAssignment", back_populates="user"
    )
    observed_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary="task_observers",
        back_populates="observers",
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary="task_executors",
        back_populates="executors",
    )
