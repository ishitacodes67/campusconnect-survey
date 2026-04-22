import bcrypt, secrets, os, getpass

def main():
    print("\n" + "="*50)
    print("  CampusConnect — First-Time Setup")
    print("="*50 + "\n")
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        if input(".env exists. Overwrite? (y/N): ").strip().lower() != "y":
            return

    while True:
        pw = getpass.getpass("Dashboard password: ")
        if len(pw) < 6: print("Too short.\n"); continue
        if getpass.getpass("Confirm: ") != pw: print("No match.\n"); continue
        break

    hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=12)).decode()
    secret = secrets.token_hex(32)
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f'DB_PATH=campusconnect.db\nJWT_SECRET={secret}\nDASHBOARD_PASSWORD_HASH="{hashed}"\nSUPABASE_URL=\nSUPABASE_KEY=\n')
    print("\n✅ Setup complete! Edit .env to add SUPABASE_URL and SUPABASE_KEY.\n")

if __name__ == "__main__":
    main()
