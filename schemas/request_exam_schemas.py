from pydantic import BaseModel, UUID4

from .exam_schemas import ExamInDB
from .user_schemas import UserOut


class RequestExamBase(BaseModel):
    exam_id: UUID4


class RequestExamCreate(RequestExamBase):
    pass


class RequestExamUpdate(RequestExamBase):
    pass


class RequestExamInDBBase(RequestExamBase):
    id: UUID4
    status: str
    is_approved: bool
    examinee: UserOut
    exam: ExamInDB

    class Config:
        orm_mode = True


class RequestExam(RequestExamInDBBase):
    pass


class RequestExamInDB(RequestExamInDBBase):
    pass

    class Config:
        orm_mode = True
