from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import uuid


class Examiner(Base):
    __tablename__ = "examiner"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    profile_image = Column(String, nullable=True)
    user_type = Column(String, default="Examiner")
    status = Column(String, default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # one-to-many relationship with Exam
    exams = relationship("Exam", back_populates="examiner")
