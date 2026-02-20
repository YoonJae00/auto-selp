import sys
import os

# src 모듈을 찾기 위해 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.keyword_processor import KeywordProcessor

def test_coupang_crawling():
    print("\n[TEST] Coupang Crawling Start")
    kp = KeywordProcessor()
    # "양말" 이라는 키워드로 테스트
    keywords = kp._get_coupang_related_keywords("양말")
    print(f"Result: {keywords}")
    
    if keywords:
        print("[SUCCESS] Coupang API returned keywords.")
    else:
        print("[WARNING] Coupang API returned empty list (Check network or anti-bot).")

def test_naver_api():
    print("\n[TEST] Naver API Start")
    kp = KeywordProcessor()
    # API Key가 없으면 내부 로직에서 Skip함 via logic
    keywords = kp._get_naver_api_keywords("양말")
    print(f"Result: {keywords}")

if __name__ == "__main__":
    test_coupang_crawling()
    test_naver_api()
