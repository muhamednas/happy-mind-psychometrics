import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class CandidateResponse(Base):
    __tablename__ = "candidate_responses"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidates.id"))
    test_id: Mapped[str] = mapped_column(String(255), nullable=False)
    question_id: Mapped[str] = mapped_column(String(255), nullable=False)
    response: Mapped[dict] = mapped_column(JSON, nullable=False)
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    __table_args__ = (
        UniqueConstraint('candidate_id', 'test_id', 'question_id', name='uix_candidate_test_question'),
    )
