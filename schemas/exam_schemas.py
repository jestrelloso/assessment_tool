from typing import List, Optional
from pydantic import BaseModel, UUID4
from .topic_schemas import TopicCreate, TopicInDB, TopicUpdate


class ExamBase(BaseModel):
    title: str
    total_questions: int
    time_duration: int
    description: Optional[str] = None
    passing_rate: float
    enrollees: int = 0
    exam_topic: str
    grading_system: str
    number_of_items: int
    topics: List[TopicCreate]


class ExamCreate(ExamBase):
    pass


class ExamUpdate(ExamBase):
    title: Optional[str] = None
    total_questions: Optional[int] = None
    time_duration: Optional[int] = None
    description: Optional[str] = None
    passing_rate: Optional[float] = None
    topics: Optional[List[TopicUpdate]] = None
    cover_photo: Optional[str] = None
    enrollees: Optional[int] = None
    exam_topic: Optional[str] = None
    grading_system: Optional[str] = None
    number_of_items: Optional[int] = None


class ExamInDBBase(ExamBase):
    id: UUID4
    topics: List[TopicInDB] = []
    cover_photo: Optional[str]
    created_by: UUID4

    class Config:
        orm_mode = True


class Exam(ExamInDBBase):
    pass


class ExamInDB(ExamInDBBase):
    pass

    class Config:
        orm_mode = True
