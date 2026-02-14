import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class CategoryProcessor:
    def __init__(self, mapping_file_path: str = "mapping.xlsx"):
        self.naver_client_id = os.getenv("NAVER_API_KEY") # 검색 API ID (Client ID)
        self.naver_client_secret = os.getenv("NAVER_SECRET_KEY") # 검색 API Secret
        
        # 주의: 검색광고 API 키와 쇼핑 검색(Search) API 키는 다를 수 있음.
        # 여기서는 .env에 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET이 있다고 가정하거나
        # 기존 키를 혼용해서 쓸 경우 헤더 설정을 맞춰야 함.
        # User Provided Code uses X-Naver-Client-Id header, which implies Naver Search API (Developers).
        # We need to ensure .env has these.
        
        self.mapping_file_path = mapping_file_path
        self.category_mapping = self._load_mapping_file()

    def _load_mapping_file(self):
        """매핑 엑셀 파일을 로드하여 딕셔너리로 변환"""
        if not os.path.exists(self.mapping_file_path):
            print(f"[WARNING] 매핑 파일이 없습니다: {self.mapping_file_path}")
            return {}
            
        try:
            # A열: 네이버 카테고리명, B열: 내 코드 라고 가정
            df = pd.read_excel(self.mapping_file_path, header=0)
            mapping = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
            print(f"카테고리 매핑 {len(mapping)}개 로드 완료")
            return mapping
        except Exception as e:
            print(f"매핑 파일 로드 실패: {e}")
            return {}

    def get_category_code(self, product_name: str) -> str:
        """상품명을 기반으로 코드 반환"""
        # 1. 네이버 쇼핑 API로 카테고리 찾기
        naver_cat = self._search_naver_category(product_name)
        if not naver_cat:
            return "매핑실패"
            
        # 2. 매핑 테이블에서 코드 찾기
        # 전체 일치
        if naver_cat in self.category_mapping:
            return str(self.category_mapping[naver_cat])
            
        # 부분 일치 (마지막 깊이 카테고리만 비교)
        last_cat = naver_cat.split(">")[-1].strip()
        for k, v in self.category_mapping.items():
            if str(k).endswith(last_cat):
                return str(v)
                
        return f"확인필요({naver_cat})"

    def _search_naver_category(self, query: str) -> str:
        """네이버 검색 API (쇼핑) 호출"""
        url = "https://openapi.naver.com/v1/search/shop.json"
        
        # Search API requires Client ID/Secret, distinct from Ad API.
        # Using ENV vars or placeholders if missing.
        headers = {
            "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID", ""),
            "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET", "")
        }
        
        if not headers["X-Naver-Client-Id"]:
            return ""

        try:
            res = requests.get(url, headers=headers, params={"query": query, "display": 1}, timeout=5)
            if res.status_code == 200:
                items = res.json().get("items")
                if items:
                    item = items[0]
                    cats = [item.get(f"category{i}") for i in range(1, 5)]
                    return ">".join([c for c in cats if c])
            return ""
        except:
            return ""
