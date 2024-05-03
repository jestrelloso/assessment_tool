from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
import uuid


class Choice(Base):
    __tablename__ = "choices"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    option = Column(String, nullable=False)

    # many-to-one relationship with Question
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    question = relationship("Question", back_populates="choices")
