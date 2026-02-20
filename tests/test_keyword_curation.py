
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.getcwd())

from src.keyword_processor import KeywordProcessor
from src.llm_provider import get_llm_provider

load_dotenv()

def test_keyword_curation():
    print("Testing Keyword Curation Logic...")
    
    # Mock LLM Provider (Connect to real one to see output format)
    # Ensure OPENAI_API_KEY is in env or settings. I'll rely on env.
    try:
        llm_provider = get_llm_provider("openai", model="gpt-5-nano")
        if not llm_provider.is_configured():
            print("OpenAI API Key not configured.")
            return
    except Exception as e:
        print(f"Failed to init LLM: {e}")
        return

    kp = KeywordProcessor(llm_provider=llm_provider)
    
    product_name = "페디큐어 손가락 발가락 분리대"
    
    # Mock data passed from phase 2
    mock_keywords_data = [
        {"keyword": "페디큐어", "compIdx": "중간", "totalQcCnt": 5000},
        {"keyword": "발가락분리대", "compIdx": "낮음", "totalQcCnt": 2000},
        {"keyword": "네일아트", "compIdx": "높음", "totalQcCnt": 50000}, # Should be filtered out by LLM if instructed
        {"keyword": "발가락교정기", "compIdx": "중간", "totalQcCnt": 3000},
        {"keyword": "패디큐어세트", "compIdx": "낮음", "totalQcCnt": 1000},
        {"keyword": "네일재료", "compIdx": "높음", "totalQcCnt": 20000},
        {"keyword": "발가락링", "compIdx": "낮음", "totalQcCnt": 500},
        {"keyword": "토우세퍼레이터", "compIdx": "낮음", "totalQcCnt": 100},
        {"keyword": "젤네일", "compIdx": "높음", "totalQcCnt": 100000},
        {"keyword": "발관리", "compIdx": "중간", "totalQcCnt": 4000},
        {"keyword": "네일용품", "compIdx": "높음", "totalQcCnt": 30000},
        # Total 11
    ]

    print(f"Input Keywords: {[k['keyword'] for k in mock_keywords_data]}")
    
    try:
        final_keywords = kp._curate_with_llm(product_name, mock_keywords_data)
        print(f"\nFinal Result: {final_keywords}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_keyword_curation()
