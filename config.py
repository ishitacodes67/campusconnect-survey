import os, sys
from dotenv import load_dotenv
load_dotenv()

class Settings:
    DB_PATH:                 str = os.getenv("DB_PATH", "campusconnect.db")
    JWT_SECRET:              str = os.getenv("JWT_SECRET", "")
    DASHBOARD_PASSWORD_HASH: str = os.getenv("DASHBOARD_PASSWORD_HASH", "")
    SUPABASE_URL:            str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY:            str = os.getenv("SUPABASE_KEY", "")

    def validate(self):
        errors = []
        if not self.JWT_SECRET:              errors.append("JWT_SECRET missing")
        if not self.DASHBOARD_PASSWORD_HASH: errors.append("DASHBOARD_PASSWORD_HASH missing")
        elif not self.DASHBOARD_PASSWORD_HASH.startswith("$2b$"): errors.append("DASHBOARD_PASSWORD_HASH invalid")
        if not self.SUPABASE_URL:            errors.append("SUPABASE_URL missing")
        if not self.SUPABASE_KEY:            errors.append("SUPABASE_KEY missing")
        if errors:
            print("\n❌ Setup incomplete:")
            for e in errors: print(f"   • {e}")
            sys.exit(1)

settings = Settings()
