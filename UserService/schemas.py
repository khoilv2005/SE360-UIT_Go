from pydantic import BaseModel, EmailStr
import uuid

# Schema for token data
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for creating a new user (registration)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Schema for reading/returning user data (without the password)
class User(BaseModel):
    id: uuid.UUID
    email: EmailStr

    class Config:
        from_attributes = True

