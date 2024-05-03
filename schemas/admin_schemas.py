from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional
from datetime import datetime


class AdminBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class AdminCreate(AdminBase):
    pass


class AdminUpdate(BaseModel):
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]


class AdminInDB(AdminBase):
    id: UUID4
    admin_type: str = "Admin"
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AdminBaseWithoutPassword(BaseModel):
    id: UUID4
    email: EmailStr
    first_name: str
    last_name: str
    profile_image: Optional[str]
    user_type: str = "Admin"


class AdminOut(AdminBaseWithoutPassword):
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
