
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from src.keyword_processor import KeywordProcessor
from src.product_name_processor import ProductNameProcessor
from src.llm_provider import get_llm_provider

load_dotenv()

def verify_fix():
    print("Verifying gpt-5-nano Fix with JSON Prompts...")
    
    try:
        # 1. Init Provider with gpt-5-nano
        llm = get_llm_provider("openai", model="gpt-5-nano")
        if not llm.is_configured():
            print("❌ OpenAI API Key missing.")
            return

        # 2. Test Product Name
        print("\n--- Testing Product Name Processing ---")
        p_processor = ProductNameProcessor(llm_provider=llm)
        original = "시즈맥스 페디큐어 손가락 발가락 분리대 10p"
        refined = p_processor.refine_product_name(original)
        print(f"Original: {original}")
        print(f"Refined:  {refined}")
        
        if refined and refined != original and "시즈맥스" not in refined:
            print("✅ Product Name Success")
        else:
            print(f"⚠️ Product Name Check Output: '{refined}' (Might be same as original if LLM failed silently or logic preserved it)")

        # 3. Test Keyword Curation
        print("\n--- Testing Keyword Curation ---")
        k_processor = KeywordProcessor(llm_provider=llm)
        
        mock_data = [
            {"keyword": "페디큐어", "compIdx": "중간", "totalQcCnt": 5000},
            {"keyword": "발가락분리대", "compIdx": "낮음", "totalQcCnt": 2000},
            {"keyword": "삼성네일", "compIdx": "높음", "totalQcCnt": 50}, # Should be removed (Brand)
            {"keyword": "토우세퍼레이터", "compIdx": "낮음", "totalQcCnt": 100}
        ]
        
        keywords = k_processor._curate_with_llm("페디큐어 분리대", mock_data)
        print(f"Keywords: {keywords}")
        
        if keywords and len(keywords) > 0:
            print("✅ Keyword Curation Success")
        else:
            print("❌ Keyword Curation Failed (Empty Result)")

    except Exception as e:
        print(f"❌ Verification Failed: {e}")

if __name__ == "__main__":
    verify_fix()
