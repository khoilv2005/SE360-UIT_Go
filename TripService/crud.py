from typing import List, Optional
from bson import ObjectId
from database import trips_collection, ratings_collection
import models
import schemas
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
# import polyline  # Uncomment if you install polyline package

# Load environment variables from .env file
load_dotenv()

# Mapbox API configuration
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", "pk.your_mapbox_token_here")

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

async def get_coordinates(location_name: str) -> tuple | None:
    """Hàm này nhận tên một địa điểm và trả về tọa độ (kinh độ, vĩ độ)."""
    geocoding_url = "https://api.mapbox.com/search/geocode/v6/forward"
    params = {
        'q': location_name,
        'access_token': MAPBOX_ACCESS_TOKEN,
        'limit': 1
    }
    
    print(f"Mapbox token: {MAPBOX_ACCESS_TOKEN}")
    print(f"Requesting geocoding for: {location_name}")
    print(f"URL: {geocoding_url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(geocoding_url, params=params)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response body: {response.text}")
        
        response.raise_for_status()
        data = response.json()
        
        if data.get("features"):
            coords = data["features"][0]["geometry"]["coordinates"]
            return (coords[0], coords[1])  # (kinh độ, vĩ độ)
        else:
            print(f"No features found for location: {location_name}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Mapbox API error: {e}")
        raise e



