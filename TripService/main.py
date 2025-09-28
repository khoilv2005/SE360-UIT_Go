from fastapi import FastAPI, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv

import crud
import models
import schemas

# Load environment variables
load_dotenv()

app = FastAPI(title="UIT-Go Trip Service (MongoDB)", version="1.0.0")

@app.get("/")
async def get_service_info():
    return {"service": "UIT-Go Trip Service", "version": "1.0", "status": "running", "database": "MongoDB"}

# Trip CRUD routes
# New flow: FE sends coordinates -> BE returns fare estimates for all vehicle types
@app.post("/fare-estimate/", response_model=schemas.FareEstimateResponse)
async def estimate_fare(fare_request: schemas.FareEstimateRequest):
    """Estimate fare for all vehicle types based on pickup/dropoff coordinates"""
    pickup_coords = (fare_request.pickup.longitude, fare_request.pickup.latitude)
    dropoff_coords = (fare_request.dropoff.longitude, fare_request.dropoff.latitude)
    
    estimates = await crud.estimate_fare_for_all_vehicles(pickup_coords, dropoff_coords)
    
    if not estimates:
        raise HTTPException(status_code=400, detail="Could not calculate fare estimates")
    
    return schemas.FareEstimateResponse(estimates=estimates)

# New endpoints for passenger -> driver flow
@app.post("/trip-requests/", response_model=schemas.TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip_request(trip_request: schemas.TripRequest):
    """Passenger creates trip request (no driver assigned yet) - Legacy endpoint"""
    trip_data = await crud.create_trip_request(trip_request)
    return schemas.TripResponse(**trip_data)

@app.post("/trip-requests/complete/", response_model=schemas.TripResponse, status_code=status.HTTP_201_CREATED)
async def create_complete_trip_request(trip_request: schemas.TripRequestComplete):
    """Passenger creates trip request with complete location data from FE"""
    trip_data = await crud.create_trip_request_complete(trip_request)
    return schemas.TripResponse(**trip_data)

@app.put("/trips/{trip_id}/assign-driver", response_model=schemas.TripResponse)
async def assign_driver(trip_id: str, assign_data: schemas.AssignDriver):
    """Assign driver to a pending trip"""
    trip_data = await crud.assign_driver_to_trip(trip_id, assign_data.driver_id)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found or already assigned")
    return schemas.TripResponse(**trip_data)



@app.get("/trips/{trip_id}", response_model=schemas.TripResponse)
async def get_trip(trip_id: str):
    """Get trip by ID with all nested information"""
    trip_data = await crud.get_trip_by_id(trip_id)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return schemas.TripResponse(**trip_data)

@app.delete("/trips/{trip_id}")
async def delete_trip(trip_id: str):
    success = await crud.delete_trip(trip_id)
    if not success:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip deleted successfully"}

# Trip listing routes
@app.get("/trips/passenger/{passenger_id}", response_model=List[schemas.TripSummaryResponse])
async def get_passenger_trips(
    passenger_id: str, 
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=100)
):
    """Get trips for a specific passenger"""
    trips = await crud.get_trips_by_passenger(passenger_id, skip=skip, limit=limit)
    return [_convert_to_summary(trip) for trip in trips]

