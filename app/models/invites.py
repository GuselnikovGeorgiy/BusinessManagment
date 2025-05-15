from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.companies import Company


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    token: Mapped[str] = mapped_column(unique=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
