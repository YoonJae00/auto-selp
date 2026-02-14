import os
import time
import requests
import hashlib
import hmac
import base64
from typing import List
from curl_cffi import requests as cffi_requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class KeywordProcessor:
    def __init__(self):
        # Naver Config
        self.naver_base_url = os.getenv("NAVER_API_BASE_URL", "https://api.naver.com")
        self.naver_api_key = os.getenv("NAVER_API_KEY")
        self.naver_secret_key = os.getenv("NAVER_SECRET_KEY")
        self.naver_customer_id = os.getenv("NAVER_CUSTOMER_ID")
        
        # Gemini Config
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            print("[WARNING] GEMINI_API_KEY not found in .env")

    def process_keywords(self, product_name: str) -> str:
        """
        통합 프로세스:
        1. 쿠팡/네이버 API로 연관 키워드 수집 (Seed)
        2. Gemini로 소상공인 맞춤 필터링 (Filter)
        3. 최종 키워드 문자열 반환 (콤마 구분)
        """
        # Step 1: Seed Collection
        seed_keywords = self._collect_seed_keywords(product_name)
        if not seed_keywords:
            return ""
            
        # Step 2: Filtering with LLM
        filtered_keywords = self._filter_keywords_with_gemini(product_name, seed_keywords)
        
        return ", ".join(filtered_keywords)

    def _collect_seed_keywords(self, keyword: str) -> List[str]:
        """쿠팡 + 네이버 API를 통해 후보 키워드 수집"""
        coupang_keywords = self._get_coupang_related_keywords(keyword)
        naver_keywords = self._get_naver_api_keywords(keyword)
        
        # 중복 제거
        all_keywords = list(set(coupang_keywords + naver_keywords))
        print(f"총 {len(all_keywords)}개의 후보 키워드 수집됨.")
        return all_keywords

    def _filter_keywords_with_gemini(self, product_name: str, keywords: List[str]) -> List[str]:
        """Gemini를 이용하여 경쟁력 있는 키워드만 선별"""
        if not self.gemini_api_key or not keywords:
            return keywords[:5] # Fallback

        try:
            keywords_str = ", ".join(keywords)
            prompt = f"""
            역할: 스마트스토어/쿠팡 전문 마케터
            작업: 주어진 '후보 키워드 리스트'에서 소상공인 셀러가 판매하기 유리한 '알짜배기 키워드' 5~8개를 선별해주세요.

            상품명: {product_name}

            [필수 제거 조건] - 위반 시 절대 안됨
            1. **상표권/대형 브랜드** 포함된 키워드 무조건 삭제 (예: 삼성, LG, 다이소, 이케아, 3M, 시즈맥스, 나이키 등).
            2. 너무 광범위하고 경쟁이 치열한 '대형 키워드' 삭제 (예: 그냥 '의자', '책상', '수납함' 같은 단일 명사).
            3. 상품과 관련 없는 키워드 삭제.

            [선호 조건]
            1. **세부 키워드(Long-tail)** 우선 (예: '투명 화장품 정리함', '원룸 책상 꾸미기').
            2. 구매 전환율이 높을 것 같은 구체적인 키워드.

            후보 키워드 리스트: [{keywords_str}]

            결과 출력 형식:
            키워드1, 키워드2, 키워드3, ... (콤마로만 구분하여 출력, 설명 없이)
            """
            
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # 후처리: 콤마로 분리 및 공백 제거
            filtered = [k.strip() for k in result.split(',') if k.strip()]
            print(f"Gemini가 선별한 키워드({len(filtered)}개): {filtered}")
            return filtered

        except Exception as e:
            print(f"Gemini 키워드 필터링 중 오류: {e}")
            return keywords[:5]

    def _get_coupang_related_keywords(self, keyword: str) -> List[str]:
        # (기존 로직 유지)
        try:
            base_url = "https://www.coupang.com/n-api/web-adapter/search"
            params = {"keyword": keyword}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }
            res = cffi_requests.get(base_url, params=params, headers=headers, impersonate="chrome124")
            if res.status_code != 200: return []
            data = res.json()
            return [item.get("keyword") for item in data if item.get("keyword")]
        except:
            return []

    def _get_naver_api_keywords(self, keyword: str) -> List[str]:
        # (기존 로직 유지)
        if not (self.naver_api_key and self.naver_secret_key): return []
        try:
            uri = '/keywordstool'
            method = 'GET'
            params = {'hintKeywords': keyword, 'showDetail': '1'}
            headers = self._get_naver_header(method, uri)
            resp = requests.get(self.naver_base_url + uri, params=params, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [item.get('relKeyword') for item in data.get('keywordList', []) if item.get('relKeyword')]
            return []
        except:
            return []

    def _get_naver_header(self, method, uri):
        timestamp = str(round(time.time() * 1000))
        message = f"{timestamp}.{method}.{uri}"
        secret_key = self.naver_secret_key
        hash = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
        signature = base64.b64encode(hash.digest()).decode()
        return {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Timestamp": timestamp,
            "X-API-KEY": self.naver_api_key,
            "X-Customer": self.naver_customer_id,
            "X-Signature": signature
        }

if __name__ == "__main__":
    # Test
    kp = KeywordProcessor()
    print(kp.process_keywords("원룸 미니 건조대"))
