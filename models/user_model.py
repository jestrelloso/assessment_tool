from sqlalchemy import Column, String, Boolean, ARRAY, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
from .examinee_exam_table_model import examinee_exam_table
from sqlalchemy import and_
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    email = Column(String, nullable=False, unique=True)
    email_auth = Column(Boolean, default=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    profile_image = Column(String, nullable=True)
    status = Column(String, default="Pending")
    user_type = Column(String, default="Examinee")
    four_digit_code = Column(INTEGER, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    exams = relationship(
        "Exam",
        secondary=examinee_exam_table,
        primaryjoin=(
            lambda: and_(
                User.id == examinee_exam_table.c.examinee_id,
                examinee_exam_table.c.is_approved == True,
            )
        ),
        lazy="joined",
    )
    exam_requests = relationship("RequestExam", back_populates="examinee")
