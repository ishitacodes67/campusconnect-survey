import bcrypt
import getpass
import secrets

print("\n" + "="*52)
print("  CampusConnect - Render Deployment Helper")
print("="*52 + "\n")
print("This generates the values you need to paste")
print("into Render's Environment Variables panel.\n")

while True:
    pw = getpass.getpass("Choose your dashboard password: ")
    if len(pw) < 6:
        print("  Too short - use at least 6 characters.\n")
        continue
    pw2 = getpass.getpass("Confirm password: ")
    if pw != pw2:
        print("  Passwords don't match. Try again.\n")
        continue
    break

hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=12)).decode()
secret = secrets.token_hex(32)

print("\n✅ Copy these into Render Environment Variables:\n")
print("-"*52)
print("Key:   DASHBOARD_PASSWORD_HASH")
print("Value: " + hashed)
print()
print("Key:   JWT_SECRET")
print("Value: " + secret)
print("-"*52)
print("\n Keep these values private. Never share them.\n")
