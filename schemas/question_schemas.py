from pydantic import BaseModel, UUID4
from typing import List, Optional
from .choices_schemas import ChoiceUpdate, ChoiceCreate, ChoiceInDB


class QuestionBase(BaseModel):
    question: str
    correct_answer: str
    answer_temp: Optional[str]
    options_temp: Optional[str]
    choices: List[ChoiceCreate]


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    id: Optional[UUID4]
    question: Optional[str]
    correct_answer: Optional[str]
    answer_temp: Optional[str]
    options_temp: Optional[str]
    choices: Optional[List[ChoiceUpdate]]


class QuestionInDB(QuestionBase):
    id: UUID4
    choices: List[ChoiceInDB]

    class Config:
        orm_mode = True
