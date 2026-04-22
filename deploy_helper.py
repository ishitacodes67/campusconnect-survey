import bcrypt, getpass, secrets

print("\n" + "="*52)
print("  CampusConnect — Render Deployment Helper")
print("="*52 + "\n")

while True:
    pw = getpass.getpass("Choose your dashboard password: ")
    if len(pw) < 6: print("Too short.\n"); continue
    if getpass.getpass("Confirm: ") != pw: print("No match.\n"); continue
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
print("-"*52 + "\n")
