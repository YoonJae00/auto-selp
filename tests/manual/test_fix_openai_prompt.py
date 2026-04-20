import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import httpx

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

prompt = """역할: 쇼핑몰 키워드 추천 전문가
목표: 소상공인이 사용할 수 있는 안전한 키워드 10개 선별.

상품명: 페디큐어 손가락 발가락 분리대

규칙:
1. 브랜드명/상표명은 절대 포함하지 마세요. (예: 삼성, LG, 뽀로로 등 금지)
2. 너무 광범위하거나 관련 없는 키워드는 제외하세요.
3. 경쟁도가 낮고 검색수가 적절한 세부 키워드를 선호합니다.

후보 키워드:
- 페디큐어 (경쟁도: 중간, 월 검색수: 5000)
- 발가락분리대 (경쟁도: 낮음, 월 검색수: 2000)
- 네일아트 (경쟁도: 높음, 월 검색수: 50000)
- 발가락교정기 (경쟁도: 중간, 월 검색수: 3000)
- 패디큐어세트 (경쟁도: 낮음, 월 검색수: 1000)
- 네일재료 (경쟁도: 높음, 월 검색수: 20000)
- 발가락링 (경쟁도: 낮음, 월 검색수: 500)
- 토우세퍼레이터 (경쟁도: 낮음, 월 검색수: 100)
- 젤네일 (경쟁도: 높음, 월 검색수: 100000)
- 발관리 (경쟁도: 중간, 월 검색수: 4000)
- 네일용품 (경쟁도: 높음, 월 검색수: 30000)

결과: 키워드1, 키워드2, ... (콤마로 구분)"""

def test_full_prompt():
    print("Testing Full Prompt with gpt-5-nano...")
    try:
        http_client = httpx.Client(
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=60.0
        )
        
        client = OpenAI(api_key=api_key, http_client=http_client)
        
        # Test 1: Full Prompt with gpt-4o-mini
        print("\nTest 1: Full Prompt (gpt-4o-mini)")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1000
        )
        content = response.choices[0].message.content
        print(f"Result: '{content}'")

        # Test 2: Full Prompt with max 200
        print("\nTest 2: Full Prompt (max=200)")
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=200
        )
        content = response.choices[0].message.content
        print(f"Result: '{content}'")
        
        # Test 4: Structure Test (Fruits)
        print("\nTest 4: Structure Test (Fruits)")
        fruit_prompt = """역할: 과일 전문가
목표: 맛있는 과일 3개 선별.

상황: 소풍감.

규칙:
1. 빨간 과일 제외.
2. 껍질 있는 과일 선호.

후보:
- 사과 (빨강)
- 바나나 (노랑)
- 포도 (보라)
- 수박 (초록)

결과: 과일1, 과일2"""
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": fruit_prompt}],
            max_completion_tokens=500
        )
        print(f"Result: '{response.choices[0].message.content}'")

        # Test 5: Content Test (Pedicure/Brands)
        print("\nTest 5: Content Test (Pedicure/Brands)")
        pedi_prompt = "페디큐어와 발가락 분리대 키워드를 추천해주세요. 나이키나 삼성 같은 브랜드는 쓰지 마세요."
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": pedi_prompt}],
            max_completion_tokens=500
        )
        # Test 6: Simple Pedicure (No brand mention)
        print("\nTest 6: Simple Pedicure (No brand mention)")
        pedi_simple = "페디큐어와 발가락 분리대 키워드 3개만 추천해주세요."
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": pedi_simple}],
            max_completion_tokens=500
        )
        print(f"Result: '{response.choices[0].message.content}'")
        
        # Test 7: Very Simple Structure
        print("\nTest 7: Very Simple Structure")
        struct_simple = """역할: 친구
인사해줘."""
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": struct_simple}],
            max_completion_tokens=500
        )
        print(f"Result: '{response.choices[0].message.content}'")

        # Test 8: Ultra Simple List Selection
        print("\nTest 8: Ultra Simple List Selection")
        simple_list_prompt = """다음 키워드 목록에서 상표권 문제가 없고 경쟁력이 좋은 키워드 10개를 골라주세요.
        
목록: 페디큐어, 발가락분리대, 네일아트, 발가락교정기, 패디큐어세트, 네일재료, 발가락링, 토우세퍼레이터, 젤네일, 발관리, 네일용품

결과:"""
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": simple_list_prompt}],
            max_completion_tokens=500
        )
        print(f"Result: '{response.choices[0].message.content}'")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_full_prompt()
