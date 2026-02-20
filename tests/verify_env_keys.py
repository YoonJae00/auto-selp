import os
import sys
from dotenv import load_dotenv
# Add src to path
sys.path.append(os.getcwd())

from src.user_settings_utils import get_user_api_key
from src.api.database import get_db

load_dotenv()

def test_key_retrieval():
    print("Testing get_user_api_key with .env fallback...")
    
    # Mocking DB client (we don't need real DB connectivity for env fallback test, 
    # but the function expects an object. 
    # However, get_user_api_key calls supabase.table... so it needs a real client or mock.)
    # Getting a real client might be tricky if I don't have credentials loaded in this context 
    # (though they are in .env).
    # Let's try getting real db.
    try:
        db = get_db()
    except Exception as e:
        print(f"DB Connection failed: {e}")
        # If DB fails, we can't fully test the function as written because it tries DB first.
        # But we can verify the map in the file visually or via import.
        # Let's just print the map from the module if we can't run it?
        # No, let's try running it.
        return

    user_id = "test_user_no_setting" 
    
    # Test Coupang Access Key
    key = get_user_api_key(db, user_id, "coupang_access_key")
    print(f"Coupang Access Key retrieved: {key[:5]}... (Length: {len(key)})")
    
    if len(key) > 10:
        print("✅ SUCCESS: Coupang Access Key found.")
    else:
        print("❌ FAILURE: Coupang Access Key NOT found.")

    # Test OpenAI Key
    key = get_user_api_key(db, user_id, "openai_api_key")
    print(f"OpenAI API Key retrieved: {key[:5]}... (Length: {len(key)})")
    if len(key) > 10:
        print("✅ SUCCESS: OpenAI API Key found.")
    else:
        print("❌ FAILURE: OpenAI API Key NOT found.")

if __name__ == "__main__":
    test_key_retrieval()
