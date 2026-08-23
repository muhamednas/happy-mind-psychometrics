import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Numeric, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CandidateProgress(Base):
    __tablename__ = "candidate_progress"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    corporate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("corporates.id", ondelete="CASCADE"), nullable=False
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="NOT_STARTED", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)

    __table_args__ = (
        UniqueConstraint("candidate_id", "assessment_id", name="uq_progress_candidate_assessment"),
    )
