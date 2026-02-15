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
            # 엑셀 파일 로드 (파일명: naver_category_mapping.xls)
            # 컬럼: 카테고리번호, 대분류, 중분류, 소분류, 세분류
            df = pd.read_excel(self.mapping_file_path)
            
            mapping = {}
            for _, row in df.iterrows():
                # 각 분류 컬럼을 가져와서 깨끗하게 정리
                parts = []
                for col in ['대분류', '중분류', '소분류', '세분류']:
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip():
                        parts.append(str(val).strip())
                
                if parts:
                    full_path = ">".join(parts)
                    # 카테고리번호는 숫자인 경우가 많으므로 문자로 변환
                    code = str(row.get('카테고리번호', '')).strip()
                    if code:
                        mapping[full_path] = code
            
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
            return "매핑실패(검색불가)"
            
        # 2. 매핑 테이블에서 코드 찾기
        # naver_cat 예: "디지털/가전>휴대폰악세서리>휴대폰케이스>아이폰케이스"
        
        # 완전 일치 시도
        if naver_cat in self.category_mapping:
            return self.category_mapping[naver_cat]
            
        # 부분 일치 시도 (세분류부터 역순으로 시도하거나, 혹은 포함 여부 확인)
        # 하지만 엑셀 매핑이 정확하다면 full path가 일치해야 하는 것이 원칙입니다.
        # 예외적으로 네이버 API가 주는 카테고리 명칭과 엑셀의 명칭이 미세하게 다를 수 있으므로
        # 가장 마지막 카테고리(세분류)가 일치하는 것을 찾습니다.
        
        target_last_cat = naver_cat.split(">")[-1].strip()
        
        for path, code in self.category_mapping.items():
            path_last_cat = path.split(">")[-1].strip()
            if path_last_cat == target_last_cat:
                 # 주의: 마지막 카테고리명이 중복될 수 있음 (예: '기타'). 
                 # 이 경우 상위 카테고리까지 비교하면 좋겠지만, 
                 # 일단은 단순화하여 마지막이 같으면 반환하거나, 
                 # 혹은 '확인필요'로 넘길 수 있습니다.
                 return code

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