async def get_route_info(pickup_coords: tuple[float, float], dropoff_coords: tuple[float, float], vehicle_type: models.VehicleTypeEnum) -> dict | None:
    """Get route information from Mapbox Directions API"""
    # Use driving profile for all vehicle types
    directions_url = "https://api.mapbox.com/directions/v5/mapbox/driving"
    coordinates = f"{pickup_coords[0]},{pickup_coords[1]};{dropoff_coords[0]},{dropoff_coords[1]}"
    
    params = {
        'access_token': MAPBOX_ACCESS_TOKEN,
        'geometries': 'polyline',
        'overview': 'full'
    }
    
    # For motorcycles (2-seater), exclude motorways
    if vehicle_type == models.VehicleTypeEnum.TWO_SEATER:
        params['exclude'] = 'motorway'
    
    print(f"Requesting directions from {pickup_coords} to {dropoff_coords}")
    print(f"URL: {directions_url}/{coordinates}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(f"{directions_url}/{coordinates}", params=params)
        print(f"Directions response status: {response.status_code}")
        print(f"Directions response: {response.text}")
        
        response.raise_for_status()
        data = response.json()
        
        if data.get("routes"):
            route = data["routes"][0]
            return {
                "distance": route["distance"],  # meters
                "duration": route["duration"],  # seconds
                "geometry": route["geometry"]   # encoded polyline
            }
        else:
            print("No routes found")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Directions API error: {e}")
        raise e



def calculate_estimated_fare(distance_meters: float, vehicle_type: models.VehicleTypeEnum) -> float:
    """Calculate estimated fare based on distance and vehicle type"""
    # TODO: Implement your fare calculation logic here
    # Base fare + distance-based pricing + vehicle type multiplier
    
    distance_km = distance_meters / 1000
    
    # Base fare by vehicle type
    base_fares = {
        models.VehicleTypeEnum.TWO_SEATER: 15000,   # 2 chỗ
        models.VehicleTypeEnum.FOUR_SEATER: 20000,  # 4 chỗ
        models.VehicleTypeEnum.SEVEN_SEATER: 30000  # 7 chỗ
    }
    
    # Per km rate by vehicle type
    per_km_rates = {
        models.VehicleTypeEnum.TWO_SEATER: 8000,    # 2 chỗ
        models.VehicleTypeEnum.FOUR_SEATER: 10000,  # 4 chỗ
        models.VehicleTypeEnum.SEVEN_SEATER: 15000  # 7 chỗ
    }
    
    base_fare = base_fares.get(vehicle_type, 20000)
    per_km_rate = per_km_rates.get(vehicle_type, 10000)
    
    estimated_fare = base_fare + (distance_km * per_km_rate)
    
    # Round to nearest 1000 VND
    return round(estimated_fare / 1000) * 1000

async def estimate_fare_for_all_vehicles(pickup_coords: tuple[float, float], dropoff_coords: tuple[float, float]) -> List[dict]:
    """Estimate fare for all 3 vehicle types"""
    estimates = []
    
    for vehicle_type in [models.VehicleTypeEnum.TWO_SEATER, models.VehicleTypeEnum.FOUR_SEATER, models.VehicleTypeEnum.SEVEN_SEATER]:
        # Get route info for this vehicle type
        route_info = await get_route_info(pickup_coords, dropoff_coords, vehicle_type)
        
        if route_info:
            # Calculate fare
            estimated_fare = calculate_estimated_fare(route_info["distance"], vehicle_type)
            
            # Let FE handle polyline decoding
            route_geometry = {
                "type": "LineString",
                "encoded_polyline": route_info["geometry"]  # FE will decode this to coordinates
            }
            
            estimates.append({
                "vehicle_type": vehicle_type,
                "estimated_fare": estimated_fare,
                "distance_meters": route_info["distance"],
                "duration_seconds": route_info["duration"],
                "route_geometry": route_geometry
            })
    
    return estimates

async def create_trip_request_complete(trip_request: schemas.TripRequestComplete) -> dict:
    """Create trip request with complete location data from FE"""
    # Convert complete locations to LocationInfo with GeoJSON
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
    
    # Calculate route info from coordinates
    pickup_coords = (trip_request.pickup.longitude, trip_request.pickup.latitude)
    dropoff_coords = (trip_request.dropoff.longitude, trip_request.dropoff.latitude)
    route_info_data = await get_route_info(pickup_coords, dropoff_coords, trip_request.vehicle_type)
    
    if not route_info_data:
        raise ValueError("Could not calculate route between coordinates")
    
    # Create RouteInfo object
    route_info = models.RouteInfo(
        distance=route_info_data["distance"],
        duration=route_info_data["duration"], 
        geometry=route_info_data["geometry"]
    )
    
    # Calculate estimated fare
    estimated_fare = calculate_estimated_fare(route_info_data["distance"], trip_request.vehicle_type)
    
    # Create fare info
    fare_info = models.FareInfo(
        estimated=estimated_fare
    )
    
    # Create payment info
    payment_info = models.PaymentInfo(
        method=trip_request.payment_method,
        status=models.PaymentStatusEnum.PENDING
    )
    
    # Create initial status history
    initial_history = [models.StatusHistory(status=models.TripStatusEnum.PENDING)]
    
    # Create trip object
    trip_obj = models.Trip(
        passenger_id=trip_request.passenger_id,
        driver_id="",  # Empty initially
        vehicle_type=trip_request.vehicle_type,
        status=models.TripStatusEnum.PENDING,
        pickup=pickup_location,
        dropoff=dropoff_location,
        created_at=datetime.now(),
        fare=fare_info,
        route_info=route_info,
        payment=payment_info,
        history=initial_history,
        notes=trip_request.notes
    )
    
    # Convert to dict for MongoDB
    trip_dict = trip_obj.model_dump(by_alias=True, exclude={"id"})
    
    # Insert to database
    result = await trips_collection.insert_one(trip_dict)
    trip_dict["_id"] = str(result.inserted_id)
    return trip_dict

async def create_trip_request(trip_request: schemas.TripRequest) -> dict:
    """Create new trip request from passenger (using Mapbox APIs)"""
    # Get coordinates from addresses using Mapbox Geocoding API
    pickup_coords = await get_coordinates(trip_request.pickup.address)
    dropoff_coords = await get_coordinates(trip_request.dropoff.address)
    
    if not pickup_coords or not dropoff_coords:
        raise ValueError("Could not geocode one or both addresses")
    
    # Get route information from Mapbox Directions API
    route_info_data = await get_route_info(pickup_coords, dropoff_coords, trip_request.vehicle_type)
    
    if not route_info_data:
        raise ValueError("Could not calculate route between addresses")
    
    # Create RouteInfo object
    route_info = models.RouteInfo(
        distance=route_info_data["distance"],
        duration=route_info_data["duration"], 
        geometry=route_info_data["geometry"]
    )
    
    # Calculate estimated fare based on distance and vehicle type
    estimated_fare = calculate_estimated_fare(route_info_data["distance"], trip_request.vehicle_type)
    
    # Convert addresses to LocationInfo with Mapbox coordinates
    pickup_location = models.LocationInfo(
        address=trip_request.pickup.address,
        location=models.GeoLocation(
            coordinates=[pickup_coords[0], pickup_coords[1]]  # [longitude, latitude]
        )
    )
    
    dropoff_location = models.LocationInfo(
        address=trip_request.dropoff.address,
        location=models.GeoLocation(
            coordinates=[dropoff_coords[0], dropoff_coords[1]]  # [longitude, latitude]
        )
    )
    
    # Create fare info with calculated estimate
    fare_info = models.FareInfo(
        estimated=estimated_fare
    )
    
    # Create payment info from request
    payment_info = models.PaymentInfo(
        method=trip_request.payment_method,
        status=models.PaymentStatusEnum.PENDING
    )
    
    # Create initial status history
    initial_history = [models.StatusHistory(status=models.TripStatusEnum.PENDING)]
    
    # Create trip object (without driver_id) - explicitly set defaults
    trip_obj = models.Trip(
        passenger_id=trip_request.passenger_id,
        driver_id="",  # Empty initially - will be assigned later
        vehicle_type=trip_request.vehicle_type,  # Vehicle type from request
        status=models.TripStatusEnum.PENDING,  # Explicitly set status
        pickup=pickup_location,
        dropoff=dropoff_location,
        created_at=datetime.now(),  # Explicitly set created_at
        fare=fare_info,
        route_info=route_info,  # Add route information
        payment=payment_info,  # Add payment information
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

async def deny_trip(trip_id: str, driver_id: str) -> Optional[dict]:
    """Driver denies/rejects assigned trip - removes driver and sets back to PENDING"""
    if not ObjectId.is_valid(trip_id):
        return None
    
    # Only allow denial if trip is ACCEPTED and belongs to this driver
    new_history_entry = {
        "status": models.TripStatusEnum.PENDING.value,
        "timestamp": datetime.now()
    }
    
    result = await trips_collection.update_one(
        {
            "_id": ObjectId(trip_id), 
            "status": models.TripStatusEnum.ACCEPTED.value,
            "driver_id": driver_id
        },
        {
            "$set": {
                "driver_id": "",  # Remove driver
                "status": models.TripStatusEnum.PENDING.value
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