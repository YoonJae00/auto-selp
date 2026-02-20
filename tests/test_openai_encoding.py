#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenAI 한글 인코딩 테스트
"""
import os
import sys
from dotenv import load_dotenv

# UTF-8 인코딩 강제 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_openai_korean():
    """OpenAI API로 한글 프롬프트 테스트"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        return
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # 한글 프롬프트 테스트
        test_prompt = "안녕하세요를 영어로 번역해주세요."
        
        print(f"프롬프트: {test_prompt}")
        print(f"프롬프트 타입: {type(test_prompt)}")
        print(f"프롬프트 인코딩 가능 여부: {test_prompt.encode('utf-8')}")
        
        model_name = "gpt-5-nano"
        print(f"Testing with model: {model_name}")

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": test_prompt}
            ],
            max_completion_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"\n✅ 성공!")
        print(f"결과: {result}")
        
    except Exception as e:
        import traceback
        print(f"\n❌ 오류 발생:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_openai_korean()
