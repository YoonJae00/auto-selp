from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.api.database import get_db

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Supabase Auth (JWT) 검증 및 사용자 ID 반환.
    실제 검증은 Supabase Client가 하거나, 여기서 JWT 디코딩을 수행할 수 있음.
    여기서는 간단히 토큰 유무만 확인하고 Supabase의 getUser를 호출하는 방식 사용 권장.
    """
    token = credentials.credentials
    db = get_db()
    
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )

    try:
        # Supabase-py의 auth.get_user(token) 사용
        user = db.auth.get_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
