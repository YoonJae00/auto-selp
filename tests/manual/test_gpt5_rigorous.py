import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import httpx

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def test_rigorous():
    print("Testing Rigorous Compatibility for gpt-5-nano...")
    try:
        http_client = httpx.Client(headers={"Content-Type": "application/json; charset=utf-8"}, timeout=30.0)
        client = OpenAI(api_key=api_key, http_client=http_client)
        
        # 1. English Control (Fruit) - Expect Success (based on prev test)
        print("\n--- 1. English Fruit ---")
        p1 = "Extract keywords from: apple, sky, tech. JSON: {\"keywords\":[]}"
        res1 = client.chat.completions.create(model="gpt-5-nano", messages=[{"role": "user", "content": p1}], max_completion_tokens=200).choices[0].message.content
        print(f"Result: '{res1}'")

        # 2. Korean Fruit - Language Test
        print("\n--- 2. Korean Fruit ---")
        p2 = "다음에서 키워드 추출: 사과, 하늘, 테크. JSON: {\"keywords\":[]}"
        res2 = client.chat.completions.create(model="gpt-5-nano", messages=[{"role": "user", "content": p2}], max_completion_tokens=200).choices[0].message.content
        print(f"Result: '{res2}'")
        
        # 3. English Brand - Safety Test
        print("\n--- 3. English Brand ---")
        p3 = "Extract keywords from: Samsung, Apple, Nike. JSON: {\"keywords\":[]}"
        res3 = client.chat.completions.create(model="gpt-5-nano", messages=[{"role": "user", "content": p3}], max_completion_tokens=200).choices[0].message.content
        print(f"Result: '{res3}'")

        # 4. Korean Brand - Safety Test
        print("\n--- 4. Korean Brand ---")
        p4 = "다음에서 키워드 추출: 삼성, 애플, 나이키. JSON: {\"keywords\":[]}"
        res4 = client.chat.completions.create(model="gpt-5-nano", messages=[{"role": "user", "content": p4}], max_completion_tokens=200).choices[0].message.content
        print(f"Result: '{res4}'")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_rigorous()
