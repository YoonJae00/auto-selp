import os
import sys
import uuid
import base64
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet

# 프로젝트 루트를 python path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.database import Base
from src.api.models import User, UserSettings

# 백엔드와 동일한 암호화 키 생성 로직
def get_encryption_key():
    secret = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "default-secret-key")
    key = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key)

cipher = Fernet(get_encryption_key())

def encrypt_key(val: str) -> str:
    if not val: return ""
    return cipher.encrypt(val.strip().encode()).decode()

def setup():
    print(">>> [LOCAL SETUP] Starting environment initialization...", flush=True)
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print(">>> [LOCAL SETUP] SKIP: DATABASE_URL not found.", flush=True)
        return

    engine = create_engine(database_url)
    print(">>> [LOCAL SETUP] Ensuring tables exist...", flush=True)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1. Admin 유저 확인 또는 생성
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print(">>> [LOCAL SETUP] Creating default admin user...", flush=True)
            admin_user = User(
                username="admin",
                hashed_password="admin123",
                role="admin",
                is_profile_completed=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        
        # 2. UserSettings 확인 또는 생성
        settings = db.query(UserSettings).filter(UserSettings.user_id == admin_user.id).first()
        if not settings:
            settings = UserSettings(user_id=admin_user.id)
            db.add(settings)
            db.commit()
            db.refresh(settings)

        # 3. .env에서 API 키 가져오기 (정확한 필드명 매칭)
        # ApiKeys 모델 규격에 맞춤
        raw_keys = {
            "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
            "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
            "naver_api_key": os.environ.get("NAVER_API_KEY", ""),
            "naver_secret_key": os.environ.get("NAVER_SECRET_KEY", ""),
            "naver_client_secret": os.environ.get("NAVER_CLIENT_SECRET", ""),
            "naver_client_id": os.environ.get("NAVER_CLIENT_ID", ""),
            "naver_customer_id": os.environ.get("NAVER_CUSTOMER_ID", "")
        }
        
        # 값이 있는 것들만 암호화하여 준비
        encrypted_keys = {k: encrypt_key(v) for k, v in raw_keys.items() if v}
        
        if encrypted_keys:
            current_keys = dict(settings.api_keys) if settings.api_keys else {}
            current_keys.update(encrypted_keys)
            settings.api_keys = current_keys
            db.commit()
            print(f">>> [LOCAL SETUP] SUCCESS: Injected {len(encrypted_keys)} encrypted API keys into admin settings.", flush=True)
        else:
            print(">>> [LOCAL SETUP] WARNING: No API keys found in environment.", flush=True)

    except Exception as e:
        print(f">>> [LOCAL SETUP] ERROR: {e}", flush=True)
    finally:
        db.close()

if __name__ == "__main__":
    setup()
