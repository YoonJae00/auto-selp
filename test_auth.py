import requests

base_url = "http://localhost:8000/api/auth"

print("--- Testing /verify-admin-code ---")
res = requests.post(f"{base_url}/verify-admin-code", json={"admin_code": "elwlslfosem7!"})
print("verify:", res.status_code, res.text)

print("--- Testing /register-admin ---")
res = requests.post(f"{base_url}/register-admin", json={"username": "testadmin2", "password": "testpassword2"})
print("register:", res.status_code, res.text)

print("--- Testing /login ---")
res = requests.post(f"{base_url}/login", json={"username": "testadmin2", "password": "testpassword2"})
print("login JSON:", res.status_code, res.text)
