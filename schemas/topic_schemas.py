from pydantic import BaseModel, UUID4
from typing import List, Optional
from .question_schemas import QuestionCreate, QuestionInDB, QuestionUpdate


class TopicBase(BaseModel):
    name: str
    questions: List[QuestionCreate]


class TopicCreate(TopicBase):
    pass


class TopicUpdate(TopicBase):
    id: UUID4
    name: Optional[str] = None
    questions: Optional[List[QuestionUpdate]] = None


class TopicInDBBase(TopicBase):
    id: UUID4
    questions: List[QuestionInDB] = []

    class Config:
        orm_mode = True


class Topic(TopicInDBBase):
    pass


class TopicInDB(TopicInDBBase):
    pass
