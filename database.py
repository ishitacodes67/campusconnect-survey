"""
Database layer — Supabase REST API.
Uses httpx directly to avoid client version issues.
"""

import httpx
from config import settings


def get_headers():
    return {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def supabase_get(table: str, params: dict = None):
    """SELECT from a table."""
    url = f"{settings.SUPABASE_URL}/rest/v1/{table}"
    with httpx.Client(timeout=10) as client:
        r = client.get(url, headers=get_headers(), params=params or {})
        r.raise_for_status()
        return r.json()


def supabase_count(table: str, params: dict = None):
    """COUNT rows in a table."""
    url = f"{settings.SUPABASE_URL}/rest/v1/{table}"
    headers = {**get_headers(), "Prefer": "count=exact"}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, headers=headers, params={"select": "id", **(params or {})})
        r.raise_for_status()
        count = r.headers.get("content-range", "0/0").split("/")[-1]
        return int(count) if count != "*" else 0


def supabase_insert(table: str, data: dict):
    """INSERT a row."""
    url = f"{settings.SUPABASE_URL}/rest/v1/{table}"
    with httpx.Client(timeout=10) as client:
        r = client.post(url, headers=get_headers(), json=data)
        r.raise_for_status()
        return r.json()


def supabase_delete(table: str, eq_field: str, eq_value):
    """DELETE a row by field value."""
    url = f"{settings.SUPABASE_URL}/rest/v1/{table}"
    params = {eq_field: f"eq.{eq_value}"}
    headers = {**get_headers(), "Prefer": "return=representation"}
    with httpx.Client(timeout=10) as client:
        r = client.delete(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()


def init_db():
    """Verify Supabase connection at startup."""
    try:
        supabase_get("responses", {"select": "id", "limit": "1"})
        print("   Database → Supabase connected ✅")
    except Exception as e:
        print(f"   ⚠ Supabase warning: {e}")
        print("   Check SUPABASE_URL and SUPABASE_KEY in Render environment variables.")
