import hmac
import hashlib
import requests
import json
import time
import os
from datetime import datetime
from urllib.parse import urlparse

class CoupangCategoryProcessor:
    def __init__(self, access_key: str, secret_key: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = "https://api-gateway.coupang.com"

    def _generate_signature(self, method, path, query=""):
        datetime_str = datetime.utcnow().strftime('%y%m%dT%H%M%SZ')
        message = datetime_str + method + path + (query if query else "")
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return f"CEA algorithm=HmacSHA256, access-key={self.access_key}, signed-date={datetime_str}, signature={signature}"

    def get_category_code(self, product_name: str, brand: str = "", attributes: dict = None) -> str:
        """
        쿠팡 카테고리 추천 API를 호출하여 최적의 카테고리 코드를 반환합니다.
        
        Args:
            product_name: 상품명
            brand: (옵션) 브랜드
            attributes: (옵션) 상품 속성 딕셔너리
            
        Returns:
            str: 추천 카테고리 코드 (실패 시 에러 메시지 또는 "매칭실패")
        """
        path = "/v2/providers/openapi/apis/api/v1/categorization/predict"
        url = f"{self.base_url}{path}"
        
        # Request Body
        body = {
            "productName": product_name,
            "brand": brand,
            "attributes": attributes if attributes else {}
        }
        
        # Authentication
        authorization = self._generate_signature("POST", path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization
        }
        
        try:
            response = requests.post(url, headers=headers, json=body, timeout=5)
            # print(f"[DEBUG] Coupang Response: {response.status_code} {response.text}") 
            # Uncommenting above for more debug if needed, but error handling below should catch it.
            if response.status_code != 200:
                 print(f"[ERROR] Coupang API Failed: {response.status_code} {response.text}")
            response.raise_for_status()
            
            data = response.json()
            if data['code'] == 200 and data['data']['autoCategorizationPredictionResultType'] == 'SUCCESS':
                return data['data']['predictedCategoryId']
            else:
                return f"매칭실패({data.get('message', 'Unknown Error')})"
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Coupang API Error: {e}")
            return f"API오류"
        except Exception as e:
            print(f"[ERROR] Coupang Processing Error: {e}")
            return f"처리실패"
