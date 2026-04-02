"""
Run this once on your laptop to generate the dashboard password hash.
Then paste the output into Render's environment variables.

Usage:
    python deploy_helper.py
"""
import bcrypt, getpass, secrets

print("\n" + "="*52)
print("  CampusConnect — Render Deployment Helper")
print("="*52 + "\n")
print("This generates the values you need to paste into")
print("Render's Environment Variables panel.\n")

while True:
    pw = getpass.getpass("Choose your dashboard password: ")
    if len(pw) < 6:
        print("  Too short — use at least 6 characters.\n")
        continue
    pw2 = getpass.getpass("Confirm password: ")
    if pw != pw2:
        print("  Passwords don't match.\n")
        continue
    break

hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=12)).decode()
secret = secrets.token_hex(32)

print("\n✅ Done! Copy these into Render's Environment Variables:\n")
print("─"*52)
print(f"Key:   DASHBOARD_PASSWORD_HASH")
print(f"Value: {hashed}")
print()
print(f"Key:   JWT_SECRET")
print(f"Value: {secret}")
print("─"*52)
print("\n⚠  Keep these values private. Never share them publicly.\n")
