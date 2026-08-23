import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Assessment(Base):
    """A single test within a package (normalized from the old JSON `tests` blob)."""

    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    corporate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("corporates.id", ondelete="CASCADE"), nullable=False
    )
    package_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("packages.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
