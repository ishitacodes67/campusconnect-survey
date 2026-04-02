# CampusConnect — Survey Backend

FastAPI + SQLite backend for the CampusConnect student survey.
Includes a password-protected dashboard to view, filter, and export responses.

---

## Folder Structure

```
backend/
├── main.py           ← FastAPI app — all API routes
├── models.py         ← Pydantic validation models
├── database.py       ← SQLite connection + table creation
├── config.py         ← Reads settings from .env
├── setup.py          ← Run ONCE to create your password + .env
├── dashboard.html    ← Dashboard UI (served at http://localhost:8000)
├── requirements.txt  ← Python dependencies
└── .gitignore        ← Keeps .env and .db off GitHub ✓
```

The database file `campusconnect.db` is created automatically on first run.

---

## Setup (Do this ONCE)

### Step 1 — Make sure Python 3.10+ is installed
```bash
python --version
```

### Step 2 — Create a virtual environment (recommended)
```bash
# Navigate into the backend folder
cd backend

# Create venv
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run setup to create your dashboard password
```bash
python setup.py
```
This will ask you to set a shared password, then write a `.env` file with:
- A bcrypt hash of your password (the raw password is never stored)
- A random JWT secret key

**Share the password with Radhika and Maitrey — they'll use it to log into the dashboard.**

### Step 5 — Start the server
```bash
python main.py
```

You'll see:
```
✅ CampusConnect backend running
   Dashboard → http://localhost:8000
   API docs  → http://localhost:8000/docs
```

---

## Using the Dashboard

1. Open **http://localhost:8000** in your browser
2. Enter the shared password
3. You'll see:
   - **Analytics tab** — charts for every question (role breakdown, interests, features wanted, notification preferences, daily submissions, etc.)
   - **All Responses tab** — full table with filters by department and role
   - Click **"View all"** on any row to see the complete response in a popup
   - Click **"⬇ Export CSV"** in the top bar to download all responses as a spreadsheet

---

## Connecting the Survey Form

The `campus_survey.html` file already POSTs to `http://localhost:8000/api/survey`.

**When sharing the survey with students:**
- Both the survey HTML and the backend server must be accessible from the same network
- If running locally: students need to be on the same WiFi, and you need to find your local IP (see below)
- Replace `localhost` with your local IP in `campus_survey.html` line with `fetch('http://localhost:8000/api/survey'...)`

**Finding your local IP:**
```bash
# Windows
ipconfig

# Mac/Linux
ifconfig
```
Example: if your IP is `192.168.1.5`, change the survey fetch URL to `http://192.168.1.5:8000/api/survey`

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/survey` | None | Submit a survey response |
| POST | `/api/dashboard/login` | None | Get dashboard JWT token |
| GET | `/api/dashboard/responses` | JWT | Paginated response list |
| GET | `/api/dashboard/stats` | JWT | Aggregated stats + chart data |
| GET | `/api/dashboard/export` | JWT | Download CSV of all responses |
| DELETE | `/api/dashboard/responses/{id}` | JWT | Delete a single response |

---

## Security Notes

- The dashboard password is hashed with **bcrypt (12 rounds)** — even if someone finds your `.env`, they can't recover the password
- The `.env` file and `.db` database are both in `.gitignore` — they will **never** be pushed to GitHub
- JWT tokens are stateless — logging out just removes the token from the browser
- All dashboard endpoints require a valid JWT — no token, no data
- Input validation via Pydantic rejects any malformed survey submissions before they touch the database

---

## Troubleshooting

**"Cannot connect to backend" on login screen**
→ Make sure `python main.py` is running in your terminal

**Students can't submit the survey**
→ Replace `localhost` in the survey HTML with your actual local IP address

**"Module not found" error on start**
→ Run `pip install -r requirements.txt` and make sure your venv is activated

**Forgot the dashboard password**
→ Run `python setup.py` again and overwrite the `.env` file

**Port 8000 already in use**
→ Change the port in the last line of `main.py`: `uvicorn.run("main:app", port=8001, ...)`
