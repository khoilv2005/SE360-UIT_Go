from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from models import (
    TripStatusEnum, LocationInfo, FareInfo, PaymentInfo, 
    RatingInfo, CancellationInfo, StatusHistory, PaymentMethodEnum,
    PaymentStatusEnum, CancelledByEnum, GeoLocation, VehicleTypeEnum,
    RouteInfo
)

# Input schemas for creating/updating
# Location with coordinates for fare estimation
class LocationCoordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

# Schema for fare estimation request
class FareEstimateRequest(BaseModel):
    pickup: LocationCoordinates
    dropoff: LocationCoordinates

# Schema for single vehicle fare estimate response
class VehicleFareEstimate(BaseModel):
    vehicle_type: VehicleTypeEnum
    estimated_fare: float
    distance_meters: float
    duration_seconds: float
    route_geometry: dict  # Contains encoded_polyline for FE to decode

# Schema for fare estimation response (all 3 vehicle types)
class FareEstimateResponse(BaseModel):
    estimates: List[VehicleFareEstimate]

# Enhanced location with both address and coordinates
class LocationComplete(BaseModel):
    address: str = Field(..., max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

# Simplified location for trip request (only address)
class LocationSimple(BaseModel):
    address: str = Field(..., max_length=100)

# Enhanced trip request with complete location data
class TripRequestComplete(BaseModel):
    passenger_id: str
    pickup: LocationComplete
    dropoff: LocationComplete
    vehicle_type: VehicleTypeEnum
    route_geometry: dict  # GeoJSON LineString from FE
    payment_method: PaymentMethodEnum = PaymentMethodEnum.CASH
    notes: Optional[str] = None

# Schema for passenger creating a trip request (no driver yet)
class TripRequest(BaseModel):
    passenger_id: str
    pickup: LocationSimple
    dropoff: LocationSimple
    vehicle_type: VehicleTypeEnum
    payment_method: PaymentMethodEnum = PaymentMethodEnum.CASH  # Default to cash
    notes: Optional[str] = None

# Schema for assigning driver to a trip
class AssignDriver(BaseModel):
    driver_id: str



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
    vehicle_type: VehicleTypeEnum
    status: TripStatusEnum
    pickup: LocationInfo
    dropoff: LocationInfo
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    created_at: datetime
    fare: FareInfo
    route_info: Optional[RouteInfo] = None
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