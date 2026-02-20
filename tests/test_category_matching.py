"""
카테고리 매칭 테스트 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.category_processor import CategoryProcessor

def test_category_matching():
    print("=" * 60)
    print("카테고리 매칭 테스트 시작")
    print("=" * 60)
    
    # CategoryProcessor 초기화
    cat_processor = CategoryProcessor(mapping_file_path="naver_category_mapping.xls")
    
    # 매핑 파일 로드 확인
    if not cat_processor.category_mapping:
        print("[ERROR] 매핑 파일이 로드되지 않았습니다.")
        print("프로젝트 루트에 'naver_category_mapping.xls' 파일이 있는지 확인하세요.")
        return
    
    print(f"\n✓ 매핑 파일 로드 완료: {len(cat_processor.category_mapping)}개 항목")
    print("\n매핑 데이터 샘플 (처음 5개):")
    for i, (path, code) in enumerate(list(cat_processor.category_mapping.items())[:5]):
        print(f"  {i+1}. {path} → {code}")
    
    # 테스트 상품명들
    test_products = [
        "아이폰 14 투명 케이스",
        "원룸 미니 건조대",
        "무선 블루투스 이어폰"
    ]
    
    print("\n" + "=" * 60)
    print("상품명별 카테고리 코드 매칭 테스트")
    print("=" * 60)
    
    for product_name in test_products:
        print(f"\n상품명: {product_name}")
        
        # 네이버 API 카테고리 검색
        naver_cat = cat_processor._search_naver_category(product_name)
        print(f"  └ 네이버 검색 결과: {naver_cat if naver_cat else '검색 실패'}")
        
        # 카테고리 코드 매칭
        category_code = cat_processor.get_category_code(product_name)
        print(f"  └ 매칭된 코드: {category_code}")
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)

if __name__ == "__main__":
    test_category_matching()
