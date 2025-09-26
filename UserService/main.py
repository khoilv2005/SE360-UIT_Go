from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

import crud
import models
import schemas
import auth
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
def get_service_info():
    return {"service": "UIT-Go User Service", "version": "1.0", "status": "running"}

# Authentication routes
@app.post("/auth/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/auth/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/logout")
async def logout_user(current_user: models.User = Depends(get_current_user)):
    # Với JWT, logout chủ yếu được xử lý ở client-side bằng cách xóa token
    # Server chỉ trả về thông báo thành công
    return {"message": f"User {current_user.email} logged out successfully"}

# Protected route example - Get current user info
@app.get("/users/me", response_model=schemas.User)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user

# Driver profile routes
@app.post("/drivers/profile", response_model=schemas.DriverProfile, status_code=status.HTTP_201_CREATED)
def create_driver_profile(driver_profile: schemas.DriverProfileCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != models.UserTypeEnum.DRIVER:
        raise HTTPException(status_code=403, detail="Only drivers can create driver profiles")
    return crud.create_driver_profile(db=db, driver_profile=driver_profile, user_id=current_user.user_id)

# Vehicle routes
@app.post("/drivers/vehicles", response_model=schemas.Vehicle, status_code=status.HTTP_201_CREATED)
def register_vehicle(vehicle: schemas.VehicleCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != models.UserTypeEnum.DRIVER:
        raise HTTPException(status_code=403, detail="Only drivers can register vehicles")
    return crud.create_vehicle(db=db, vehicle=vehicle, user_id=current_user.user_id)

