import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import httpx
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

prompt_formats = {
    "1_system_user": [
        {"role": "system", "content": "You are a keyword expert."},
        {"role": "user", "content": "Pick 3 keywords for 'apple': fruit, tech, red, delicious. Format: comma separated."}
    ],
    "2_user_only_complex": [
        {"role": "user", "content": "Role: Keyword Expert\nTask: Pick 3 keywords for 'apple' from [fruit, tech, red, delicious].\nFormat: comma separated."}
    ],
    "3_user_only_simple": [
        {"role": "user", "content": "Select 3 related keywords for 'apple' from this list: fruit, tech, red, delicious. Return only the keywords separated by commas."}
    ],
    "4_user_json_request": [
        {"role": "user", "content": "Extract 3 keywords for 'apple' from: fruit, tech, red, delicious. Return JSON: {\"keywords\": [\"k1\", \"k2\"]}"}
    ],
    "5_few_shot": [
        {"role": "user", "content": "Input: banana, yellow, car. Output: banana, yellow\nInput: apple, tech, sky. Output:"}
    ]
}

def test_formats():
    print("Testing gpt-5-nano prompt compatibility...")
    try:
        http_client = httpx.Client(headers={"Content-Type": "application/json; charset=utf-8"}, timeout=30.0)
        client = OpenAI(api_key=api_key, http_client=http_client)
        
        for name, messages in prompt_formats.items():
            print(f"\n--- Testing {name} ---")
            try:
                # Try without max_completion_tokens first, then with if needed
                # But gpt-5-nano might require it? user said param change.
                # Let's use standard params.
                response = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=messages,
                    max_completion_tokens=500
                )
                content = response.choices[0].message.content
                print(f"Result: '{content}'")
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        print(f"Setup Failed: {e}")

if __name__ == "__main__":
    test_formats()
