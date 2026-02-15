from src.api.database import get_db

def get_user_id():
    db = get_db()
    # Try to list users
    try:
        # This requires service_role key
        users = db.auth.admin.list_users()
        if users:
            print(f"Found user: {users[0].id}")
            return users[0].id
        else:
            print("No users found in auth.users")
    except Exception as e:
        print(f"Error listing users: {e}")

if __name__ == "__main__":
    get_user_id()
