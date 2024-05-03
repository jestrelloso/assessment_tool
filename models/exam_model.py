from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db.database import Base
from .user_model import examinee_exam_table


class Exam(Base):
    __tablename__ = "exams"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    title = Column(String, nullable=False)
    total_questions = Column(Integer, nullable=False)
    time_duration = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    passing_rate = Column(Float, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("examiner.id"), nullable=False)
    cover_photo = Column(String, nullable=True)
    enrollees = Column(Integer, nullable=False, default=0)
    exam_topic = Column(String, nullable=False)
    grading_system = Column(String, nullable=False)
    number_of_items = Column(Integer, nullable=False)

    # one-to-many relationship with Topic
    topics = relationship("Topic", back_populates="exam", cascade="all, delete")

    examiner = relationship("Examiner", back_populates="exams")

    users = relationship("User", secondary=examinee_exam_table, back_populates="exams")
