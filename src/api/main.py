from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from src.api.database import engine, Base, SessionLocal
from src.api.models import User, Prompt, Job, UserSettings

# 데이터베이스 테이블 생성 (개발 환경용)
Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    try:
        # 유저가 한 명도 없는지 확인
        if db.query(User).count() == 0:
            print("No users found. Creating default admin user...")
            admin_user = User(
                username="admin",
                hashed_password="admin123", # 현재 프로젝트는 평문 비교 중
                role="admin",
                is_profile_completed=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # 기본 설정 추가
            settings = UserSettings(user_id=admin_user.id)
            db.add(settings)
            db.commit()
            print("Default admin user (admin / admin123) created successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

init_db()

app = FastAPI(title="Auto-Selp API", version="1.0.0")

# CORS Setup
origins = [
    "http://localhost:3000", # React Frontend
    "http://localhost:5173", # Vite Default
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Auto-Selp API"}

from src.api.routers import jobs, prompts, settings, auth

app.include_router(jobs.router)
app.include_router(prompts.router)
app.include_router(settings.router)
app.include_router(auth.router)
