import sys
import os
from dotenv import load_dotenv

# src 모듈 경로 설정을 위해
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.product_name_processor import ProductNameProcessor
from src.keyword_processor import KeywordProcessor

def verify_core_logic():
    load_dotenv()
    
    # 1. API Key Check
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("\n[CRITICAL] GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        print("테스트를 중단합니다.")
        return

    print("\n" + "="*50)
    print("Auto-Selp Core Logic Verification")
    print("="*50)

    # 2. Product Name Processor Test
    print("\n[TEST 1] 상품명 가공 테스트")
    pnp = ProductNameProcessor()
    
    # 예시: 브랜드(시즈맥스), 수량(1p), 특수문자([])
    original_name = "[시즈맥스] 3단 미니미 소품함 1p (정리함)"
    cleaned_name = pnp.refine_product_name(original_name)
    
    print(f"원본: {original_name}")
    print(f"결과: {cleaned_name}")
    
    if "시즈맥스" not in cleaned_name and "1p" not in cleaned_name:
        print(">> [PASS] 브랜드 및 수량 제거 성공")
    else:
        print(">> [FAIL] 필터링 규칙 적용 미흡 (프롬프트 조정 필요)")

    # 3. Keyword Processor Test
    print("\n[TEST 2] 키워드 수집 및 필터링 테스트")
    kp = KeywordProcessor()
    
    # 위에서 가공된 상품명 사용 (실패 시에도 테스트 가능하도록 강제 설정)
    target_keyword = "3단 미니 소품함" 
    print(f"검색어: {target_keyword}")
    
    final_keywords = kp.process_keywords(target_keyword)
    print(f"\n최종 추천 키워드: {final_keywords}")
    
    if final_keywords:
        print(">> [PASS] 키워드 생성 성공")
    else:
        print(">> [FAIL] 키워드 생성 실패 (API 확인 필요)")

if __name__ == "__main__":
    verify_core_logic()
