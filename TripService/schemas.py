from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from models import (
    TripStatusEnum, LocationInfo, FareInfo, PaymentInfo, 
    RatingInfo, CancellationInfo, StatusHistory, PaymentMethodEnum,
    PaymentStatusEnum, CancelledByEnum, GeoLocation
)

# Input schemas for creating/updating
class LocationCreate(BaseModel):
    address: str = Field(..., max_length=100)
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)

# Schema for passenger creating a trip request (no driver yet)
class TripRequest(BaseModel):
    passenger_id: str
    pickup: LocationCreate
    dropoff: LocationCreate
    estimated_fare: Optional[float] = None
    notes: Optional[str] = None

# Schema for assigning driver to a trip
class AssignDriver(BaseModel):
    driver_id: str

# Original schema (for backward compatibility)
class TripCreate(BaseModel):
    passenger_id: str
    driver_id: str
    pickup: LocationCreate
    dropoff: LocationCreate
    estimated_fare: Optional[float] = None
    notes: Optional[str] = None

class TripUpdate(BaseModel):
    status: Optional[TripStatusEnum] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    actual_fare: Optional[float] = None
    discount: Optional[float] = None
    notes: Optional[str] = None

class PaymentCreate(BaseModel):
    method: PaymentMethodEnum
    transaction_id: Optional[str] = None

class PaymentUpdate(BaseModel):
    status: PaymentStatusEnum
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None

class RatingCreate(BaseModel):
    stars: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class CancellationCreate(BaseModel):
    cancelled_by: CancelledByEnum
    reason: Optional[str] = None

# Response schemas
class TripResponse(BaseModel):
    id: str = Field(alias="_id")
    passenger_id: str
    driver_id: str
    status: TripStatusEnum
    pickup: LocationInfo
    dropoff: LocationInfo
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    created_at: datetime
    fare: FareInfo
    payment: Optional[PaymentInfo] = None
    rating: Optional[RatingInfo] = None
    cancellation: Optional[CancellationInfo] = None
    history: List[StatusHistory] = []
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

class TripSummaryResponse(BaseModel):
    """Simplified trip response for list views"""
    id: str = Field(alias="_id")
    passenger_id: str
    driver_id: str
    status: TripStatusEnum
    pickup_address: str
    dropoff_address: str
    estimated_fare: Optional[float]
    actual_fare: Optional[float]
    created_at: datetime
    startTime: Optional[datetime]
    endTime: Optional[datetime]

    model_config = ConfigDict(populate_by_name=True)

class StandaloneRatingResponse(BaseModel):
    id: str = Field(alias="_id")
    trip_id: str
    passenger_id: str
    driver_id: str
    stars: int
    comment: Optional[str]
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)

# Statistics schemas
class TripStatistics(BaseModel):
    total_trips: int
    completed_trips: int
    cancelled_trips: int
    total_revenue: float
    average_rating: Optional[float]