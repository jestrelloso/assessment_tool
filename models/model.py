import uuid

from sqlalchemy import ARRAY, Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import INTEGER, UUID
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey

from db.database import Base


class User(Base):
    __tablename__ = "users"

    client_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    email = Column(String, nullable=False, unique=True)
    email_auth = Column(Boolean, default=False)
    exams = Column(ARRAY(String), nullable=True)
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


class Questions(Base):
    __tablename__ = "questions"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    question_text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Choices(Base):
    __tablename__ = "choices"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    choice_text = Column(String, index=True)
    isCorrect = Column(Boolean, default=False)
    question_id = Column(UUID, ForeignKey("questions.id", ondelete="CASCADE"))
