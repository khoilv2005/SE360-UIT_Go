from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid
from models import UserTypeEnum

# Schema for token data
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for creating a new user (registration)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    user_type: UserTypeEnum

# Schema for reading/returning user data (without the password)
class User(BaseModel):
    user_id: uuid.UUID
    username: str
    email: EmailStr
    full_name: str
    user_type: UserTypeEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
    # Custom validator để hiển thị "chưa chỉnh" nếu full_name là null
    @classmethod
    def model_validate(cls, obj, **kwargs):
        if hasattr(obj, 'full_name') and obj.full_name is None:
            obj.full_name = "chưa chỉnh"
        return super().model_validate(obj, **kwargs)

class DriverProfileCreate(BaseModel):
    license_num: str
    birth: datetime
    card_num: str

class DriverProfile(BaseModel):
    user_id: uuid.UUID
    license_num: str
    birth: datetime
    rating_score: Optional[float] = None
    card_num: str

    class Config:
        from_attributes = True

class VehicleCreate(BaseModel):
    license_plate: str
    seat_type: int

class Vehicle(BaseModel):
    vehicle_id: uuid.UUID
    user_id: uuid.UUID
    license_plate: str
    seat_type: int

    class Config:
        from_attributes = True

