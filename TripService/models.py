from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Annotated
from datetime import datetime
from enum import Enum
from bson import ObjectId

class TripStatusEnum(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    ON_TRIP = "ON_TRIP"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PaymentMethodEnum(str, Enum):
    CREDIT_CARD = "Credit Card"
    CASH = "Cash"
    E_WALLET = "E-Wallet"
    BANK_TRANSFER = "Bank Transfer"

class PaymentStatusEnum(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class CancelledByEnum(str, Enum):
    PASSENGER = "PASSENGER"
    DRIVER = "DRIVER"
    SYSTEM = "SYSTEM"

# Nested models for complex structures
class GeoLocation(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(..., min_items=2, max_items=2)  # [longitude, latitude]

class LocationInfo(BaseModel):
    address: str = Field(..., max_length=100)
    location: GeoLocation

class FareInfo(BaseModel):
    estimated: Optional[float] = None
    actual: Optional[float] = None
    discount: Optional[float] = 0.0
    tax: Optional[float] = 0.0

class PaymentInfo(BaseModel):
    method: PaymentMethodEnum
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None

class RatingInfo(BaseModel):
    stars: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    rated_at: Optional[datetime] = None

class CancellationInfo(BaseModel):
    cancelled_by: CancelledByEnum
    reason: Optional[str] = None
    cancelled_at: datetime = Field(default_factory=datetime.now)

class StatusHistory(BaseModel):
    status: TripStatusEnum
    timestamp: datetime = Field(default_factory=datetime.now)

class Trip(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    passenger_id: str  # ObjectId as string reference to users collection
    driver_id: str     # ObjectId as string reference to users collection
    status: TripStatusEnum = TripStatusEnum.PENDING
    
    # Location information with GeoJSON
    pickup: LocationInfo
    dropoff: LocationInfo
    
    # Time information
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Fare information
    fare: FareInfo = Field(default_factory=FareInfo)
    
    # Payment information
    payment: Optional[PaymentInfo] = None
    
    # Rating information
    rating: Optional[RatingInfo] = None
    
    # Cancellation information
    cancellation: Optional[CancellationInfo] = None
    
    # Status history
    history: List[StatusHistory] = Field(default_factory=list)
    
    # Additional notes
    notes: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
        
    def add_status_history(self, status: TripStatusEnum):
        """Add new status to history"""
        self.history.append(StatusHistory(status=status))
        self.status = status

# Separate Rating model for standalone ratings collection (if needed)
class StandaloneRating(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    trip_id: str  # ObjectId as string
    passenger_id: str
    driver_id: str
    stars: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
