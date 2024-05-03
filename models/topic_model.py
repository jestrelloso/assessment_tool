from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
import uuid


class Topic(Base):
    __tablename__ = "topics"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    name = Column(String, nullable=False)

    # many-to-one relationship with Exam
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    exam = relationship("Exam", back_populates="topics")

    # one-to-many relationship with Question
    questions = relationship("Question", back_populates="topic", cascade="all, delete")
