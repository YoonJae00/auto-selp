import os
import sys

# Add parent directory to path to import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.api.database import engine

def migrate():
    print("Starting migration...")
    with engine.connect() as conn:
        try:
            # 1. Rename column email to username
            conn.execute(text("ALTER TABLE users RENAME COLUMN email TO username;"))
            print("Renamed 'email' to 'username'.")
        except Exception as e:
            print(f"Error renaming column: {e}")

        try:
            # 2. Add role column
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user';"))
            print("Added 'role' column.")
        except Exception as e:
            print(f"Error adding 'role': {e}")
            
        try:
            # 3. Add is_profile_completed column
            conn.execute(text("ALTER TABLE users ADD COLUMN is_profile_completed BOOLEAN DEFAULT FALSE;"))
            print("Added 'is_profile_completed' column.")
        except Exception as e:
            print(f"Error adding 'is_profile_completed': {e}")
            
        try:
            # 4. Add email column (nullable)
            conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR;"))
            print("Added 'email' column.")
        except Exception as e:
            print(f"Error adding 'email': {e}")
            
        try:
            # 5. Add name column
            conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR;"))
            print("Added 'name' column.")
        except Exception as e:
            print(f"Error adding 'name': {e}")
            
        try:
            # 6. Add phone column
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR;"))
            print("Added 'phone' column.")
        except Exception as e:
            print(f"Error adding 'phone': {e}")
            
        conn.commit()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
