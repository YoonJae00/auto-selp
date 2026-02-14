import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[WARNING] SUPABASE_URL or SUPABASE_KEY not found in .env")
    supabase: Client = None
else:
    supabase: Client = create_client(url, key)

def get_db() -> Client:
    return supabase
