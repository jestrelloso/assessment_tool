from sqlalchemy import Table, Column, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from db.database import Base

examinee_exam_table = Table(
    "examinee_exam",
    Base.metadata,
    Column("examinee_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("exam_id", UUID(as_uuid=True), ForeignKey("exams.id")),
    Column("is_approved", Boolean, default=False),
)
