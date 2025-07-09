from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.companies import CompanyModel
    from app.models.departments import DepartmentModel
    from app.models.positions import PositionModel
    from app.models.roles import RoleAssignmentModel
    from app.models.tasks import TaskModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["CompanyModel"] = relationship("Company", back_populates="employees")
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"), nullable=True)
    position: Mapped["PositionModel"] = relationship("Position", back_populates="users")
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    department: Mapped["DepartmentModel"] = relationship(
        "Department", back_populates="employees", foreign_keys=[department_id]
    )
    managed_departments: Mapped[list["DepartmentModel"]] = relationship(
        "Department", back_populates="manager", foreign_keys="Department.manager_id"
    )
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    manager: Mapped[Optional["UserModel"]] = relationship(
        "User", remote_side="User.id", back_populates="subordinates"
    )
    subordinates: Mapped[list["UserModel"]] = relationship("User", back_populates="manager", lazy="joined")
    role_assignments: Mapped[list["RoleAssignmentModel"]] = relationship(
        "RoleAssignment", back_populates="user"
    )
    observed_tasks: Mapped[list["TaskModel"]] = relationship(
        "Task",
        secondary="task_observers",
        back_populates="observers",
    )
    assigned_tasks: Mapped[list["TaskModel"]] = relationship(
        "Task",
        secondary="task_executors",
        back_populates="executors",
    )
