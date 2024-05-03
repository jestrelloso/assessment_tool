from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
import uuid


class Question(Base):
    __tablename__ = "questions"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    question = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    answer_temp = Column(String, nullable=False)
    options_temp = Column(String, nullable=False)

    # many-to-one relationship with Topic
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    topic = relationship("Topic", back_populates="questions")

    # one-to-many relationship with Choice
    choices = relationship("Choice", back_populates="question", cascade="all, delete")
