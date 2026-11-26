
from pwdlib import PasswordHash

# Use Argon2 for secure password hashing.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Convert a plain-text password into a secure hash."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its stored hash."""
    return password_hash.verify(password, hashed_password)

import sqlite3
import os
from pathlib import Path

# Store user accounts separately from the PLC application.
DATABASE_PATH = Path(
    os.getenv("AUTH_DATABASE", str(Path(__file__).resolve().parent / "users.db"))
)

VALID_ROLES = {"Viewer", "Operator", "Admin"}


def init_user_database() -> None:
    """Create the user table if it does not already exist."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK (role IN ('Viewer', 'Operator', 'Admin'))
            )
        """)


def create_user(username: str, password: str, role: str) -> None:
    """Create a user with a hashed password and an assigned role."""
    if not username.strip():
        raise ValueError("Username cannot be empty")
    if len(password) < 5:
        raise ValueError("Password must be at least 5 characters")
    if role not in VALID_ROLES:
        raise ValueError("Invalid role")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username.strip(), hash_password(password), role),
        )


def authenticate_user(username: str, password: str):
    """Return the user's username and role only if credentials are valid."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()

    if row and verify_password(password, row[1]):
        return {"username": row[0], "role": row[2]}
    return None
def get_user_by_username(username: str):
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT username, role FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()

    if row:
        return {"username": row[0], "role": row[1]}

    return None

def change_password(username: str, current_password: str, new_password: str) -> bool:
    """Change a user's password after verifying the current password."""
    if len(new_password) < 5:
        raise ValueError("New password must be at least 5 characters")

    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()

        if not row or not verify_password(current_password, row[0]):
            return False

        connection.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (hash_password(new_password), username.strip()),
        )

    return True

