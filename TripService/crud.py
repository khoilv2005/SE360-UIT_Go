from typing import List, Optional
from bson import ObjectId
from database import trips_collection, ratings_collection
import models
import schemas
from datetime import datetime

def convert_objectid(doc):
    """Convert ObjectId to string for Pydantic models"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def get_trip_by_id(trip_id: str) -> Optional[dict]:
    """Get trip by ObjectId"""
    if not ObjectId.is_valid(trip_id):
        return None
    doc = await trips_collection.find_one({"_id": ObjectId(trip_id)})
    return convert_objectid(doc)

async def get_trips_by_passenger(passenger_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
    """Get trips by passenger ID"""
    cursor = trips_collection.find({"passenger_id": passenger_id}).skip(skip).limit(limit).sort("created_at", -1)
    return await cursor.to_list(length=limit)

async def get_trips_by_driver(driver_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
    """Get trips by driver ID"""
    cursor = trips_collection.find({"driver_id": driver_id}).skip(skip).limit(limit).sort("created_at", -1)
    return await cursor.to_list(length=limit)

async def get_available_trips(skip: int = 0, limit: int = 100) -> List[dict]:
    """Get available trips (status = PENDING)"""
    cursor = trips_collection.find({"status": models.TripStatusEnum.PENDING.value}).skip(skip).limit(limit).sort("created_at", -1)
    return await cursor.to_list(length=limit)

async def get_trips_near_location(longitude: float, latitude: float, max_distance: int = 5000, limit: int = 50) -> List[dict]:
    """Get trips near specific location using GeoJSON"""
    cursor = trips_collection.find({
        "pickup.location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": max_distance  # meters
            }
        },
        "status": models.TripStatusEnum.PENDING.value
    }).limit(limit)
    return await cursor.to_list(length=limit)

async def create_trip(trip: schemas.TripCreate) -> dict:
    """Create new trip with complex nested structure"""
    # Convert LocationCreate to LocationInfo with GeoJSON
    pickup_location = models.LocationInfo(
        address=trip.pickup.address,
        location=models.GeoLocation(
            coordinates=[trip.pickup.longitude, trip.pickup.latitude]
        )
    )
    
    dropoff_location = models.LocationInfo(
        address=trip.dropoff.address,
        location=models.GeoLocation(
            coordinates=[trip.dropoff.longitude, trip.dropoff.latitude]
        )
    )
    
    # Create fare info
    fare_info = models.FareInfo(
        estimated=trip.estimated_fare
    )
    
    # Create initial status history
    initial_history = [models.StatusHistory(status=models.TripStatusEnum.PENDING)]
    
    trip_data = models.Trip(
        passenger_id=trip.passenger_id,
        driver_id=trip.driver_id,
        pickup=pickup_location,
        dropoff=dropoff_location,
        fare=fare_info,
        history=initial_history,
        notes=trip.notes,
        status=models.TripStatusEnum.PENDING
    )
    
    trip_dict = trip_data.dict(by_alias=True, exclude_none=True)
    
    # Ensure ObjectId is properly handled
    if "_id" in trip_dict:
        trip_dict["_id"] = ObjectId(trip_dict["_id"])
    
    result = await trips_collection.insert_one(trip_dict)
    trip_dict["_id"] = result.inserted_id
    return trip_dict

async def create_trip_request(trip_request: schemas.TripRequest) -> dict:
    """Create new trip request from passenger (no driver assigned yet)"""
    # Convert LocationCreate to LocationInfo with GeoJSON
    pickup_location = models.LocationInfo(
        address=trip_request.pickup.address,
        location=models.GeoLocation(
            coordinates=[trip_request.pickup.longitude, trip_request.pickup.latitude]
        )
    )
    
    dropoff_location = models.LocationInfo(
        address=trip_request.dropoff.address,
        location=models.GeoLocation(
            coordinates=[trip_request.dropoff.longitude, trip_request.dropoff.latitude]
        )
    )
    
    # Create fare info
    fare_info = models.FareInfo(
        estimated=trip_request.estimated_fare
    )
    
    # Create initial status history
    initial_history = [models.StatusHistory(status=models.TripStatusEnum.PENDING)]
    
    # Create trip object (without driver_id) - explicitly set defaults
    trip_obj = models.Trip(
        passenger_id=trip_request.passenger_id,
        driver_id="",  # Empty initially - will be assigned later
        status=models.TripStatusEnum.PENDING,  # Explicitly set status
        pickup=pickup_location,
        dropoff=dropoff_location,
        created_at=datetime.now(),  # Explicitly set created_at
        fare=fare_info,
        history=initial_history,
        notes=trip_request.notes
    )
    
    # Convert to dict for MongoDB - exclude the id field to let MongoDB generate it
    trip_dict = trip_obj.model_dump(by_alias=True, exclude={"id"})
    
    # Insert to database
    result = await trips_collection.insert_one(trip_dict)
    
    # Add the inserted ID to the dict and return it directly
    trip_dict["_id"] = str(result.inserted_id)
    return trip_dict

async def assign_driver_to_trip(trip_id: str, driver_id: str) -> Optional[dict]:
    """Assign driver to a pending trip"""
    if not ObjectId.is_valid(trip_id):
        return None
        
    # Update trip with driver_id and change status to ACCEPTED
    new_history_entry = {
        "status": models.TripStatusEnum.ACCEPTED.value,
        "timestamp": datetime.now()
    }
    
    result = await trips_collection.update_one(
        {"_id": ObjectId(trip_id), "status": models.TripStatusEnum.PENDING.value},
        {
            "$set": {
                "driver_id": driver_id,
                "status": models.TripStatusEnum.ACCEPTED.value
            },
            "$push": {"history": new_history_entry}
        }
    )
    
    if result.modified_count == 0:
        return None
        
    return await get_trip_by_id(trip_id)

async def update_trip_status(trip_id: str, new_status: models.TripStatusEnum) -> Optional[dict]:
    """Update trip status and add to history"""
    if not ObjectId.is_valid(trip_id):
        return None
    
    # Get current trip
    current_trip = await get_trip_by_id(trip_id)
    if not current_trip:
        return None
    
    # Create new status history entry
    new_history_entry = {
        "status": new_status.value,
        "timestamp": datetime.now()
    }
    
    # Prepare update data
    set_data = {
        "status": new_status.value
    }
    
    # Add specific timestamp fields based on status
    if new_status == models.TripStatusEnum.ON_TRIP:
        set_data["startTime"] = datetime.now()
    elif new_status == models.TripStatusEnum.COMPLETED:
        set_data["endTime"] = datetime.now()
    
    # Update with both $set and $push operations
    result = await trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {
            "$set": set_data,
            "$push": {"history": new_history_entry}
        }
    )
    
    if result.modified_count:
        return await get_trip_by_id(trip_id)
    return None

async def update_trip_fare(trip_id: str, actual_fare: float, discount: float = 0, tax: float = 0) -> Optional[dict]:
    """Update trip fare information"""
    if not ObjectId.is_valid(trip_id):
        return None
    
    update_data = {
        "fare.actual": actual_fare,
        "fare.discount": discount,
        "fare.tax": tax
    }
    
    result = await trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        return await get_trip_by_id(trip_id)
    return None

async def add_payment_info(trip_id: str, payment: schemas.PaymentCreate) -> Optional[dict]:
    """Add payment information to trip"""
    if not ObjectId.is_valid(trip_id):
        return None
    
    payment_data = models.PaymentInfo(
        method=payment.method,
        transaction_id=payment.transaction_id,
        status=models.PaymentStatusEnum.PENDING
    )
    
    result = await trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"payment": payment_data.dict()}}
    )
    
    if result.modified_count:
        return await get_trip_by_id(trip_id)
    return None

async def update_payment_status(trip_id: str, payment_update: schemas.PaymentUpdate) -> Optional[dict]:
    """Update payment status"""
    if not ObjectId.is_valid(trip_id):
        return None
    
    update_data = {
        "payment.status": payment_update.status.value
    }
    
    if payment_update.transaction_id:
        update_data["payment.transaction_id"] = payment_update.transaction_id
    
    if payment_update.paid_at:
        update_data["payment.paid_at"] = payment_update.paid_at
    elif payment_update.status == models.PaymentStatusEnum.SUCCESS:
        update_data["payment.paid_at"] = datetime.now()
    
    result = await trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        return await get_trip_by_id(trip_id)
    return None

async def add_trip_rating(trip_id: str, rating: schemas.RatingCreate) -> Optional[dict]:
    """Add rating to trip (embedded)"""
    if not ObjectId.is_valid(trip_id):
        return None
    
    rating_data = models.RatingInfo(
        stars=rating.stars,
        comment=rating.comment,
        rated_at=datetime.now()
    )
    
    result = await trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"rating": rating_data.dict()}}
    )
    
    if result.modified_count:
        return await get_trip_by_id(trip_id)
    return None

async def cancel_trip(trip_id: str, cancellation: schemas.CancellationCreate) -> Optional[dict]:
    """Cancel trip with reason"""
    if not ObjectId.is_valid(trip_id):
        return None
    
    cancellation_data = models.CancellationInfo(
        cancelled_by=cancellation.cancelled_by,
        reason=cancellation.reason,
        cancelled_at=datetime.now()
    )
    
    # Update status and add cancellation info
    update_data = {
        "status": models.TripStatusEnum.CANCELLED.value,
        "cancellation": cancellation_data.dict(),
        "$push": {
            "history": {
                "status": models.TripStatusEnum.CANCELLED.value,
                "timestamp": datetime.now()
            }
        }
    }
    
    result = await trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        return await get_trip_by_id(trip_id)
    return None

async def delete_trip(trip_id: str) -> bool:
    """Delete trip"""
    if not ObjectId.is_valid(trip_id):
        return False
    
    result = await trips_collection.delete_one({"_id": ObjectId(trip_id)})
    return result.deleted_count > 0

async def get_trip_statistics(driver_id: Optional[str] = None, passenger_id: Optional[str] = None) -> dict:
    """Get trip statistics"""
    match_condition = {}
    
    if driver_id:
        match_condition["driver_id"] = driver_id
    if passenger_id:
        match_condition["passenger_id"] = passenger_id
    
    pipeline = [
        {"$match": match_condition},
        {
            "$group": {
                "_id": None,
                "total_trips": {"$sum": 1},
                "completed_trips": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "COMPLETED"]}, 1, 0]
                    }
                },
                "cancelled_trips": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "CANCELLED"]}, 1, 0]
                    }
                },
                "total_revenue": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$status", "COMPLETED"]},
                            "$fare.actual",
                            0
                        ]
                    }
                },
                "average_rating": {"$avg": "$rating.stars"}
            }
        }
    ]
    
    result = await trips_collection.aggregate(pipeline).to_list(length=1)
    return result[0] if result else {
        "total_trips": 0,
        "completed_trips": 0, 
        "cancelled_trips": 0,
        "total_revenue": 0,
        "average_rating": None
    }

async def add_trip_rating(trip_id: str, rating: schemas.RatingCreate) -> Optional[dict]:
    """Add rating to a completed trip"""
    if not ObjectId.is_valid(trip_id):
        return None
    
    # Create rating object with timestamp
    rating_data = {
        "stars": rating.stars,
        "comment": rating.comment,
        "rated_at": datetime.now()
    }
    
    # Update trip with rating
    result = await trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"rating": rating_data}}
    )
    
    if result.modified_count:
        return await get_trip_by_id(trip_id)
    return None