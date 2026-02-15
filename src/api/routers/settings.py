from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.api.deps import get_current_user, get_db
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
async def get_settings(user=Depends(get_current_user)):
    """현재 사용자의 설정을 조회합니다."""
    supabase = get_db()
    
    # 사용자 설정 조회
    response = supabase.table("user_settings").select("*").eq("user_id", user.id).execute()
    
    if not response.data:
        # 설정이 없으면 기본값으로 생성
        default_settings = {
            "user_id": user.id,
            "excel_column_mapping": {
                "original_product_name": "A",
                "refined_product_name": "B",
                "keyword": "C",
                "category": "D"
            },
            "api_keys": {},
            "preferences": {}
        }
        insert_response = supabase.table("user_settings").insert(default_settings).execute()
        settings = insert_response.data[0]
    else:
        settings = response.data[0]
    
    # API 키 마스킹 처리
    settings["api_keys"] = mask_api_keys(settings.get("api_keys", {}))
    
    return settings

@router.put("/")
async def update_settings(
    settings_update: UserSettingsUpdate,
    user=Depends(get_current_user)
):
    """사용자 설정을 업데이트합니다."""
    supabase = get_db()
    
    # 기존 설정 조회
    response = supabase.table("user_settings").select("*").eq("user_id", user.id).execute()
    
    update_data = {}
    
    # 엑셀 컬럼 매핑 업데이트
    if settings_update.excel_column_mapping:
        update_data["excel_column_mapping"] = settings_update.excel_column_mapping.dict()
    
    # API 키 업데이트 (암호화)
    if settings_update.api_keys:
        encrypted_keys = encrypt_api_keys(settings_update.api_keys)
        # 기존 키와 병합 (부분 업데이트 지원)
        if response.data:
            existing_keys = response.data[0].get("api_keys", {})
            existing_keys.update(encrypted_keys)
            update_data["api_keys"] = existing_keys
        else:
            update_data["api_keys"] = encrypted_keys
    
    # 환경 설정 업데이트
    if settings_update.preferences:
        update_data["preferences"] = settings_update.preferences
    
    if not response.data:
        # 설정이 없으면 새로 생성
        update_data["user_id"] = user.id
        result = supabase.table("user_settings").insert(update_data).execute()
    else:
        # 기존 설정 업데이트
        result = supabase.table("user_settings").update(update_data).eq("user_id", user.id).execute()
    
    return {"message": "설정이 업데이트되었습니다.", "data": result.data[0] if result.data else None}

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
            
            client = OpenAI(api_key=api_key, http_client=http_client)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello, test connection"}],
                max_tokens=10
            )
            
            return {"success": True, "message": "OpenAI API 연결 성공"}
        except Exception as e:
            return {"success": False, "message": f"연결 실패: {str(e)}"}
    
    elif api_type == "naver_ad":
        # Naver 광고 API 테스트 (실제 API 호출은 생략, 키 형식만 검증)
        required_keys = ["naver_api_key", "naver_secret_key", "naver_customer_id"]
        if not all(k in api_credentials for k in required_keys):
            return {"success": False, "message": "필수 키가 누락되었습니다."}
        return {"success": True, "message": "Naver 광고 API 설정 완료"}
    
    elif api_type == "naver_search":
        # Naver 쇼핑 검색 API 테스트
        required_keys = ["naver_client_id", "naver_client_secret"]
        if not all(k in api_credentials for k in required_keys):
            return {"success": False, "message": "필수 키가 누락되었습니다."}
        return {"success": True, "message": "Naver 쇼핑 API 설정 완료"}
    
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 API 타입입니다.")

@router.get("/api-keys/decrypt/{key_name}")
async def get_decrypted_api_key(
    key_name: str,
    user=Depends(get_current_user)
):
    """
    특정 API 키를 복호화하여 반환합니다. (내부 처리용)
    보안상 주의해서 사용해야 합니다.
    """
    supabase = get_db()
    
    response = supabase.table("user_settings").select("api_keys").eq("user_id", user.id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="설정을 찾을 수 없습니다.")
    
    api_keys = response.data[0].get("api_keys", {})
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
