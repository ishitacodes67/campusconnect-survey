"""
CampusConnect Survey Backend
FastAPI + Supabase + JWT dashboard auth
Works 24/7 — no local terminal needed
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, Response
from contextlib import asynccontextmanager
import uvicorn
import jwt
import bcrypt
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Optional
from models import SurveyResponse, DashboardLogin, TokenResponse
from database import init_db, get_supabase
from config import settings


# ── Rate limiter ──────────────────────────────────────────────────────────────
_login_attempts: dict = defaultdict(list)
MAX_ATTEMPTS = 10
WINDOW_SECS  = 300


def check_rate_limit(ip: str):
    now   = time.time()
    times = [t for t in _login_attempts[ip] if now - t < WINDOW_SECS]
    _login_attempts[ip] = times
    if len(times) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Wait {WINDOW_SECS // 60} minutes."
        )
    _login_attempts[ip].append(now)


# ── Startup ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate()
    init_db()
    print("\n✅ CampusConnect backend running")
    print("   Dashboard  → /dashboard")
    print("   Survey     → /survey")
    print("   Share/QR   → /share\n")
    yield


app = FastAPI(
    title="CampusConnect Survey API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)
TOKEN_EXPIRE_HOURS = 12


# ── Auth ──────────────────────────────────────────────────────────────────────
def create_token(payload: dict) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(
        {**payload, "exp": expiry, "iat": datetime.now(timezone.utc)},
        settings.JWT_SECRET,
        algorithm="HS256",
    )


def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired — please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ── File helper ───────────────────────────────────────────────────────────────
def _read_file(name: str) -> str:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    return HTMLResponse(content=_read_file("dashboard.html"))


@app.get("/survey", response_class=HTMLResponse, include_in_schema=False)
def serve_survey(request: Request):
    html   = _read_file("campus_survey.html")
    origin = str(request.base_url).rstrip("/")
    html   = html.replace(
        "const API_URL = 'http://localhost:8000';",
        f"const API_URL = '{origin}';"
    )
    return HTMLResponse(content=html)


@app.get("/share", response_class=HTMLResponse, include_in_schema=False)
def serve_share(request: Request):
    origin     = str(request.base_url).rstrip("/")
    survey_url = f"{origin}/survey"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Share CampusConnect Survey</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<style>
:root{{--bg:#0d0f14;--surface:#151820;--border:#252a3a;--accent:#4fffb0;--text:#e8eaf2;--muted:#6b7280}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:24px;padding:48px 40px;max-width:520px;width:100%;text-align:center}}
.logo{{font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:var(--accent);letter-spacing:.12em;text-transform:uppercase;margin-bottom:24px}}
h1{{font-family:'Syne',sans-serif;font-size:26px;font-weight:800;margin-bottom:10px}}
.sub{{color:var(--muted);font-size:14px;margin-bottom:36px;line-height:1.6}}
.qr-wrap{{background:#fff;border-radius:16px;padding:20px;display:inline-block;margin-bottom:32px}}
.url-box{{background:#0d0f14;border:1px solid var(--border);border-radius:12px;padding:14px 16px;font-size:13px;color:var(--accent);word-break:break-all;margin-bottom:16px;font-family:monospace;text-align:left}}
.btn{{display:inline-flex;align-items:center;gap:8px;font-family:'Syne',sans-serif;font-size:13px;font-weight:700;padding:13px 24px;border-radius:10px;cursor:pointer;border:none;text-decoration:none;transition:all .2s}}
.btn-primary{{background:var(--accent);color:#0d0f14;margin-right:8px}}
.btn-ghost{{background:transparent;color:var(--muted);border:1px solid var(--border)}}
.divider{{height:1px;background:var(--border);margin:32px 0}}
.tip{{font-size:12px;color:var(--muted);line-height:1.7}}
.tip strong{{color:var(--text)}}
.copied{{color:var(--accent);font-size:12px;margin-top:8px;height:16px}}
</style>
</head>
<body>
<div class="card">
  <div class="logo">◆ CampusConnect</div>
  <h1>Share the Survey</h1>
  <p class="sub">Anyone can fill this from any device, any network, anywhere — no WiFi restrictions.</p>
  <div class="qr-wrap" id="qrcode"></div>
  <div class="url-box">{survey_url}</div>
  <div class="copied" id="copiedMsg"></div>
  <div style="margin-top:16px">
    <button class="btn btn-primary" onclick="copyLink()">Copy Link</button>
    <button class="btn btn-ghost" onclick="downloadQR()">⬇ Download QR</button>
  </div>
  <div class="divider"></div>
  <p class="tip">
    <strong>WhatsApp/Instagram</strong> — paste the link directly.<br/>
    <strong>Notice board poster</strong> — download QR and print it.<br/>
    <strong>Works on mobile data</strong> — no college WiFi needed.
  </p>
  <div class="divider"></div>
  <a href="/dashboard" class="btn btn-ghost" style="margin-top:4px">← Back to Dashboard</a>
</div>
<script>
const SURVEY_URL = "{survey_url}";
new QRCode(document.getElementById("qrcode"), {{
  text: SURVEY_URL, width: 220, height: 220,
  colorDark: "#000000", colorLight: "#ffffff",
  correctLevel: QRCode.CorrectLevel.H
}});
function copyLink() {{
  navigator.clipboard.writeText(SURVEY_URL).then(() => {{
    const el = document.getElementById('copiedMsg');
    el.textContent = '✓ Copied!';
    setTimeout(() => el.textContent = '', 2000);
  }});
}}
function downloadQR() {{
  setTimeout(() => {{
    const canvas = document.querySelector('#qrcode canvas');
    if (!canvas) {{ alert('QR not ready, try again'); return; }}
    const a = document.createElement('a');
    a.download = 'campusconnect_qr.png';
    a.href = canvas.toDataURL('image/png');
    a.click();
  }}, 100);
}}
</script>
</body>
</html>"""
    return HTMLResponse(content=html)


