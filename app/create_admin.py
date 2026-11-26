
from getpass import getpass
import sqlite3

from app.auth import init_user_database, create_user


def main():
    init_user_database()

    username = input("Admin username: ").strip()
    password = getpass("Admin password (minimum 5 characters): ")
    confirmation = getpass("Confirm admin password: ")

    if password != confirmation:
        print("Passwords do not match.")
        return

    try:
        create_user(username, password, "Admin")
    except ValueError as exc:
        print(f"Cannot create admin: {exc}")
        return
    except sqlite3.IntegrityError:
        print("That username already exists.")
        return

    print(f"Admin account '{username}' created successfully.")


if __name__ == "__main__":
    main()
