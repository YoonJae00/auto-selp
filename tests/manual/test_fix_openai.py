import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import httpx

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # Try getting it from settings if not in env (mocking logic)
    print("OPENAI_API_KEY not found in .env")
    # For this test, we really need the key. I saw it wasn't in .env before.
    # The user said they updated settings via UI, so it might be in the DB, 
    # but I can't easily access the DB from this script without more setup.
    # I will rely on the error message interpretation if I can't run it.
    # BUT, I can try to use the key if I can read it from the `user_settings` table using the existing code.
    pass

def test_openai_generation():
    print("Testing OpenAI gpt-5-nano generation...")
    try:
        http_client = httpx.Client(
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=60.0
        )
        
        # Mocking the provider logic
        client = OpenAI(api_key=api_key, http_client=http_client)
        
        # Test 1: No params
        print("\nTest 1: Minimal params")
        try:
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[{"role": "user", "content": "Hello"}],
            )
            print("Success!")
            print(response.choices[0].message.content)
        except Exception as e:
            print(f"Failed: {e}")

        # Test 2: With max_completion_tokens
        print("\nTest 2: With max_completion_tokens=100")
        try:
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[{"role": "user", "content": "Hello"}],
                max_completion_tokens=100
            )
            print("Success!")
            print(response.choices[0].message.content)
        except Exception as e:
            print(f"Failed: {e}")

        # Test 3: With temperature=1
        print("\nTest 3: With temperature=1")
        try:
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=1
            )
            print("Success!")
            print(response.choices[0].message.content)
        except Exception as e:
            print(f"Failed: {e}")

    except Exception as e:
        print(f"Setup Failed: {e}")

if __name__ == "__main__":
    test_openai_generation()
