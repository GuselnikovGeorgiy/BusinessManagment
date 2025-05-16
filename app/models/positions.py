from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import User


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (
        UniqueConstraint("name", "company_id", name="unique_position_in_company"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    users: Mapped[list["User"]] = relationship("User", back_populates="position")
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

