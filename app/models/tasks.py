from enum import Enum
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import User


class TaskStatus(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    CANCELED = "Canceled"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    responsible_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    observers: Mapped[list["User"]] = relationship(
        "User",
        secondary="task_observers",
        back_populates="observed_tasks",
        lazy="joined",
    )
    executors: Mapped[list["User"]] = relationship(
        "User",
        secondary="task_executors",
        back_populates="assigned_tasks",
        lazy="joined",
    )
    deadline: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        SQLAlchemyEnum(TaskStatus), default=TaskStatus.NEW.value
    )
    estimated_time: Mapped[Optional[float]] = mapped_column(nullable=True)


task_observers = Table(
    "task_observers",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

task_executors = Table(
    "task_executors",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)