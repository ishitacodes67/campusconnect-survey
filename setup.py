"""
Run this ONCE before starting the server.
It will:
  1. Ask you to set a dashboard password
  2. Hash it securely with bcrypt
  3. Generate a random JWT secret
  4. Write everything to .env

Usage:
    python setup.py
"""

import bcrypt
import secrets
import os
import getpass


def main():
    print("\n" + "═" * 50)
    print("  CampusConnect — First-Time Setup")
    print("═" * 50 + "\n")

    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        overwrite = input(".env already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != "y":
            print("Setup cancelled. Existing .env kept.")
            return

    # ── Get password ─────────────────────────────────────────────────────────
    print("Set the shared dashboard password (your team will use this to log in).")
    print("Min 8 characters recommended.\n")

    while True:
        password = getpass.getpass("Enter dashboard password: ")
        if len(password) < 6:
            print("  ✗ Too short. Use at least 6 characters.\n")
            continue
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("  ✗ Passwords don't match. Try again.\n")
            continue
        break

    # ── Hash password ─────────────────────────────────────────────────────────
    print("\nHashing password...")
    salt   = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    # ── Generate JWT secret ───────────────────────────────────────────────────
    jwt_secret = secrets.token_hex(32)

    # ── Write .env ────────────────────────────────────────────────────────────
    env_content = f"""# CampusConnect — Environment Variables
# DO NOT share this file or commit it to GitHub

DB_PATH=campusconnect.db
JWT_SECRET={jwt_secret}
DASHBOARD_PASSWORD_HASH="{hashed}"
"""
    with open(env_path, "w") as f:
        f.write(env_content)

    print("\n✅ Setup complete!")
    print(f"   .env written to: {env_path}")
    print("\n📌 Next steps:")
    print("   1. pip install -r requirements.txt")
    print("   2. python main.py")
    print("   3. Open http://localhost:8000/dashboard\n")
    print("⚠️  Never commit .env to GitHub. It's already in .gitignore.\n")


if __name__ == "__main__":
    main()
