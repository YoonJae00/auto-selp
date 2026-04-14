import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Config
API_URL = "http://localhost:8000"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase settings missing in .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_backend_flow():
    import logging
    logging.basicConfig(filename='backend_test.log', level=logging.INFO, format='%(message)s')
    def print(msg): logging.info(msg)
    print("=== Auto-Selp Backend Integration Test ===")
    
    email = "admin@autoselp.com"
    password = "testpassword123"
    
    print(f"1. Authenticating User: {email}")
    try:
        # Try Login first
        try:
            session = supabase.auth.sign_in_with_password({"email": email, "password": password})
            token = session.session.access_token
            print(f"   -> Login Success! Token: {token[:10]}...")
        except:
            # If Login fails, try Sign Up
            print("   -> Login failed, trying Sign Up...")
            res = supabase.auth.sign_up({"email": email, "password": password})
            # Check if auto-confirm is on (session) or off (user)
            if res.session:
                token = res.session.access_token
                print(f"   -> Signup & Login Success! Token: {token[:10]}...")
            else:
                 # Try login again (sometimes autoconfirm works but response is different)
                session = supabase.auth.sign_in_with_password({"email": email, "password": password})
                token = session.session.access_token
                print(f"   -> Signup Success! Token: {token[:10]}...")
                
    except Exception as e:
        print(f"   -> Auth Failed: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload Dummy Excel
    print("\n2. Uploading Dummy Excel File...")
    
    # Create dummy excel
    dummy_data = {
        "상품명": ["테스트 상품 1p", "브랜드 시즈맥스 의자", "좋은 상품 10p"],
        "키워드": ["의자", "책상", "마우스"],
        "카테고리ID": ["50000001", "50000002", "50000003"]
    }
    df = pd.DataFrame(dummy_data)
    dummy_file = "test_upload.xlsx"
    df.to_excel(dummy_file, index=False)
    
    try:
        with open(dummy_file, "rb") as f:
            files = {"file": (dummy_file, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            resp = requests.post(f"{API_URL}/api/jobs/", headers=headers, files=files)
            
        if resp.status_code == 200:
            job_data = resp.json()
            job_id = job_data['job_id']
            print(f"   -> Upload Success! Job ID: {job_id}, Status: {job_data['status']}")
        else:
            print(f"   -> Upload Failed: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print(f"   -> Request Error: {e}")
        return
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

    # 3. Poll Status
    print(f"\n3. Polling Job Status for {job_id}...")
    for i in range(10):
        time.sleep(2)
        resp = requests.get(f"{API_URL}/api/jobs/{job_id}", headers=headers)
        if resp.status_code == 200:
            status_data = resp.json()
            status = status_data['status']
            progress = status_data['progress']
            print(f"   -> [{i+1}/10] Status: {status}, Progress: {progress}%")
            
            if status == 'completed':
                print("\n=== Test Passed! Job Completed Successfully ===")
                break
            elif status == 'failed':
                print(f"\n=== Test Failed! Error: {status_data.get('error_message')} ===")
                break
        else:
            print(f"   -> Polling Failed: {resp.status_code}")
    else:
        print("\n=== Test Timeout! Job did not complete in time ===")

if __name__ == "__main__":
    # Ensure server is up
    try:
        requests.get(API_URL)
        test_backend_flow()
    except:
        print("Error: Backend Server is not running on localhost:8000")
