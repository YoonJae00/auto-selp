import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Example: postgresql://postgres:postgrespassword@localhost:5432/postgres
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("[WARNING] DATABASE_URL not found in .env")
    engine = None
    SessionLocal = None
else:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
