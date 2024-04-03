from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email_auth: bool = False
    exams: Optional[List[str]]
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    phone_number: str
    profile_image: Optional[str]
    four_digit_code: Optional[int]


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserInDB(UserBase):
    client_id: UUID4
    status: str = "Pending"
    user_type: str = "Examinee"
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserBaseWithoutPassword(BaseModel):
    client_id: UUID4
    email: EmailStr
    email_auth: bool = False
    exams: Optional[List[str]]
    first_name: str
    last_name: str
    phone_number: str
    profile_image: Optional[str]
    status: str = "Pending"
    user_type: str = "Examinee"
    four_digit_code: int


class UserOut(UserBaseWithoutPassword):
    created_at: datetime
    updated_at: Optional[datetime]
    four_digit_code: Optional[int]

    class Config:
        orm_mode = True
