import os
import sys
import argparse
import time
from tqdm import tqdm
from dotenv import load_dotenv

# src 모듈 경로 추가1
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.excel_handler import ExcelHandler
from src.product_name_processor import ProductNameProcessor
from src.keyword_processor import KeywordProcessor
from src.category_processor import CategoryProcessor

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Auto-Selp: 쇼핑몰 대량등록 상품 가공 자동화 툴")
    parser.add_argument("input_file", nargs='?', default="sample_input.xlsx", help="가공할 엑셀 파일 경로")
    parser.add_argument("--p_col", default="A", help="상품명 열 문자 (기본: A)")
    parser.add_argument("--k_col", default="E", help="기존 키워드 열 문자 (기본: E)")
    parser.add_argument("--start_col", default="H", help="결과 저장 시작 열 문자 (기본: H)")
    
    args = parser.parse_args()

    print("="*50)
    print("Auto-Selp Automation Started")
    print(f"Target File: {args.input_file}")
    print("="*50)

    if not os.path.exists(args.input_file):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {args.input_file}")
        print("엑셀 파일을 프로젝트 폴더(/Users/yoonjae/Desktop/auto-selp)에 넣어주세요.")
        return

    # 1. 모듈 초기화
    print(">> 모듈 초기화 중...")
    try:
        excel = ExcelHandler()
        pnp = ProductNameProcessor()
        kp = KeywordProcessor()
        cp = CategoryProcessor(mapping_file_path="mapping.xlsx")
    except Exception as e:
        print(f"[ERROR] 초기화 실패: {e}")
        return

    # 2. 데이터 로드
    print(">> 데이터 로드 중...")
    try:
        rows = excel.load_excel(args.input_file, args.p_col, args.k_col)
    except Exception as e:
        print(f"[ERROR] 엑셀 로드 실패: {e}")
        return

    total_count = len(rows)
    print(f">> 총 {total_count}개 상품 데이터를 가공합니다.")
    
    results = []
    
    # 3. 가공 루프 (tqdm 진행률 표시)
    # Gemini Rate Limit 고려하여 4000개 처리 시 주의 필요
    
    for row in tqdm(rows, desc="Processing"):
        try:
            original_name = row['product_name']
            
            # 3-1. 상품명
            refined_name = pnp.refine_product_name(original_name)
            
            # 3-2. 키워드
            keywords = kp.process_keywords(refined_name)
            
            # 3-3. 카테고리
            cat_code = cp.get_category_code(refined_name)
            
            results.append({
                'row_index': row['row_index'],
                'refined_name': refined_name,
                'keywords': keywords,
                'category_code': cat_code,
                'image_url': '' 
            })
            
            # API Rate Limit 방지용 짧은 대기 (필요 시 주석 해제)
            # time.sleep(0.5) 
            
        except Exception as e:
            print(f"\n[ERROR] Row {row['row_index']} 처리 중 오류: {e}")
            # 오류 나도 계속 진행
            results.append({'row_index': row['row_index']})

    # 4. 저장
    print("\n>> 결과 저장 중...")
    try:
        saved_path = excel.save_results(args.input_file, results, args.start_col)
        print(f"✅ 완료되었습니다! 결과 파일: {saved_path}")
    except Exception as e:
        print(f"[ERROR] 저장 실패: {e}")

if __name__ == "__main__":
    main()
