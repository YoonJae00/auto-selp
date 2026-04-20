import sys
import os
import uuid
from sqlalchemy.orm import Session

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.database import SessionLocal
from src.api.models import User
from src.api.auth_utils import hash_password, is_hashed

def migrate_passwords():
    """기존의 평문 비밀번호를 Argon2 해시로 마이그레이션합니다."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        total = len(users)
        migrated = 0
        skipped = 0
        
        print(f"Total users found: {total}")
        
        for user in users:
            # 이미 해싱된 경우 건너뛰기
            if is_hashed(user.hashed_password):
                skipped += 1
                continue
                
            # 평문 비밀번호 해싱
            plain_password = user.hashed_password
            user.hashed_password = hash_password(plain_password)
            migrated += 1
            
        db.commit()
        print(f"Successfully migrated {migrated} users.")
        print(f"Skipped {skipped} already hashed users.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting password migration to Argon2...")
    migrate_passwords()
    print("Migration finished.")
