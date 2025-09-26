from sqlalchemy.orm import Session
import models
import schemas
import auth

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        full_name=user.full_name,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_driver_profile(db: Session, driver_profile: schemas.DriverProfileCreate, user_id: str):
    db_driver_profile = models.DriverProfile(
        user_id=user_id,
        license_num=driver_profile.license_num,
        birth=driver_profile.birth,
        card_num=driver_profile.card_num
    )
    db.add(db_driver_profile)
    db.commit()
    db.refresh(db_driver_profile)
    return db_driver_profile

def create_vehicle(db: Session, vehicle: schemas.VehicleCreate, user_id: str):
    db_vehicle = models.Vehicle(
        user_id=user_id,
        license_plate=vehicle.license_plate,
        seat_type=vehicle.seat_type
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

