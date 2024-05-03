from pydantic import BaseModel, UUID4


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenOut(BaseModel):
    user_id: UUID4
    user_type: str
