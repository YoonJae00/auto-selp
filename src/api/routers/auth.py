from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
import os

from src.api.database import get_db
from src.api.models import User, UserSettings

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "auto-selp-super-secret-dev-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

class LoginRequest(BaseModel):
    email: str
    password: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Very simple authentication for this private tool
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Create the user on first login if not exists (simplifying setup)
        user = User(email=request.email, hashed_password=request.password)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create default settings
        settings = UserSettings(user_id=user.id)
        db.add(settings)
        db.commit()
    else:
        # Verify password (using simple string comparison since we don't have passlib installed for simple setup)
        if user.hashed_password != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": str(user.id), "email": user.email}}