@app.get("/trips/driver/{driver_id}", response_model=List[schemas.TripSummaryResponse])
async def get_driver_trips(
    driver_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get trips for a specific driver"""
    trips = await crud.get_trips_by_driver(driver_id, skip=skip, limit=limit)
    return [_convert_to_summary(trip) for trip in trips]

@app.get("/trips/available/", response_model=List[schemas.TripSummaryResponse])
async def get_available_trips(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get available trips (PENDING status)"""
    trips = await crud.get_available_trips(skip=skip, limit=limit)
    return [_convert_to_summary(trip) for trip in trips]

@app.get("/trips/near/", response_model=List[schemas.TripSummaryResponse])
async def get_trips_near_location(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    max_distance: int = Query(5000, ge=100, le=50000),  # meters
    limit: int = Query(50, ge=1, le=100)
):
    """Get trips near a specific location using GeoJSON"""
    trips = await crud.get_trips_near_location(longitude, latitude, max_distance, limit)
    return [_convert_to_summary(trip) for trip in trips]

# Trip status management
@app.post("/trips/{trip_id}/accept")
async def accept_trip(trip_id: str):
    """Accept a trip (PENDING -> ACCEPTED)"""
    trip_data = await crud.update_trip_status(trip_id, models.TripStatusEnum.ACCEPTED)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip accepted successfully", "trip_id": trip_id, "status": "ACCEPTED"}

@app.post("/trips/{trip_id}/start")
async def start_trip(trip_id: str):
    """Start a trip (ACCEPTED -> ON_TRIP)"""
    trip_data = await crud.update_trip_status(trip_id, models.TripStatusEnum.ON_TRIP)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip started successfully", "trip_id": trip_id, "status": "ON_TRIP"}

@app.post("/trips/{trip_id}/deny")
async def deny_trip(trip_id: str, deny_data: schemas.AssignDriver):
    """Driver denies/rejects assigned trip - removes driver and sets back to PENDING"""
    trip_data = await crud.deny_trip(trip_id, deny_data.driver_id)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found or cannot be denied")
    return {"message": "Trip denied successfully - returned to pending", "trip_id": trip_id, "status": "PENDING"}

@app.post("/trips/{trip_id}/complete")
async def complete_trip(
    trip_id: str, 
    actual_fare: Optional[float] = None,
    discount: float = 0,
    tax: float = 0
):
    """Complete a trip (ON_TRIP -> COMPLETED)"""
    # Update status first
    trip_data = await crud.update_trip_status(trip_id, models.TripStatusEnum.COMPLETED)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Update fare if provided
    if actual_fare is not None:
        await crud.update_trip_fare(trip_id, actual_fare, discount, tax)
    
    return {"message": "Trip completed successfully", "trip_id": trip_id, "status": "COMPLETED"}

@app.post("/trips/{trip_id}/cancel")
async def cancel_trip(trip_id: str, cancellation: schemas.CancellationCreate):
    """Cancel a trip with reason"""
    trip_data = await crud.cancel_trip(trip_id, cancellation)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip cancelled successfully", "trip_id": trip_id, "status": "CANCELLED"}

# Payment management
@app.post("/trips/{trip_id}/payment")
async def add_payment_info(trip_id: str, payment: schemas.PaymentCreate):
    """Add payment information to trip"""
    trip_data = await crud.add_payment_info(trip_id, payment)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Payment info added successfully", "trip_id": trip_id}

@app.put("/trips/{trip_id}/payment")
async def update_payment_status(trip_id: str, payment_update: schemas.PaymentUpdate):
    """Update payment status"""
    trip_data = await crud.update_payment_status(trip_id, payment_update)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Payment status updated", "trip_id": trip_id, "status": payment_update.status}

# Rating management (embedded in trip)
@app.post("/trips/{trip_id}/rating")
async def add_trip_rating(trip_id: str, rating: schemas.RatingCreate):
    """Add rating to completed trip"""
    # Check if trip exists and is completed
    trip_data = await crud.get_trip_by_id(trip_id)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip_data["status"] != models.TripStatusEnum.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Can only rate completed trips")
    
    if trip_data.get("rating"):
        raise HTTPException(status_code=400, detail="Trip already rated")
    
    updated_trip = await crud.add_trip_rating(trip_id, rating)
    return {"message": "Rating added successfully", "trip_id": trip_id, "rating": rating.stars}

@app.get("/trips/{trip_id}/rating")
async def get_trip_rating(trip_id: str):
    """Get rating for a trip"""
    trip_data = await crud.get_trip_by_id(trip_id)
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    rating = trip_data.get("rating")
    if not rating:
        raise HTTPException(status_code=404, detail="No rating found for this trip")
    
    return rating

# Statistics
@app.get("/statistics/driver/{driver_id}", response_model=schemas.TripStatistics)
async def get_driver_statistics(driver_id: str):
    """Get trip statistics for a driver"""
    stats = await crud.get_trip_statistics(driver_id=driver_id)
    return schemas.TripStatistics(**stats)

@app.get("/statistics/passenger/{passenger_id}", response_model=schemas.TripStatistics)
async def get_passenger_statistics(passenger_id: str):
    """Get trip statistics for a passenger"""
    stats = await crud.get_trip_statistics(passenger_id=passenger_id)
    return schemas.TripStatistics(**stats)

# Helper function
def _convert_to_summary(trip: dict) -> schemas.TripSummaryResponse:
    """Convert full trip to summary response"""
    return schemas.TripSummaryResponse(
        _id=str(trip["_id"]),
        passenger_id=trip["passenger_id"],
        driver_id=trip["driver_id"],
        status=trip["status"],
        pickup_address=trip["pickup"]["address"],
        dropoff_address=trip["dropoff"]["address"],
        estimated_fare=trip.get("fare", {}).get("estimated"),
        actual_fare=trip.get("fare", {}).get("actual"),
        created_at=trip["created_at"],
        startTime=trip.get("startTime"),
        endTime=trip.get("endTime")
    )