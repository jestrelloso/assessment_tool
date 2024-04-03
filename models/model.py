from sqlalchemy import Column, String, Boolean, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import UUID, INTEGER
from sqlalchemy.sql import func
from db.database import Base
import uuid


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
