from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from src.api.deps import get_current_user, get_db
from src.api.models import User, UserSettings
import os
import google.generativeai as genai
from cryptography.fernet import Fernet
import base64
import hashlib

router = APIRouter(prefix="/api/settings", tags=["settings"])

# 암호화 키 생성 (환경변수 기반)
# 실제 프로덕션에서는 안전한 키 관리 시스템 사용 권장
def get_encryption_key():
    # SECRET_KEY 환경변수를 기반으로 고정 키 생성
    secret = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "default-secret-key")
    # SHA256 해시를 사용하여 32바이트 키 생성
    key = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key)

cipher = Fernet(get_encryption_key())

# ─── Pydantic 모델 ─────────────────────────────────────────────

class ExcelColumnMapping(BaseModel):
    original_product_name: str = "A"
    refined_product_name: str = "B"
    keyword: str = "C"
    category: str = "D"
    coupang_category: Optional[str] = None

class ApiKeys(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    naver_api_key: Optional[str] = None
    naver_secret_key: Optional[str] = None
    naver_customer_id: Optional[str] = None
    naver_client_id: Optional[str] = None
    naver_client_secret: Optional[str] = None
    nano_banana_api_key: Optional[str] = None

class UserSettingsUpdate(BaseModel):
    excel_column_mapping: Optional[ExcelColumnMapping] = None
    api_keys: Optional[ApiKeys] = None
    preferences: Optional[Dict[str, Any]] = None  # llm_provider 등 저장

class UserSettingsResponse(BaseModel):
    id: str
    user_id: str
    excel_column_mapping: Dict[str, str]
    api_keys: Dict[str, str]  # API 키는 마스킹되어 반환
    preferences: Dict[str, Any]
    created_at: str
    updated_at: str

# ─── 헬퍼 함수 ─────────────────────────────────────────────

def encrypt_api_key(api_key: str) -> str:
    """API 키를 암호화합니다."""
    if not api_key or not api_key.strip():
        return ""
    try:
        # 공백 제거
        clean_key = api_key.strip()
        # ASCII 검증
        try:
            clean_key.encode('ascii')
        except UnicodeEncodeError:
            print(f"[WARNING] API 키에 비-ASCII 문자 포함, 제거합니다.")
            clean_key = ''.join(char for char in clean_key if ord(char) < 128).strip()
            if not clean_key:
                print(f"[ERROR] API 키 정제 후 빈 문자열")
                return ""
        
        return cipher.encrypt(clean_key.encode()).decode()
    except Exception as e:
        print(f"[ERROR] API 키 암호화 실패: {e}")
        return ""

def decrypt_api_key(encrypted_key: str) -> str:
    """암호화된 API 키를 복호화합니다."""
    if not encrypted_key:
        return ""
    try:
        return cipher.decrypt(encrypted_key.encode()).decode()
    except Exception:
        return ""

def mask_api_key(api_key: str) -> str:
    """API 키를 마스킹 처리합니다. (프론트엔드 표시용)"""
    if not api_key or len(api_key) < 8:
        return "••••••••"
    return api_key[:4] + "••••••••" + api_key[-4:]

def encrypt_api_keys(api_keys: ApiKeys) -> Dict[str, str]:
    """모든 API 키를 암호화합니다."""
    encrypted = {}
    for key, value in api_keys.dict(exclude_none=True).items():
        if value and value.strip():  # 빈 문자열 필터링
            encrypted_value = encrypt_api_key(value)
            if encrypted_value:  # 암호화 성공한 것만 추가
                encrypted[key] = encrypted_value
                print(f"[INFO] API 키 암호화 성공: {key}")
            else:
                print(f"[WARNING] API 키 암호화 실패: {key}")
    return encrypted

def mask_api_keys(encrypted_keys: Dict[str, str]) -> Dict[str, str]:
    """모든 암호화된 API 키를 마스킹 처리합니다."""
    masked = {}
    for key, encrypted_value in encrypted_keys.items():
        if encrypted_value:
            # 복호화하지 않고 마스킹만 표시
            masked[key] = "••••••••"
    return masked

# ─── API 엔드포인트 ─────────────────────────────────────────────

@router.get("/", response_model=UserSettingsResponse)
async def get_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """현재 사용자의 설정을 조회합니다."""
    
    settings_db = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    
    if not settings_db:
        # 설정이 없으면 기본값으로 생성
        settings_db = UserSettings(user_id=user.id)
        db.add(settings_db)
        db.commit()
        db.refresh(settings_db)
        
    settings = {
        "id": str(settings_db.id),
        "user_id": str(settings_db.user_id),
        "excel_column_mapping": settings_db.excel_column_mapping or {
            "original_product_name": "A",
            "refined_product_name": "B",
            "keyword": "C",
            "category": "D"
        },
        "api_keys": settings_db.api_keys or {},
        "preferences": settings_db.preferences or {},
        "created_at": settings_db.created_at.isoformat() if settings_db.created_at else "",
        "updated_at": settings_db.updated_at.isoformat() if settings_db.updated_at else ""
    }
    
    # API 키 마스킹 처리
    settings["api_keys"] = mask_api_keys(settings.get("api_keys", {}))
    
    return settings

@router.put("/")
async def update_settings(
    settings_update: UserSettingsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 설정을 업데이트합니다."""
    
    settings_db = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings_db:
        settings_db = UserSettings(user_id=user.id)
        db.add(settings_db)
    
    # 엑셀 컬럼 매핑 업데이트
    if settings_update.excel_column_mapping:
        settings_db.excel_column_mapping = settings_update.excel_column_mapping.dict()
    
    # API 키 업데이트 (암호화)
    if settings_update.api_keys:
        encrypted_keys = encrypt_api_keys(settings_update.api_keys)
        # 기존 키와 병합 (부분 업데이트 지원)
        existing_keys = dict(settings_db.api_keys) if settings_db.api_keys else {}
        existing_keys.update(encrypted_keys)
        settings_db.api_keys = existing_keys
    
    # 환경 설정 업데이트
    if settings_update.preferences:
        settings_db.preferences = settings_update.preferences
    
    db.commit()
    db.refresh(settings_db)
    
    response_data = {
        "id": str(settings_db.id),
        "user_id": str(settings_db.user_id),
        "excel_column_mapping": settings_db.excel_column_mapping,
        "api_keys": settings_db.api_keys,
        "preferences": settings_db.preferences,
        "created_at": settings_db.created_at.isoformat() if settings_db.created_at else "",
        "updated_at": settings_db.updated_at.isoformat() if settings_db.updated_at else ""
    }
    
    return {"message": "설정이 업데이트되었습니다.", "data": response_data}

@router.post("/test-api/{api_type}")
async def test_api_connection(
    api_type: str,
    api_credentials: Dict[str, str] = Body(...),
    user=Depends(get_current_user)
):
    """
    API 연결을 테스트합니다.
    
    지원하는 api_type:
    - gemini: Gemini API
    - openai: OpenAI API
    - naver_ad: Naver 광고 API
    - naver_search: Naver 쇼핑 검색 API
    """
    
    if api_type == "gemini":
        try:
            api_key = api_credentials.get("gemini_api_key")
            if not api_key:
                raise HTTPException(status_code=400, detail="API 키가 필요합니다.")
            
            # Gemini API 테스트
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content("Hello, test connection")
            
            return {"success": True, "message": "Gemini API 연결 성공"}
        except Exception as e:
            return {"success": False, "message": f"연결 실패: {str(e)}"}
    
    elif api_type == "openai":
        try:
            api_key = api_credentials.get("openai_api_key")
            if not api_key:
                raise HTTPException(status_code=400, detail="API 키가 필요합니다.")
            
            # API Key 정제 (비-ASCII 문자 제거)
            api_key = api_key.strip()
            try:
                api_key.encode('ascii')
            except UnicodeEncodeError:
                print(f"[WARNING] 테스트용 API 키에 비-ASCII 문자 포함, 제거합니다.")
                api_key = ''.join(char for char in api_key if ord(char) < 128).strip()
                if not api_key:
                    raise HTTPException(status_code=400, detail="유효한 API 키가 아닙니다.")
            
            # OpenAI API 테스트
            from openai import OpenAI
            import httpx
            
            http_client = httpx.Client(
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=10.0
            )
            
            client = OpenAI(api_key=api_key, http_client=http_client)            # 테스트 요청
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_completion_tokens=50
            )
            
            return {"success": True, "message": "OpenAI API 연결 성공"}
        except Exception as e:
            return {"success": False, "message": f"연결 실패: {str(e)}"}
    
    elif api_type == "naver_ad":
        api_key = api_credentials.get("naver_api_key")
        secret_key = api_credentials.get("naver_secret_key")
        customer_id = api_credentials.get("naver_customer_id")
        if not api_key or not secret_key or not customer_id:
            raise HTTPException(status_code=400, detail="필수 키가 누락되었습니다.")
        
        try:
            import time
            import hmac
            import hashlib
            import base64
            import httpx
            
            method = 'GET'
            uri = '/keywordstool'
            timestamp = str(round(time.time() * 1000))
            message = f"{timestamp}.{method}.{uri}"
            hash_val = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
            signature = base64.b64encode(hash_val.digest()).decode()
            
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "X-Timestamp": timestamp,
                "X-API-KEY": api_key,
                "X-Customer": customer_id,
                "X-Signature": signature
            }
            params = {'hintKeywords': '테스트', 'showDetail': '1'}
            url = f"https://api.naver.com{uri}"
            
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    return {"success": True, "message": "Naver 광고 API 연결 성공"}
                else:
                    return {"success": False, "message": f"연결 실패: {response.text}"}
        except Exception as e:
            return {"success": False, "message": f"연결 실패: {str(e)}"}
    
    elif api_type == "naver_search":
        client_id = api_credentials.get("naver_client_id")
        client_secret = api_credentials.get("naver_client_secret")
        if not client_id or not client_secret:
            raise HTTPException(status_code=400, detail="필수 키가 누락되었습니다.")
        
        try:
            import httpx
            url = "https://openapi.naver.com/v1/search/shop.json"
            headers = {
                "X-Naver-Client-Id": client_id,
                "X-Naver-Client-Secret": client_secret
            }
            params = {"query": "테스트", "display": 1}
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    return {"success": True, "message": "Naver 쇼핑 API 연결 성공"}
                else:
                    return {"success": False, "message": f"연결 실패: {response.text}"}
        except Exception as e:
            return {"success": False, "message": f"연결 실패: {str(e)}"}

    elif api_type == "coupang":
        access_key = api_credentials.get("coupang_access_key")
        secret_key = api_credentials.get("coupang_secret_key")
        if not access_key or not secret_key:
            raise HTTPException(status_code=400, detail="필수 키가 누락되었습니다.")
        
        try:
            import httpx
            import hmac
            import hashlib
            from datetime import datetime
            
            method = "POST"
            path = "/v2/providers/openapi/apis/api/v1/categorization/predict"
            url = f"https://api-gateway.coupang.com{path}"
            
            datetime_str = datetime.utcnow().strftime('%y%m%dT%H%M%SZ')
            message = datetime_str + method + path
            
            signature = hmac.new(
                secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            authorization = f"CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={datetime_str}, signature={signature}"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": authorization
            }
            body = {
                "productName": "테스트 상품",
                "brand": "",
                "attributes": {}
            }
            
            with httpx.Client(timeout=5.0) as client:
                response = client.post(url, headers=headers, json=body)
                if response.status_code == 200:
                    return {"success": True, "message": "Coupang API 연결 성공"}
                else:
                    return {"success": False, "message": f"연결 실패: {response.text}"}
        except Exception as e:
            return {"success": False, "message": f"연결 실패: {str(e)}"}
    
    elif api_type == "nano_banana":
        # Nano banana API는 선택이므로 기본적으로 연결 성공 반환 (추후 실제 검증 로직 추가)
        return {"success": True, "message": "Nano Banana API 설정 완료"}

    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 API 타입입니다.")

@router.get("/api-keys/decrypt/{key_name}")
async def get_decrypted_api_key(
    key_name: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 API 키를 복호화하여 반환합니다. (내부 처리용)
    보안상 주의해서 사용해야 합니다.
    """
    settings_db = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    
    if not settings_db:
        raise HTTPException(status_code=404, detail="설정을 찾을 수 없습니다.")
    
    api_keys = settings_db.api_keys or {}
    encrypted_key = api_keys.get(key_name)
    
    if not encrypted_key:
        # 환경변수 폴백
        env_key_map = {
            "gemini_api_key": "GEMINI_API_KEY",
            "openai_api_key": "OPENAI_API_KEY",
            "naver_api_key": "NAVER_API_KEY",
            "naver_secret_key": "NAVER_SECRET_KEY",
            "naver_customer_id": "NAVER_CUSTOMER_ID",
            "naver_client_id": "NAVER_CLIENT_ID",
            "naver_client_secret": "NAVER_CLIENT_SECRET",
        }
        env_var = env_key_map.get(key_name)
        if env_var:
            return {"key": os.getenv(env_var, "")}
        raise HTTPException(status_code=404, detail="API 키를 찾을 수 없습니다.")
    
    decrypted_key = decrypt_api_key(encrypted_key)
    return {"key": decrypted_key}
