from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.departments import DepartmentModel
    from app.models.users import UserModel


class RoleAssignmentModel(Base):
    __tablename__ = "role_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    role_name: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["UserModel"] = relationship("User", back_populates="role_assignments")
    department: Mapped["DepartmentModel"] = relationship(
        "Department", back_populates="role_assignments"
    )