from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime


class ExaminerBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class ExaminerCreate(ExaminerBase):
    pass


class ExaminerUpdate(BaseModel):
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]


class ExaminerInDB(ExaminerBase):
    id: UUID4
    status: str = "Pending"
    user_type: str = "Examiner"
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ExaminerBaseWithoutPassword(BaseModel):
    id: UUID4
    email: EmailStr
    first_name: str
    last_name: str
    profile_image: Optional[str]
    status: str = "Pending"
    user_type: str = "Examiner"


class ExaminerOut(ExaminerBaseWithoutPassword):
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
