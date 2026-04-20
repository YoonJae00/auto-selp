from passlib.context import CryptContext

# Argon2 알고리즘을 사용하도록 설정
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """비밀번호를 Argon2 알고리즘으로 해싱합니다."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해싱된 비밀번호를 비교합니다."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # 해싱되지 않은(평문) 비밀번호와 비교해야 하는 경우를 위한 예외 처리
        # 마이그레이션 도중이나 예기치 못한 상황에서 안전을 위해 False 반환
        return False

def is_hashed(password: str) -> bool:
    """문자열이 이미 해싱된 형태인지(Argon2 식별자 포함 여부) 확인합니다."""
    return password.startswith("$argon2id$")
