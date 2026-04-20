import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import httpx
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def test_minimal():
    print("Testing Minimal Prompts for gpt-5-nano...")
    try:
        http_client = httpx.Client(headers={"Content-Type": "application/json; charset=utf-8"}, timeout=30.0)
        client = OpenAI(api_key=api_key, http_client=http_client)
        
        # Scenario 1: Product Name (Minimal)
        print("\n--- 1. Product Name ---")
        p_prompt = """Refine this product name for shopping search: '시즈맥스 페디큐어 손가락 발가락 분리대 10p'. Remove brands, special chars, and standardize units. Return JSON: {"refined_name": "string"}"""
        
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": p_prompt}],
            max_completion_tokens=200
        )
        print(f"Result: '{response.choices[0].message.content}'")

        # Scenario 2: Keywords (Minimal)
        print("\n--- 2. Keywords ---")
        k_prompt = """Select top 10 safe, relevant keywords from: '페디큐어, 발가락분리대, 삼성네일, 토우세퍼레이터'. Remove trademarks. Return JSON: {"keywords": ["k1", "k2"]}"""
        
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": k_prompt}],
            max_completion_tokens=200
        )
        print(f"Result: '{response.choices[0].message.content}'")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_minimal()
