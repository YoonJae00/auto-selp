import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# src 모듈 경로 설정을 위해
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from category_processor import CategoryProcessor
from keyword_processor import KeywordProcessor

class TestChanges(unittest.TestCase):
    def test_category_processor_returns_path(self):
        """CategoryProcessor가 엑셀 매핑 없이 API 결과를 반환하는지 테스트"""
        processor = CategoryProcessor()
        
        # Mock _search_naver_category
        expected_path = "패션의류>여성의류>원피스"
        processor._search_naver_category = MagicMock(return_value=expected_path)
        
        result = processor.get_category_code("예시 상품")
        print(f"\n[Category] Expected: {expected_path}, Got: {result}")
        self.assertEqual(result, expected_path)
        
    def test_keyword_processor_limit(self):
        """KeywordProcessor가 키워드를 10개로 제한하는지 테스트"""
        processor = KeywordProcessor()
        
        # Mock internal methods to return more than 10 keywords
        # We need to mock _collect_seeds_multi_round, _filter_by_competition, and _finalize_keywords
        # But specifically _finalize_keywords is where we mocked the limit in the implementation, 
        # actually no, we implemented the limit in process_keywords AFTER _finalize_keywords returns.
        # So we just need _finalize_keywords to return > 10 items.
        
        dummy_keywords = [f"키워드{i}" for i in range(15)]
        
        # Mocking the flow
        processor._collect_seeds_multi_round = MagicMock(return_value=[{"keyword": k} for k in dummy_keywords])
        processor._filter_by_competition = MagicMock(return_value=[{"keyword": k} for k in dummy_keywords])
        processor._finalize_keywords = MagicMock(return_value=dummy_keywords)
        
        result = processor.process_keywords("예시 상품")
        result_list = result.split(", ")
        
        print(f"\n[Keyword] Generated {len(dummy_keywords)} keywords internally.")
        print(f"[Keyword] Result count: {len(result_list)}")
        print(f"[Keyword] Result: {result}")
        
        self.assertLessEqual(len(result_list), 10)
        self.assertEqual(len(result_list), 10)
        self.assertEqual(result_list[-1], "키워드9")

if __name__ == "__main__":
    unittest.main()