# ── Submit survey ─────────────────────────────────────────────────────────────
@app.post("/api/survey", status_code=201)
def submit_survey(payload: SurveyResponse):
    try:
        client = get_supabase()
        data = {
            "submitted_at":    datetime.now(timezone.utc).isoformat(),
            "role":            payload.role,
            "year":            payload.year,
            "dept":            payload.dept,
            "discover":        payload.discover,
            "missed":          payload.missed,
            "comm_score":      payload.comm_score,
            "interests":       payload.interests,
            "ai_reco":         payload.ai_reco,
            "notif":           payload.notif,
            "notif_freq":      payload.notif_freq,
            "features":        payload.features,
            "privacy":         payload.privacy,
            "likely_score":    payload.likely_score,
            "biggest_problem": payload.biggest_problem,
            "wishlist":        payload.wishlist or "",
            "other":           payload.other or "",
        }
        client.table("responses").insert(data).execute()
        total = client.table("responses").select("id", count="exact").execute()
        return {"success": True, "total_responses": total.count or 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save: {e}")


# ── Dashboard login ───────────────────────────────────────────────────────────
@app.post("/api/dashboard/login", response_model=TokenResponse)
def dashboard_login(body: DashboardLogin, request: Request):
    ip = request.client.host if request.client else "unknown"
    check_rate_limit(ip)
    if not bcrypt.checkpw(
        body.password.encode("utf-8"),
        settings.DASHBOARD_PASSWORD_HASH.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Incorrect password")
    _login_attempts[ip] = []
    return {"access_token": create_token({"role": "dashboard"}), "token_type": "bearer"}


# ── Get responses ─────────────────────────────────────────────────────────────
@app.get("/api/dashboard/responses")
def get_responses(
    page:  int = 1,
    limit: int = 20,
    dept:  Optional[str] = None,
    role:  Optional[str] = None,
    _:     dict = Depends(verify_token),
):
    page  = max(1, page)
    limit = max(1, min(limit, 200))

    try:
        client = get_supabase()
        query  = client.table("responses").select("*", count="exact")
        if dept: query = query.eq("dept", dept)
        if role: query = query.eq("role", role)

        total_res = client.table("responses").select("id", count="exact")
        if dept: total_res = total_res.eq("dept", dept)
        if role: total_res = total_res.eq("role", role)
        total = total_res.execute().count or 0

        offset = (page - 1) * limit
        rows   = query.order("submitted_at", desc=True).range(offset, offset + limit - 1).execute()

        return {
            "total": total,
            "page":  page,
            "limit": limit,
            "pages": max(1, -(-total // limit)),
            "data":  rows.data or [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Stats for charts ──────────────────────────────────────────────────────────
@app.get("/api/dashboard/stats")
def get_stats(_: dict = Depends(verify_token)):
    try:
        client   = get_supabase()
        result   = client.table("responses").select("*").execute()
        all_rows = result.data or []
        total    = len(all_rows)

        if total == 0:
            return {"total": 0, "today": 0, "avg_comm_score": 0,
                    "avg_likely_score": 0, "charts": {}}

        def count_field(field):
            c = {}
            for r in all_rows:
                v = r.get(field, "") or ""
                c[v] = c.get(v, 0) + 1
            return dict(sorted(c.items(), key=lambda x: -x[1]))

        def count_multi(field):
            c = {}
            for r in all_rows:
                items = r.get(field, []) or []
                if isinstance(items, str):
                    try: items = json.loads(items)
                    except: items = []
                for item in items:
                    c[item] = c.get(item, 0) + 1
            return dict(sorted(c.items(), key=lambda x: -x[1]))

        def avg(field):
            vals = [int(r[field]) for r in all_rows if r.get(field)]
            return round(sum(vals) / len(vals), 2) if vals else 0

        today       = datetime.now(timezone.utc).date().isoformat()
        today_count = sum(1 for r in all_rows if (r.get("submitted_at") or "").startswith(today))

        daily: dict = {}
        for r in all_rows:
            day = (r.get("submitted_at") or "")[:10]
            if day: daily[day] = daily.get(day, 0) + 1

        return {
            "total":            total,
            "today":            today_count,
            "avg_comm_score":   avg("comm_score"),
            "avg_likely_score": avg("likely_score"),
            "charts": {
                "by_role":           count_field("role"),
                "by_dept":           count_field("dept"),
                "by_year":           count_field("year"),
                "missed":            count_field("missed"),
                "ai_reco":           count_field("ai_reco"),
                "privacy":           count_field("privacy"),
                "notif_freq":        count_field("notif_freq"),
                "discover":          count_multi("discover"),
                "interests":         count_multi("interests"),
                "notif":             count_multi("notif"),
                "features":          count_multi("features"),
                "daily_submissions": dict(sorted(daily.items())),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Export CSV ────────────────────────────────────────────────────────────────
@app.get("/api/dashboard/export")
def export_csv(_: dict = Depends(verify_token)):
    import csv, io
    try:
        client = get_supabase()
        rows   = client.table("responses").select("*").order("submitted_at", desc=True).execute()
        data   = rows.data or []
        if not data:
            raise HTTPException(status_code=404, detail="No responses to export yet")

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            r = dict(row)
            for f in ("discover", "interests", "notif", "features"):
                val = r.get(f, [])
                if isinstance(val, list):
                    r[f] = ", ".join(val)
            writer.writerow(r)

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition":
                     "attachment; filename=campusconnect_responses.csv"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Delete response ───────────────────────────────────────────────────────────
@app.delete("/api/dashboard/responses/{response_id}")
def delete_response(response_id: int, _: dict = Depends(verify_token)):
    try:
        client = get_supabase()
        result = client.table("responses").delete().eq("id", response_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Response not found")
        return {"success": True, "deleted_id": response_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
