from src.llm_provider import OpenAIProvider
import os

# 테스트용 더티 키 (보이지 않는 문자 포함)
dirty_key = "sk-test1234\u200b"  # Zero-width space included
print(f"Dirty Key: {repr(dirty_key)}")

provider = OpenAIProvider(api_key=dirty_key)
print(f"Sanitized Key: {repr(provider.api_key)}")

if provider.api_key == "sk-test1234":
    print("✅ API Key Sanitization Successful")
else:
    print("❌ API Key Sanitization Failed")

# 한글 포함 테스트
korean_key = "sk-test한글"
print(f"\nKorean Key: {repr(korean_key)}")
provider = OpenAIProvider(api_key=korean_key)
print(f"Sanitized Key: {repr(provider.api_key)}")

if provider.api_key == "sk-test":
    print("✅ Korean Strip Successful")
else:
    print("❌ Korean Strip Failed")
