import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
# TEMP: Prefer SERVICE_KEY for verification to bypass RLS
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[WARNING] SUPABASE_URL or SUPABASE_KEY not found in .env")
    supabase: Client = None
else:
    supabase: Client = create_client(url, key)

def get_db() -> Client:
    return supabase
