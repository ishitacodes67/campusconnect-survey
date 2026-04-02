"""
Database layer — Supabase (PostgreSQL) via REST API.
No local SQLite needed. Works 24/7 from anywhere.
"""

import os
from supabase import create_client, Client
from config import settings


def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def init_db():
    """
    Table is created in Supabase dashboard directly.
    This just verifies the connection works at startup.
    """
    try:
        client = get_supabase()
        client.table("responses").select("id").limit(1).execute()
        print("   Database → Supabase connected ✅")
    except Exception as e:
        print(f"   ⚠ Supabase connection warning: {e}")
        print("   Make sure the responses table exists in Supabase.")
