#!/usr/bin/env python3
"""
상품명 리스트를 입력받아 상품명 가공, 키워드 추출, 카테고리 매핑을 테스트하는 스크립트

사용법:
    python test_processors_simple.py
"""

import os
import sys
from dotenv import load_dotenv
import pandas as pd

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from src.product_name_processor import ProductNameProcessor
from src.keyword_processor import KeywordProcessor
from src.category_processor import CategoryProcessor

# 환경 변수 로드
load_dotenv()

# 테스트할 상품명 리스트
SAMPLE_PRODUCT_NAMES = [
    "[시즈맥스] 3단 미니미 소품함 1p (정리함)",
    "브랜드명 좋은 의자 10p",
    "원룸 미니 건조대",
    "다이소 주방 수세미 5p",
    "3M 스카치 테이프 1개"
]

def test_processors():
    """3가지 프로세서를 순차적으로 테스트"""
    
    print("\n" + "="*80)
    print("Auto-Selp 프로세서 통합 테스트")
    print("="*80)
    
    # API 키 확인
    gemini_key = os.getenv("GEMINI_API_KEY")
    naver_client_id = os.getenv("NAVER_CLIENT_ID")
    
    if not gemini_key:
        print("\n⚠️  [WARNING] GEMINI_API_KEY가 .env 파일에 없습니다.")
        print("   상품명 가공과 키워드 추출이 제대로 작동하지 않을 수 있습니다.\n")
    
    if not naver_client_id:
        print("\n⚠️  [WARNING] NAVER_CLIENT_ID가 .env 파일에 없습니다.")
        print("   카테고리 매핑이 제대로 작동하지 않을 수 있습니다.\n")
    
    # 프로세서 초기화
    print("\n프로세서 초기화 중...")
    pn_processor = ProductNameProcessor()
    kw_processor = KeywordProcessor()
    cat_processor = CategoryProcessor(mapping_file_path="mapping.xlsx")
    print("✅ 프로세서 초기화 완료\n")
    
    # 결과 저장용 리스트
    results = []
    
    # 각 상품명에 대해 처리
    for idx, original_name in enumerate(SAMPLE_PRODUCT_NAMES, 1):
        print(f"\n{'─'*80}")
        print(f"[{idx}/{len(SAMPLE_PRODUCT_NAMES)}] 처리 중: {original_name}")
        print(f"{'─'*80}")
        
        # 1. 상품명 가공
        print("\n[1/3] 상품명 가공 중...")
        try:
            refined_name = pn_processor.refine_product_name(original_name)
            print(f"  ✅ 원본: {original_name}")
            print(f"  ✅ 가공: {refined_name}")
        except Exception as e:
            refined_name = f"ERROR: {str(e)}"
            print(f"  ❌ 오류: {e}")
        
        # 2. 키워드 추출
        print("\n[2/3] 키워드 추출 중...")
        try:
            keywords = kw_processor.process_keywords(refined_name if "ERROR" not in refined_name else original_name)
            print(f"  ✅ 키워드: {keywords}")
        except Exception as e:
            keywords = f"ERROR: {str(e)}"
            print(f"  ❌ 오류: {e}")
        
        # 3. 카테고리 매핑
        print("\n[3/3] 카테고리 매핑 중...")
        try:
            category_code = cat_processor.get_category_code(refined_name if "ERROR" not in refined_name else original_name)
            print(f"  ✅ 카테고리 코드: {category_code}")
        except Exception as e:
            category_code = f"ERROR: {str(e)}"
            print(f"  ❌ 오류: {e}")
        
        # 결과 저장
        results.append({
            "원본 상품명": original_name,
            "가공된 상품명": refined_name,
            "키워드": keywords,
            "카테고리 코드": category_code
        })
    
    # 결과 요약 출력
    print("\n" + "="*80)
    print("테스트 결과 요약")
    print("="*80)
    
    df = pd.DataFrame(results)
    print("\n" + df.to_string(index=False))
    
    # 성공/실패 통계
    print("\n" + "="*80)
    print("통계")
    print("="*80)
    
    total = len(results)
    success_refined = sum(1 for r in results if "ERROR" not in str(r["가공된 상품명"]))
    success_keywords = sum(1 for r in results if "ERROR" not in str(r["키워드"]) and r["키워드"])
    success_category = sum(1 for r in results if "ERROR" not in str(r["카테고리 코드"]) and r["카테고리 코드"] and "매핑실패" not in r["카테고리 코드"])
    
    print(f"\n총 테스트 건수: {total}")
    print(f"상품명 가공 성공: {success_refined}/{total} ({success_refined/total*100:.1f}%)")
    print(f"키워드 추출 성공: {success_keywords}/{total} ({success_keywords/total*100:.1f}%)")
    print(f"카테고리 매핑 성공: {success_category}/{total} ({success_category/total*100:.1f}%)")
    
    # 최종 판정
    print("\n" + "="*80)
    if success_refined == total and success_keywords == total and success_category == total:
        print("✅ 모든 테스트 통과!")
    elif success_refined == total and success_keywords == total:
        print("⚠️  상품명 가공과 키워드 추출은 성공했으나, 카테고리 매핑에 문제가 있습니다.")
        print("   네이버 API 키를 확인하거나 mapping.xlsx 파일을 업데이트하세요.")
    else:
        print("❌ 일부 테스트 실패. 위의 오류 메시지를 확인하세요.")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_processors()
