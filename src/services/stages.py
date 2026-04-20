from typing import Dict, Any, Optional
from .processing_pipeline import BaseProcessorStage
from src.processors.product_name_processor import ProductNameProcessor
from src.processors.keyword_processor import KeywordProcessor
from src.processors.category_processor import CategoryProcessor
from src.processors.coupang_category_processor import CoupangCategoryProcessor

class ProductNameStage(BaseProcessorStage):
    """상품명 정제 스테이지"""
    def __init__(self, pn_processor: ProductNameProcessor):
        self.processor = pn_processor

    def process(self, row: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if not context.get("options", {}).get("refine_name"):
            return row
            
        p_name = row.get('product_name', '').strip()
        if p_name:
            refined_name = self.processor.refine_product_name(
                p_name, 
                prompt_template=context.get("pn_prompt")
            )
            row['refined_name'] = refined_name
            # 다음 스테이지에서 정제된 이름을 원본처럼 사용할 수 있도록 context 업데이트 고려 가능
            # 여기서는 row 자체를 변경하여 전달
        return row

class KeywordStage(BaseProcessorStage):
    """키워드 추출 스테이지"""
    def __init__(self, kw_processor: KeywordProcessor):
        self.processor = kw_processor

    def process(self, row: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if not context.get("options", {}).get("keyword"):
            return row
            
        # 정제된 이름이 있으면 그것을 사용, 없으면 원본 이름 사용
        target_name = row.get('refined_name') or row.get('product_name', '')
        if target_name:
            row['keywords'] = self.processor.process_keywords(
                target_name, 
                prompt_template=context.get("kw_prompt")
            )
        return row

class CategoryStage(BaseProcessorStage):
    """카테고리 매칭 스테이지 (네이버 & 쿠팡)"""
    def __init__(self, cat_processor: CategoryProcessor, coupang_processor: Optional[CoupangCategoryProcessor] = None):
        self.cat_processor = cat_processor
        self.coupang_processor = coupang_processor

    def process(self, row: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        options = context.get("options", {})
        target_name = row.get('refined_name') or row.get('product_name', '')
        
        if not target_name:
            return row

        # 네이버 카테고리
        if options.get("category"):
            row['category_code'] = self.cat_processor.get_category_code(target_name)

        # 쿠팡 카테고리
        if options.get("coupang") and self.coupang_processor:
            row['coupang_category_code'] = self.coupang_processor.get_category_code(target_name)
            
        return row
