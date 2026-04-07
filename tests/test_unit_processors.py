import pytest
from unittest.mock import MagicMock
from src.product_name_processor import ProductNameProcessor
from src.keyword_processor import KeywordProcessor
from src.category_processor import CategoryProcessor

@pytest.fixture
def mock_llm_provider():
    mock = MagicMock()
    mock.is_configured.return_value = True
    return mock

def test_product_name_processor(mock_llm_provider):
    mock_llm_provider.generate_content.return_value = "정제된 상품명"
    processor = ProductNameProcessor(llm_provider=mock_llm_provider)
    result = processor.refine_product_name("원래 [브랜드] 상품명 1p")
    assert result == "정제된 상품명"
    mock_llm_provider.generate_content.assert_called()

def test_keyword_processor(mock_llm_provider, mocker):
    mock_llm_provider.generate_content.return_value = "키워드1,키워드2"
    processor = KeywordProcessor(llm_provider=mock_llm_provider, api_keys={"naver_api_key":"test", "naver_secret_key":"test", "naver_customer_id":"test"})
    
    # Mocking Naver API and Coupang API to avoid real network requests
    mocker.patch.object(processor, '_search_naver_keywords_with_data', return_value=[{"keyword": "키워드1", "monthlyPcQcCnt": 100, "monthlyMobileQcCnt": 100, "compIdx": "낮음", "totalQcCnt": 200}])
    mocker.patch.object(processor, '_get_coupang_related_keywords', return_value=["키워드2"])
    
    result = processor.process_keywords("테스트 상품")
    assert "키워드" in result

def test_category_processor(mocker):
    # Dummy mapping file path to bypass loading actual excel
    processor = CategoryProcessor(mapping_file_path="dummy.xls")
    processor.category_mapping = {"디지털/가전>휴대폰악세서리>휴대폰케이스>아이폰케이스": "12345"}
    
    mocker.patch.object(processor, '_search_naver_category', return_value="디지털/가전>휴대폰악세서리>휴대폰케이스>아이폰케이스")
    result = processor.get_category_code("아이폰 케이스")
    assert result == "12345"
