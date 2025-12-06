from typing import Optional, Dict, Any
from db import fetch_one, execute_returning_id
from utils.security import hash_password, check_password

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return fetch_one(
        "SELECT id, email, password_hash, full_name, is_active FROM users WHERE email = :email",
        {"email": email},
    )

def create_user(email: str, password: str, full_name: str) -> Dict[str, Any]:
    existing = get_user_by_email(email)
    if existing:
        raise ValueError("Ya existe un usuario con ese email.")

    pw_hash = hash_password(password)
    new_id = execute_returning_id(
        """
        INSERT INTO users (email, password_hash, full_name, is_active)
        VALUES (:email, :password_hash, :full_name, 1)
        """,
        {"email": email, "password_hash": pw_hash, "full_name": full_name or None},
    )
    return {"id": new_id, "email": email}

def authenticate(email: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not user.get("is_active"):
        return None
    if not check_password(password, user["password_hash"]):
        return None
    return {"id": user["id"], "email": user["email"], "full_name": user.get("full_name")}
