from pydantic import BaseModel, UUID4
from typing import Optional


class ChoiceBase(BaseModel):
    option: str


class ChoiceCreate(ChoiceBase):
    pass


class ChoiceUpdate(BaseModel):
    id: Optional[UUID4]
    option: Optional[str]


class ChoiceInDB(BaseModel):
    id: UUID4
    option: str
    question_id: UUID4

    class Config:
        orm_mode = True
