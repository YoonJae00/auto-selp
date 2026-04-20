import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import httpx
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

prompt = """Extract 3 keywords from: apple, sky, tech, red. Return JSON: {"keywords": ["k1", "k2"]}"""

def test_magic():
    print("Testing Magic Prompt for gpt-5-nano...")
    try:
        http_client = httpx.Client(headers={"Content-Type": "application/json; charset=utf-8"}, timeout=30.0)
        client = OpenAI(api_key=api_key, http_client=http_client)
        
        # 1. The Known Working Prompt
        print("\n--- 1. Known Working ---")
        p1 = """Extract 3 keywords for 'apple' from: fruit, tech, red, delicious. Return JSON: {"keywords": ["k1", "k2"]}"""
        # Note: I realized I used 'apple' context in the original successful test.
        res1 = client.chat.completions.create(model="gpt-5-nano", messages=[{"role": "user", "content": p1}], max_completion_tokens=200).choices[0].message.content
        print(f"Result: '{res1}'")

        # 2. Adaptation to Pedicure (English)
        print("\n--- 2. Pedicure English ---")
        p2 = """Extract 3 keywords for 'pedicure' from: toe, nail, samsung, separator. Return JSON: {"keywords": ["k1", "k2"]}"""
        res2 = client.chat.completions.create(model="gpt-5-nano", messages=[{"role": "user", "content": p2}], max_completion_tokens=200).choices[0].message.content
        print(f"Result: '{res2}'")

        # 3. Adaptation to Pedicure (Korean)
        print("\n--- 3. Pedicure Korean ---")
        p3 = """Extract 3 keywords for '페디큐어' from: 발가락, 네일, 삼성, 분리대. Return JSON: {"keywords": ["k1", "k2"]}"""
        res3 = client.chat.completions.create(model="gpt-5-nano", messages=[{"role": "user", "content": p3}], max_completion_tokens=200).choices[0].message.content
        print(f"Result: '{res3}'")
        
        # 4. Adaptation with Instructions
        print("\n--- 4. With Instructions ---")
        p4 = """Extract safe keywords for '페디큐어' from: 발가락, 네일, 삼성, 분리대. Exclude '삼성'. Return JSON: {"keywords": ["k1", "k2"]}"""
        res4 = client.chat.completions.create(model="gpt-5-nano", messages=[{"role": "user", "content": p4}], max_completion_tokens=200).choices[0].message.content
        print(f"Result: '{res4}'")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_magic()
