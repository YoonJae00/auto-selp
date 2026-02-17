"""
사용자 설정 유틸리티
- Supabase에서 사용자 설정을 조회하고 캐시
- API 키 복호화 기능 제공
"""
from typing import Optional, Dict
import os
from cryptography.fernet import Fernet
import base64
import hashlib

def get_encryption_key():
    """암호화 키 생성 (settings.py와 동일한 로직)"""
    secret = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "default-secret-key")
    key = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key)

cipher = Fernet(get_encryption_key())

def decrypt_api_key(encrypted_key: str) -> str:
    """암호화된 API 키를 복호화합니다."""
    if not encrypted_key:
        return ""
    try:
        decrypted = cipher.decrypt(encrypted_key.encode()).decode()
        
        # 복호화 결과 검증
        print(f"[DEBUG] 복호화 성공: 원본 길이={len(encrypted_key)}, 복호화 후 길이={len(decrypted)}")
        print(f"[DEBUG] 복호화된 키 앞부분: {decrypted[:10] if len(decrypted) >= 10 else decrypted}...")
        
        # ASCII 검증
        try:
            decrypted.encode('ascii')
            print(f"[DEBUG] ASCII 검증 통과")
        except UnicodeEncodeError as e:
            print(f"[WARNING] 복호화된 API 키에 비-ASCII 문자 포함: {e}")
            print(f"[DEBUG] 원본 repr: {repr(decrypted)}")
            # 비-ASCII 문자 제거
            decrypted = ''.join(char for char in decrypted if ord(char) < 128).strip()
            print(f"[INFO] 비-ASCII 문자 제거 후: {decrypted[:10]}...")
        
        return decrypted
    except Exception as e:
        print(f"[ERROR] API 키 복호화 실패: {e}")
        return ""

def get_user_setting(supabase, user_id: str, setting_key: str) -> Optional[any]:
    """
    사용자 설정에서 특정 키의 값을 가져옵니다.
    
    Args:
        supabase: Supabase 클라이언트
        user_id: 사용자 ID
        setting_key: 설정 키 (예: 'excel_column_mapping', 'api_keys')
    
    Returns:
        설정 값 또는 None
    """
    try:
        response = supabase.table("user_settings").select(setting_key).eq("user_id", user_id).execute()
        if response.data:
            return response.data[0].get(setting_key)
        return None
    except Exception as e:
        print(f"설정 조회 중 오류: {e}")
        return None

def get_user_api_key(supabase, user_id: str, key_name: str) -> str:
    """
    사용자의 특정 API 키를 복호화하여 반환합니다.
    설정에 없으면 환경변수에서 폴백합니다.
    
    Args:
        supabase: Supabase 클라이언트
        user_id: 사용자 ID
        key_name: API 키 이름 (예: 'gemini_api_key')
    
    Returns:
        복호화된 API 키 또는 환경변수 값
    """
    # 환경변수 매핑
    env_key_map = {
        "gemini_api_key": "GEMINI_API_KEY",
        "openai_api_key": "OPENAI_API_KEY",
        "naver_api_key": "NAVER_API_KEY",
        "naver_secret_key": "NAVER_SECRET_KEY",
        "naver_customer_id": "NAVER_CUSTOMER_ID",
        "naver_client_id": "NAVER_CLIENT_ID",
        "naver_client_secret": "NAVER_CLIENT_SECRET",
        "nano_banana_api_key": "NANO_BANANA_API_KEY",
        "coupang_access_key": "Coupang_Access_Key",
        "coupang_secret_key": "Coupang_Secret_Key",
    }
    
    # 사용자 설정에서 조회
    api_keys = get_user_setting(supabase, user_id, "api_keys")
    if api_keys and key_name in api_keys:
        encrypted = api_keys[key_name]
        decrypted = decrypt_api_key(encrypted)
        if decrypted:
            return decrypted
    
    # 폴백: 환경변수
    env_var = env_key_map.get(key_name)
    if env_var:
        val = os.getenv(env_var, "")
        if val: return val
    
    return ""

def get_excel_column_mapping(supabase, user_id: str) -> Dict[str, str]:
    """
    사용자의 엑셀 컬럼 매핑을 반환합니다.
    설정에 없으면 기본값을 반환합니다.
    
    Returns:
        Dict: {
            'original_product_name': 'A',
            'refined_product_name': 'B',
            'keyword': 'C',
            'category': 'D'
        }
    """
    default_mapping = {
        "original_product_name": "A",
        "refined_product_name": "B",
        "keyword": "C",
        "category": "D"
    }
    
    mapping = get_user_setting(supabase, user_id, "excel_column_mapping")
    return mapping if mapping else default_mapping
