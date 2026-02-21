from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
import os

from src.api.database import get_db
from src.api.models import User, UserSettings
from src.api.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "auto-selp-super-secret-dev-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

ADMIN_SECRET_CODE = "elwlslfosem7!"

class LoginRequest(BaseModel):
    username: str
    password: str

class AdminCodeRequest(BaseModel):
    admin_code: str

class RegisterAdminRequest(BaseModel):
    username: str
    password: str

class RegisterUserRequest(BaseModel):
    username: str
    password: str

class UpdateProfileRequest(BaseModel):
    email: str
    name: str
    phone: str

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
    req_username = request.username.strip()
    req_password = request.password.strip()

    user = db.query(User).filter(User.username == req_username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"존재하지 않는 아이디입니다. (입력창에 공백이 없는지 확인해주세요)"
        )
    
    # In a real app we would use hashed passwords, but using string comparison for simplicity as before
    if user.hashed_password != req_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 일치하지 않습니다."
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": {
            "id": str(user.id), 
            "username": user.username,
            "role": user.role,
            "is_profile_completed": user.is_profile_completed
        }
    }

@router.post("/verify-admin-code")
def verify_admin_code(request: AdminCodeRequest):
    if request.admin_code != ADMIN_SECRET_CODE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 코드가 일치하지 않습니다."
        )
    return {"success": True}

@router.post("/register-admin")
def register_admin(request: RegisterAdminRequest, db: Session = Depends(get_db)):
    req_username = request.username.strip()
    req_password = request.password.strip()

    # Check if a user with the username already exists
    existing_user = db.query(User).filter(User.username == req_username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 아이디입니다."
        )
        
    user = User(
        username=req_username, 
        hashed_password=req_password,
        role="admin",
        is_profile_completed=True # Admins skip the regular profile setup
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default settings
    settings = UserSettings(user_id=user.id)
    db.add(settings)
    db.commit()
    
    return {"success": True, "user_id": str(user.id)}

@router.post("/register-user")
def register_user(request: RegisterUserRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
        
    req_username = request.username.strip()
    req_password = request.password.strip()

    # Check if user already exists
    existing_user = db.query(User).filter(User.username == req_username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 아이디입니다."
        )
        
    user = User(
        username=req_username, 
        hashed_password=req_password,
        role="user",
        is_profile_completed=False # Needs to complete profile upon first login
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default settings
    settings = UserSettings(user_id=user.id)
    db.add(settings)
    db.commit()
    
    return {"success": True, "user_id": str(user.id), "username": user.username}

@router.post("/update-profile")
def update_profile(request: UpdateProfileRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.email = request.email
    current_user.name = request.name
    current_user.phone = request.phone
    current_user.is_profile_completed = True
    
    db.commit()
    db.refresh(current_user)
    
    return {"success": True}
