#!/usr/bin/env python3
"""
상품명 리스트를 입력받아 상품명 가공, 키워드 추출, 카테고리 매핑을 테스트하는 스크립트 (Mocking 적용)
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv
import pandas as pd

# 프로젝트 루트 경로 추가 (tests/unit/ 위치 고려)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.processors.product_name_processor import ProductNameProcessor
from src.processors.keyword_processor import KeywordProcessor
from src.processors.category_processor import CategoryProcessor

# 테스트할 상품명 리스트
SAMPLE_PRODUCT_NAMES = [
    "[시즈맥스] 3단 미니미 소품함 1p (정리함)",
    "브랜드명 좋은 의자 10p"
]

def test_processors_with_mocks():
    """3가지 프로세서를 Mock을 사용하여 안전하게 테스트"""
    
    # 1. LLM Provider Mock 설정
    mock_llm = MagicMock()
    mock_llm.is_configured.return_value = True
    # 여러 번 호출되므로 side_effect로 대응
    def mock_generate(prompt):
        if "Refine product name" in prompt:
            return "정제된 상품명"
        if "동의어" in prompt or "변형" in prompt:
            return "변형1, 변형2"
        if "큐레이션" in prompt or "키워드" in prompt:
            return "키워드1, 키워드2, 키워드3"
        return "응답"
    
    mock_llm.generate_content.side_effect = mock_generate

    # 2. 내부 메서드 및 네트워크 Mock 설정
    with patch('src.processors.category_processor.requests.get') as mock_cat_get, \
         patch('src.processors.keyword_processor.KeywordProcessor._search_naver_keywords_with_data') as mock_kw_naver, \
         patch('src.processors.keyword_processor.KeywordProcessor._get_coupang_related_keywords') as mock_kw_coupang:
        
        # 네이버 쇼핑 검색 결과 Mock (CategoryProcessor용)
        mock_cat_resp = MagicMock()
        mock_cat_resp.status_code = 200
        mock_cat_resp.json.return_value = {
            "items": [{"category1": "생활", "category2": "가구", "category3": "의자", "category4": "사무용의자"}]
        }
        mock_cat_get.return_value = mock_cat_resp

        # 키워드 검색 결과 Mock (KeywordProcessor용)
        mock_kw_naver.return_value = [
            {"keyword": "의자", "monthlyPcQcCnt": 100, "monthlyMobileQcCnt": 500, "compIdx": "중간"},
            {"keyword": "소품함", "monthlyPcQcCnt": 50, "monthlyMobileQcCnt": 200, "compIdx": "낮음"}
        ]
        mock_kw_coupang.return_value = ["인테리어", "가구"]

        # 프로세서 초기화
        mapping_path = "data/naver_category_mapping.xls"
        if not os.path.exists(mapping_path):
            cat_processor = CategoryProcessor(mapping_file_path="non_existent.xls")
        else:
            cat_processor = CategoryProcessor(mapping_file_path=mapping_path)
            
        pn_processor = ProductNameProcessor(llm_provider=mock_llm)
        kw_processor = KeywordProcessor(llm_provider=mock_llm)

        results = []
        
        for original_name in SAMPLE_PRODUCT_NAMES:
            # 1. 상품명 가공
            refined_name = pn_processor.refine_product_name(original_name)
            assert refined_name is not None
            
            # 2. 키워드 추출 (Return type is str)
            keywords_str = kw_processor.process_keywords(refined_name)
            assert isinstance(keywords_str, str)
            assert len(keywords_str) > 0
            
            # 3. 카테고리 매핑
            category_code = cat_processor.get_category_code(refined_name)
            assert category_code is not None

            results.append({
                "original": original_name,
                "refined": refined_name,
                "keywords": keywords_str,
                "category": category_code
            })

        assert len(results) == len(SAMPLE_PRODUCT_NAMES)
        print(f"\n✅ {len(results)}개 샘플 상품 처리 테스트 완료 (Mocking)")

if __name__ == "__main__":
    test_processors_with_mocks()
