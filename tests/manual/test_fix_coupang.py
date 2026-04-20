import os
import sys
import hmac
import hashlib
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Hardcoded for test based on previous .env view (which had Coupang keys)
# Note: In a real scenario I should read them from .env, but I saw them earlier.
ACCESS_KEY = os.getenv("Coupang_Access_Key")
SECRET_KEY = os.getenv("Coupang_Secret_Key")

def generate_signature(method, path, secret_key, access_key, query=""):
    datetime_str = datetime.utcnow().strftime('%y%m%dT%H%M%SZ')
    message = datetime_str + method + path + (query if query else "")
    
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return f"CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={datetime_str}, signature={signature}"

def test_coupang_api():
    print("Testing Coupang API...")
    if not ACCESS_KEY or not SECRET_KEY:
        print("Coupang keys missing in .env")
        return

    base_url = "https://api-gateway.coupang.com"
    path = "/v2/providers/openapi/apis/api/v1/categorization/predict"
    url = f"{base_url}{path}"
    
    body = {
        "productName": "페디큐어 손가락 발가락 분리대",
        "brand": "",
        "attributes": {}
    }
    
    authorization = generate_signature("POST", path, SECRET_KEY, ACCESS_KEY)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization
    }
    
    print(f"Requesting URL: {url}")
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_coupang_api()
