from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import uuid


class RequestExam(Base):
    __tablename__ = "request_exams"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=True)
    examinee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    exam = relationship("Exam")
    examinee = relationship("User", back_populates="exam_requests")
    status = Column(String, default="Pending")
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
