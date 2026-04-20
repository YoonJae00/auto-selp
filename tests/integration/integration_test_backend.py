import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Config
API_URL = "http://localhost:8000"

def test_backend_flow():
    import logging
    logging.basicConfig(filename='backend_test.log', level=logging.INFO, format='%(message)s')
    def print_log(msg): 
        logging.info(msg)
        print(msg)

    print_log("=== Auto-Selp Backend Integration Test ===")
    
    username = "admin"
    password = "admin123"
    
    print_log(f"1. Authenticating User: {username}")
    try:
        # Try Login
        login_resp = requests.post(
            f"{API_URL}/api/auth/login", 
            json={"username": username, "password": password}
        )
        
        if login_resp.status_code == 200:
            token = login_resp.json()["access_token"]
            print_log(f"   -> Login Success! Token: {token[:10]}...")
        else:
            print_log(f"   -> Login failed: {login_resp.status_code} - {login_resp.text}")
            # Try to register if login failed (for clean environments)
            print_log("   -> Attempting to register admin user...")
            reg_resp = requests.post(
                f"{API_URL}/api/auth/register-admin",
                json={"username": username, "password": password}
            )
            if reg_resp.status_code == 200:
                # Login again
                login_resp = requests.post(
                    f"{API_URL}/api/auth/login", 
                    json={"username": username, "password": password}
                )
                token = login_resp.json()["access_token"]
                print_log(f"   -> Registration & Login Success!")
            else:
                print_log(f"   -> Auth Failed completely: {reg_resp.text}")
                return
                
    except Exception as e:
        print_log(f"   -> Auth Request Error: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload Dummy Excel
    print_log("\n2. Uploading Dummy Excel File...")
    
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
            print_log(f"   -> Upload Success! Job ID: {job_id}, Status: {job_data['status']}")
        else:
            print_log(f"   -> Upload Failed: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print_log(f"   -> Request Error: {e}")
        return
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

    # 3. Poll Status
    print_log(f"\n3. Polling Job Status for {job_id}...")
    for i in range(20): # Increase retries for background processing
        time.sleep(3)
        resp = requests.get(f"{API_URL}/api/jobs/{job_id}", headers=headers)
        if resp.status_code == 200:
            status_data = resp.json()
            status = status_data['status']
            progress = status_data['progress']
            print_log(f"   -> [{i+1}/20] Status: {status}, Progress: {progress}%")
            
            if status == 'completed':
                print_log("\n=== Test Passed! Job Completed Successfully ===")
                break
            elif status == 'failed':
                print_log(f"\n=== Test Failed! Error: {status_data.get('error_message')} ===")
                break
        else:
            print_log(f"   -> Polling Failed: {resp.status_code}")
    else:
        print_log("\n=== Test Timeout! Job did not complete in time ===")

if __name__ == "__main__":
    # Ensure server is up
    try:
        requests.get(API_URL)
        test_backend_flow()
    except Exception as e:
        print(f"Error: Backend Server is not running or accessible on {API_URL}: {e}")
