from sqlalchemy import Column, String, Integer, Enum, DateTime, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from database import Base

class UserTypeEnum(str, enum.Enum):
    PASSENGER = "PASSENGER"
    DRIVER = "DRIVER"

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    user_type = Column(Enum(UserTypeEnum), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    driver_profile = relationship("DriverProfile", back_populates="user", uselist=False)
    vehicles = relationship("Vehicle", back_populates="user")


class DriverProfile(Base):
    __tablename__ = "driver_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True, nullable=False)
    license_num = Column(String(20), nullable=False)
    birth = Column(DateTime, nullable=False)
    rating_score = Column(DECIMAL(2, 1))
    card_num = Column(String(20), nullable=False)

    user = relationship("User", back_populates="driver_profile")


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    license_plate = Column(String(20), nullable=False)
    seat_type = Column(Integer, nullable=False)

    user = relationship("User", back_populates="vehicles")

