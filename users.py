import json
from pathlib import Path

USERS_FILE = Path("users.json")

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def register_user(user_id: int):
    users = load_users()
    user_key = str(user_id)
    users[user_key] = users.get(user_key, 0) + 1
    save_users(users)