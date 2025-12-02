from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"