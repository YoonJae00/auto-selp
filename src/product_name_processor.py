import os
import re
from dotenv import load_dotenv
from typing import Optional
from src.llm_provider import BaseLLMProvider, get_llm_provider

load_dotenv()

class ProductNameProcessor:
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        """
        ProductNameProcessor를 초기화합니다.
        
        Args:
            llm_provider: LLM 제공자 인스턴스 (None이면 기본 Gemini 사용)
        """
        if llm_provider is None:
            # 기본값: Gemini 사용
            self.llm_provider = get_llm_provider("gemini")
        else:
            self.llm_provider = llm_provider

    def refine_product_name(self, original_name: str, prompt_template: str = None) -> str:
        """
        LLM을 사용하여 상품명을 정제합니다.
        - 브랜드 제거
        - 수량/단위 표준화 (10p -> 10개, 1p -> 제거)
        - 검색 최적화
        """
        if not self.llm_provider.is_configured():
            return original_name + " (API키 없음)"

        try:

            # 기본 프롬프트 템플릿 (System Default)
            # Retry Logic for gpt-5-nano instability
            prompts = [
                f"Refine product name: '{original_name}'. Remove brands/special chars. Output only the name.",
                f"Clean this product name: '{original_name}'. Return string only.",
                f"Fix: '{original_name}'"
            ]
            
            cleaned_name = original_name # Default fallback
            
            for attempt, p_text in enumerate(prompts):
                try:
                    result = self.llm_provider.generate_content(p_text)
                    if result and len(result) > 1:
                        # Basic cleanup
                        result = result.replace('"', '').replace("'", "").strip()
                        # If result is JSON by mistake, try to parse
                        if result.startswith("{") and "}" in result:
                            # Try skip
                            continue
                        
                        cleaned_name = result
                        break
                except Exception as e:
                    print(f"   ⚠️ Product Name LLM Error (Attempt {attempt+1}): {e}")
                    continue
            
            return cleaned_name

        except Exception as e:
            print(f"상품명 가공 중 오류 발생: {e}")
            return original_name
