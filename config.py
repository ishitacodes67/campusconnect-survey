"""
Configuration — reads from .env file.
All sensitive values live in .env, never in source code.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_PATH: str                 = os.getenv("DB_PATH", "campusconnect.db")
    JWT_SECRET: str              = os.getenv("JWT_SECRET", "")
    DASHBOARD_PASSWORD_HASH: str = os.getenv("DASHBOARD_PASSWORD_HASH", "")
    SUPABASE_URL: str            = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str            = os.getenv("SUPABASE_KEY", "")

    def validate(self):
        """Called at startup — exits immediately if env is missing."""
        errors = []
        if not self.JWT_SECRET:
            errors.append("JWT_SECRET is missing from .env")
        if not self.DASHBOARD_PASSWORD_HASH:
            errors.append("DASHBOARD_PASSWORD_HASH is missing from .env")
        elif "placeholder" in self.DASHBOARD_PASSWORD_HASH:
            errors.append("DASHBOARD_PASSWORD_HASH is still the placeholder value")
        elif not self.DASHBOARD_PASSWORD_HASH.startswith("$2b$"):
            errors.append("DASHBOARD_PASSWORD_HASH is not a valid bcrypt hash")
        if not self.SUPABASE_URL:
            errors.append("SUPABASE_URL is missing from .env")
        if not self.SUPABASE_KEY:
            errors.append("SUPABASE_KEY is missing from .env")
        if errors:
            print("\n❌ Setup incomplete. Fix these issues then restart:")
            for e in errors:
                print(f"   • {e}")
            print("\n   Run:  python setup.py\n")
            sys.exit(1)


settings = Settings()
