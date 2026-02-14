import os
from supabase import create_client, Client

# Hardcoded for debugging environment issues
url = "https://zrablxndgurvgulmalsf.supabase.co"
key = "sb_publishable_E5t1gGCzVrbjctQzpIJ2hQ_1jkCmArw"

if not url or not key:
    print("Error: URL or KEY missing", flush=True)
    exit(1)

supabase: Client = create_client(url, key)

email = "admin@autoselp.com"
password = "testpassword123"

print(f"Attempting to sign up user {email}...")

try:
    res = supabase.auth.sign_up({
        "email": email,
        "password": password,
    })
    print("Sign up response:", res)
    if res.user and res.user.identities and len(res.user.identities) > 0:
        print("User created successfully (or already exists).")
        # Check if email is confirmed
        if res.user.email_confirmed_at:
             print("Email is confirmed.")
        else:
             print("Email is NOT confirmed. Please check email (if enabled) or confirm manually in Supabase dashboard.")
    else:
        print("User creation failed or requires verification.")

except Exception as e:
    print(f"An error occurred: {e}")
