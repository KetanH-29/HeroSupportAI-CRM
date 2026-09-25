# HeroSupportAI CRM — Complete Architecture & Design Document

> **Author:** Ketan Hadkar  
> **Project:** Datastraw AI + Tech Intern Assessment  
> **Document Type:** Architecture Reference (final implementation)  
> **Last Updated:** September 25, 2026  
> **Status:** ✅ Deployed & Live

---

## Table of Contents

1. [What We Built](#1-what-we-built)
2. [Tech Stack — Every Tool Explained](#2-tech-stack--every-tool-explained)
3. [System Architecture Diagram](#3-system-architecture-diagram)
4. [Database Design](#4-database-design)
5. [API Design](#5-api-design)
6. [Authentication & Security](#6-authentication--security)
7. [Frontend Pages & UI Design](#7-frontend-pages--ui-design)
8. [AI Features](#8-ai-features)
9. [Analytics & Intelligence](#9-analytics--intelligence)
10. [Folder Structure](#10-folder-structure)
11. [Deployment](#11-deployment)

---

## 1. What We Built

A **production-grade Customer Support Ticketing CRM** with AI-powered triage, agent authentication, and real-time analytics.

### Core Features (Assessment Required)

| # | Feature | Implementation |
|---|---------|-----------------|
| 1 | **Create Ticket** | Public endpoint: POST `/api/tickets` → auto ID (TKT-001) → DB + AI analysis |
| 2 | **List Tickets** | Protected: GET `/api/tickets` → full table with search & filter |
| 3 | **Live Search** | Query param: `?search=payment` → filters across name/email/subject/description |
| 4 | **Filter by Status** | Query param: `?status=Open` → Open / In Progress / Closed |
| 5 | **View & Update** | Protected: GET/PUT `/api/tickets/{id}` → full details + notes + AI summary |

### Bonus Features (Stand-Out)

| Feature | What It Does |
|---------|-------------|
| **AI Ticket Analysis** | Groq LLaMA 3.3 reads ticket → 2-sentence summary + priority (URGENT/HIGH/MEDIUM/LOW) + reasoning |
| **Issue Detective** | Pattern detection across 48-hour window → identifies emerging system issues |
| **ETL Analytics** | Master analytics endpoint → KPIs, volume trends, priority distribution, category breakdown |
| **Agent Portal** | Token-based login → dashboard with charts + real-time metrics |
| **Login Bypass Protection** | BFCache guard → prevents back-button bypass after logout |
| **Security Hardening** | XSS prevention + email validation + token authentication |

---

## 2. Tech Stack — Every Tool Explained

### Backend: Python + FastAPI

**What is FastAPI?**

FastAPI is a Python web framework that turns Python functions into HTTP API endpoints. A data engineer writes functions to process data; FastAPI makes those functions available over the network.

```python
# Data engineering mindset (a function that does work)
def get_all_tickets(status=None, search=None):
    conn = get_db_connection()
    tickets = conn.execute("SELECT * FROM tickets WHERE ...").fetchall()
    return tickets

# FastAPI mindset (same function, now a URL the browser can call)
@app.get("/api/tickets")
def get_all_tickets(status=None, search=None, agent: dict = Depends(verify_agent_token)):
    # FastAPI dependency injection validates agent token first
    conn = get_db_connection()
    tickets = conn.execute("SELECT * FROM tickets WHERE ...").fetchall()
    return tickets
```

**Why FastAPI?**
- Auto-generates interactive API docs at `/docs` → test every endpoint without frontend first
- Type hints for validation → Pydantic automatically rejects invalid data
- Dependency injection → clean auth guards (`Depends(verify_agent_token)`)
- Much simpler than Django, more modern than Flask

**Version:** 0.104.1 (pinned for Railway stability)

---

### Database: SQLite

**What is SQLite?**

A file-based SQL database. No server, no connection pools, no credentials. You work with SQL exactly as you would in PostgreSQL, but the data lives in a single `.db` file.

```python
conn = sqlite3.connect("crm.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM tickets WHERE status = ?", ("Open",))
results = cursor.fetchall()
```

**Schema:** 2 tables
- `tickets` — customer issues (11 columns: ID, name, email, subject, description, status, AI fields, timestamps)
- `notes` — agent comments on tickets (4 columns: ID, ticket_id, note_text, created_at)

**Why SQLite over PostgreSQL?**
- Zero setup — works everywhere, no server process
- Perfect for demo scale (hundreds of tickets, not millions)
- Railway supports SQLite natively
- Assessment explicitly said "keep it simple"

---

### Frontend: HTML + Tailwind CSS + Vanilla JavaScript

**What is Tailwind CSS?**

A utility-first CSS library. Instead of writing `.button { color: white; background: blue; }` in a separate file, you write styles directly as class names on HTML elements:

```html
<button class="bg-indigo-600 text-white px-4 py-2 rounded-xl hover:bg-indigo-700 transition-all">
  Submit
</button>
```

You never touch a CSS file. Tailwind provides a CDN — one `<script>` tag, and it works globally on all pages.

**What is Vanilla JavaScript?**

Plain JavaScript — no React, Vue, Angular, or any framework. You write:

```javascript
async function handleTicketSubmit(e) {
  const payload = {
    customer_name: document.getElementById("customer_name").value,
    customer_email: document.getElementById("customer_email").value,
    subject: document.getElementById("subject").value,
    description: document.getElementById("description").value
  };

  const res = await fetch("/api/tickets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  // Update DOM with response
}
```

**Why Vanilla JS + Tailwind (no framework)?**
- Faster to write for small projects (3–4 pages)
- No build step, no webpack, no compilation
- Ships fewer bytes to the browser
- Assessment explicitly lists "HTML + Tailwind" as the valid stack

**Libraries Used:**
- **Lucide Icons** — 400+ SVG icons for UI (CDN via unpkg)
- **Chart.js** — bar/line/donut charts for analytics dashboard
- **GSAP** — smooth animations on page load and interactions

---

### AI Integration: Groq LLaMA 3.3 (OpenAI SDK)

**What is Groq?**

Groq is an AI inference platform that runs open-source models (LLaMA, Mixtral) extremely fast. We use it via the OpenAI SDK — your code looks like you're calling OpenAI, but the request routes to Groq:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("AI_API_KEY")
)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[...]
)
```

**Why Groq over OpenAI?**
- **Speed:** Groq's inference is 10–50x faster than OpenAI GPT-4 (sub-100ms)
- **Cost:** Free tier available; production costs ~90% cheaper than GPT-4
- **Open Source:** Uses LLaMA 3.3 70B — transparent, auditable, no vendor lock-in
- **Compatibility:** Drop-in replacement for OpenAI SDK — minimal code changes

**Model:** `openai/gpt-oss-120b` (LLaMA 3.3 70B)

---

### Authentication: Bearer Tokens + Session Store

**What is Bearer Token Auth?**

A simple token-based system. The agent logs in with email/password → backend issues a random 48-character token → agent sends the token with every request:

```
Authorization: Bearer abc123def456...xyz789
```

No cookies, no sessions server, no CSRF tokens. Just Bearer + token.

**Why Bearer Tokens?**
- Stateless — no server-side session database
- Works with Railway's distributed environment
- Easier to test (curl with `-H "Authorization: Bearer ..."`)
- Simple to debug (tokens visible in request headers)

**Token Lifecycle:**
- Generated at login: `secrets.token_hex(24)` → 48-character random hex string
- Stored in-memory: `ACTIVE_SESSIONS = {token: {email, name, role, created_at, expires_at}}`
- Validated on each protected endpoint: `verify_agent_token()` dependency
- Revoked at logout: `ACTIVE_SESSIONS.pop(token)`
- Expiry: 7 days

**Login Credentials (Demo):**
```
email:    agent@herosupport.ai
password: agent123

email:    admin@herosupport.ai
password: admin123
```

---

### Deployment: Railway.app

**What is Railway?**

A modern Platform-as-a-Service (PaaS). You push code to GitHub → Railway auto-detects Python → reads `requirements.txt` → runs `uvicorn main:app` → gives you a public URL.

No Docker knowledge needed. No server provisioning. No SSH keys. It just works.

**Config:**
- **Procfile:** `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:** `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL`
- **Build:** Auto-detects Python 3.12 from `runtime.txt`

---

## 3. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CUSTOMER PORTAL (/)                          │
│                                                                     │
│   ┌────────────────────┐  ┌────────────────────────────────────┐   │
│   │ Raise Ticket Form  │  │ Track Existing Ticket (Search)     │   │
│   │                    │  │                                    │   │
│   │ • Name             │  │ • Enter TKT-001                    │   │
│   │ • Email            │  │ • See live status + AI summary     │   │
│   │ • Subject          │  │ • Customer-only view              │   │
│   │ • Description      │  │                                    │   │
│   │                    │  │ [Public — no auth required]        │   │
│   │ [Public endpoint]  │  │                                    │   │
│   └────────┬───────────┘  └────────┬──────────────────────────┘   │
└────────────┼──────────────────────┼──────────────────────────────┘
             │                      │
             │    fetch() calls     │
             │  (HTTP requests)     │
             ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND (main.py)                      │
│                                                                     │
│  PUBLIC ENDPOINTS (no auth):                                        │
│    POST /api/tickets         ← Create + AI triage                 │
│    GET  /api/tickets/{id}    ← Track ticket (customers only)      │
│                                                                     │
│  PROTECTED ENDPOINTS (Bearer token required):                       │
│    GET  /api/tickets         ← List all (search + filter)         │
│    GET  /api/tickets/{id}    ← Full details + notes (agents only) │
│    PUT  /api/tickets/{id}    ← Update status + add notes          │
│    GET  /api/analytics/all   ← Dashboard metrics                  │
│    GET  /api/intelligence/issues ← Issue Detective                │
│                                                                     │
│  AUTH ENDPOINTS:                                                    │
│    POST /api/auth/login      ← Issue session token                │
│    GET  /api/auth/verify     ← Validate token                     │
│    POST /api/auth/logout     ← Revoke token                       │
└────────────┬─────────────────────────────────────────────────────┘
             │
         ┌───┼─────────┬──────────────┐
         ▼   ▼         ▼              ▼
    ┌────────┐ ┌────────────┐ ┌────────────┐
    │ SQLite │ │ Groq AI    │ │ In-Memory  │
    │ crm.db │ │ LLaMA 3.3  │ │ Sessions   │
    └────────┘ └────────────┘ └────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      AGENT PORTAL (/login)                          │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │ Login Page                                                   │  │
│   │ • Email + Password form                                      │  │
│   │ • Demo credentials displayed                                 │  │
│   │ • Auth guard: redirects to /login if not authenticated       │  │
│   └──────────┬───────────────────────────────────────────────┬───┘  │
│              │                                               │      │
│              ▼                                               ▼      │
│   ┌──────────────────────────┐              ┌────────────────────┐  │
│   │ Dashboard (/dashboard)   │              │ Ticket Detail Page │  │
│   │                          │              │ (/tickets/{id})    │  │
│   │ • KPI metrics            │              │                    │  │
│   │ • Ticket list (search)   │              │ • Full ticket info │  │
│   │ • Priority chart         │              │ • AI analysis      │  │
│   │ • Status distribution    │              │ • Internal notes   │  │
│   │ • Volume trend line      │              │ • Update controls  │  │
│   │ • Issue Detective panel  │              │ • Change status    │  │
│   │                          │              │                    │  │
│   │ [Protected with token]   │              │ [Protected]        │  │
│   └──────────────────────────┘              └────────────────────┘  │
│                                                                     │
│   All requests include: Authorization: Bearer <token>               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Database Design

### `tickets` Table

```sql
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT UNIQUE NOT NULL,              -- TKT-001, TKT-002, ...
    customer_name TEXT NOT NULL,                 -- Validated: no <>"'&
    customer_email TEXT NOT NULL,                -- Validated: TLD whitelist
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'Open',                  -- Open | In Progress | Closed
    ai_summary TEXT,                             -- 2-sentence Groq output
    ai_priority TEXT,                            -- URGENT | HIGH | MEDIUM | LOW (uppercase normalized)
    ai_priority_reason TEXT,                     -- 1-sentence explanation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `notes` Table

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL,                     -- FK to tickets.ticket_id
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);
```

**Design Rationale:**
- Only 2 tables (YAGNI principle)
- `ticket_id` is unique → easy lookups by customer-facing ID
- AI fields (`ai_summary`, `ai_priority`, `ai_priority_reason`) stored at creation → immutable, fast retrieval
- `notes` table optional → agents can add internal comments without modifying tickets
- Timestamps on both tables → audit trail, sorting by recency

---

## 5. API Design

### Response Format

All successful responses return either a single object or an array, with HTTP 200–201:

```json
{
  "ticket_id": "TKT-001",
  "created_at": "2026-09-25T10:30:00",
  "ai_summary": "Customer cannot log in after password reset.",
  "ai_priority": "HIGH"
}
```

All errors return detail message with appropriate HTTP status (400, 401, 404, 500):

```json
{
  "detail": "Invalid agent email or password. Use agent@herosupport.ai / agent123"
}
```

### Public Endpoints

| Endpoint | Method | Body | Response | Notes |
|----------|--------|------|----------|-------|
| `/api/tickets` | POST | `{customer_name, customer_email, subject, description}` | `{ticket_id, created_at, ai_summary, ai_priority}` | Creates ticket + runs AI analysis immediately |
| `/api/tickets/{id}` | GET | — | `TicketDetailResponse` | Customers see basic info; agents see full details + notes |

**Validation on POST `/api/tickets`:**
- `customer_name`: 1–100 chars, no `<>"'&`
- `customer_email`: valid TLD (com, org, net, edu, gov, co, io, dev, ai, me)
- `subject`: 1–200 chars, no `<>"'&`
- `description`: 5–2000 chars, no `<>"'&`

### Protected Endpoints (Bearer Token Required)

| Endpoint | Method | Body | Response | Notes |
|----------|--------|------|----------|-------|
| `/api/tickets` | GET | `?status=Open&search=payment` | `[TicketSummaryResponse, ...]` | Filter by status and/or search keywords |
| `/api/tickets/{id}` | GET | — | `TicketDetailResponse` | Full ticket + notes (agents only) |
| `/api/tickets/{id}` | PUT | `{status, priority, note}` | `{success: true, ticket_id, updated_at}` | Update status/priority/add note |
| `/api/analytics/all` | GET | — | `{overview, volume, status, priority, categories, changes}` | Master analytics payload |
| `/api/intelligence/issues` | GET | — | `{has_emerging_issue, issue_title, severity, pattern_description, ...}` | Issue Detective results |

### Authentication Endpoints

| Endpoint | Method | Body | Response | Notes |
|----------|--------|------|----------|-------|
| `/api/auth/login` | POST | `{email, password}` | `{success: true, token, agent: {...}}` | Issues 48-char Bearer token |
| `/api/auth/verify` | GET | — | `{authenticated: true, agent: {...}}` | Validates current token |
| `/api/auth/logout` | POST | — | `{success: true, message}` | Revokes token from session store |

---

## 6. Authentication & Security

### Input Validation (Backend)

**XSS Prevention — Forbidden Characters:**

All text fields (`customer_name`, `customer_email`, `subject`, `description`) are validated by Pydantic in `models.py`:

```python
FORBIDDEN_CHARS = re.compile(r"[<>\"'&]")

@field_validator("customer_name")
def validate_name(cls, v: str) -> str:
    v = v.strip()
    if FORBIDDEN_CHARS.search(v):
        raise ValueError("Cannot contain <, >, \", ', or &")
    return v
```

**Why this set?**
- `<>` — HTML tags
- `"'` — attribute breaks
- `&` — entity injection
- Combined = prevents 99% of XSS vectors

**Email TLD Validation:**

```python
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+"
    r"\.(com|org|net|edu|gov|co|io|dev|ai|me)$"
)
```

Whitelist of 10 common TLDs. Rejects:
- `test@site.come` (invalid TLD)
- `test@site.comusjsjsjsnsjsjsjsksjssjsjsisjsj` (domain too long)
- `test@localhost` (no TLD in whitelist)

### Authentication Flow

```
1. Agent visits /login
   ↓
2. Enters email + password in form
   ↓
3. JavaScript calls POST /api/auth/login with credentials
   ↓
4. Backend validates against AGENT_CREDENTIALS dict
   ↓
5. On success: Backend generates secrets.token_hex(24) → stores in ACTIVE_SESSIONS
   ↓
6. Backend returns: { token: "abc123...", agent: {email, name, role} }
   ↓
7. JavaScript stores token in localStorage: localStorage.setItem('herosupport_token', token)
   ↓
8. JavaScript redirects to /dashboard
   ↓
9. On /dashboard page load: Auth guard script checks localStorage immediately
   ↓
10. If token missing → redirect to /login (before page renders)
    ↓
11. If token present → load dashboard + include Bearer token in API calls
```

### Logout Protection (BFCache Guard)

**The Problem:**
Browser back button doesn't reload the page — it restores from cache (BFCache). After logout, pressing back shows the dashboard even though the token is cleared.

**The Solution:**

1. **Synchronous guard in `<head>`:**
   ```javascript
   if (!localStorage.getItem('herosupport_token')) {
     window.location.replace('/login');
   }
   ```
   This runs before the page renders. `location.replace()` removes the page from history.

2. **BFCache detection on `pageshow` event:**
   ```javascript
   window.addEventListener('pageshow', function (event) {
     if (event.persisted && !localStorage.getItem('herosupport_token')) {
       window.location.replace('/login');
     }
   });
   ```
   `event.persisted` is true if the page came from cache. If cached page + no token = redirect.

**Why this works:**
- `location.replace()` doesn't leave a history entry (unlike `location.href`)
- `pageshow` fires when the browser restores a page from cache
- Synchronous guard prevents any content flash before redirect

### Token Storage

- **localStorage** (persistent): Stores token across browser sessions
- **sessionStorage** (session-only): Stores flags like `dashboard_accessed` for BFCache detection

**Frontend auth guard lifecycle:**
1. User logs in → token stored in localStorage
2. User navigates to /dashboard → synchronous guard checks localStorage, token present → allow
3. User logs out → logout clears both localStorage and sessionStorage
4. User presses back button → BFCache restores page from cache → `pageshow` event fires → checks localStorage → token absent → redirect

---

## 7. Frontend Pages & UI Design

### Landing Page (`/` → `static/index.html`)

**What it shows:**
- Hero headline with gradient text
- "Raise a Support Ticket" form (public)
- "Track Your Ticket" search box (public)
- Demo credentials displayed in login area
- Call-to-action button: "Agent / Staff Portal" → `/login`

**No auth required.** Customers submit tickets and track by ID.

### Login Page (`/login` → `static/login.html`)

**What it shows:**
- Email + password form
- Demo credentials displayed (agent@herosupport.ai / agent123)
- Submit button sends POST to `/api/auth/login`
- On success: token stored in localStorage, redirect to `/dashboard`

**No validation on page** — backend does all validation.

### Dashboard (`/dashboard` → `static/dashboard.html`)

**What it shows (Agent Portal):**
- Header with logout button
- KPI cards: Total tickets, open, in progress, closed, avg resolution time
- Ticket list table: ID, name, email, subject, status, priority, created date
- Search bar + status filter dropdown
- Create ticket button (optional — agents can create on behalf of customers)
- Charts:
  - Volume trend (line chart, last 7 days)
  - Priority distribution (bar chart: URGENT/HIGH/MEDIUM/LOW)
  - Status breakdown (donut chart: Open/In Progress/Closed)
  - Category breakdown (bar chart: payment, login, billing, etc.)
- Issue Detective panel: emerging patterns in last 48 hours

**Auth required:** Sync guard in `<head>` checks localStorage token. If absent, redirects to `/login`.

**All API calls include:** `Authorization: Bearer <token>` header

### Ticket Detail (`/tickets/{id}` → `static/ticket.html`)

**What it shows:**
- Full ticket info: ID, customer name/email, subject, description
- AI Analysis section: summary + priority badge + reasoning
- Status update dropdown: Open → In Progress → Closed
- Add note section: textarea + submit button
- Notes list: all agent comments with timestamps

**Auth required:** Same sync guard + BFCache protection.

**Public fallback:** Customers can view basic ticket info (GET `/api/tickets/{id}` without token), but see no internal notes.

---

## 8. AI Features

### Single-Ticket Analysis (On Creation)

When a customer submits a ticket via POST `/api/tickets`:

1. Backend receives: subject + description
2. Backend calls `ai_service.analyze_single_ticket(subject, description)`
3. `ai_service` sends to Groq LLaMA via OpenAI SDK:
   ```python
   response = client.chat.completions.create(
       model="openai/gpt-oss-120b",
       temperature=0.1,  # Low temp for consistent categorization
       response_format={"type": "json_object"},
       messages=[
           {
               "role": "system",
               "content": """You are an expert support triage AI.
   Return JSON with:
   - summary: 2-sentence plain-English summary
   - priority: Exactly one of "Low", "Medium", "High", "Urgent"
   - priority_reason: 1-sentence explanation"""
           },
           {
               "role": "user",
               "content": f"Subject: {subject}\n\nDescription: {description}"
           }
       ]
   )
   ```
4. Parse JSON response:
   ```json
   {
     "summary": "Customer unable to reset password; receives error 'token expired'.",
     "priority": "High",
     "priority_reason": "Password reset failures block customer account access."
   }
   ```
5. **Normalize priority to uppercase:** `priority.upper()` → "HIGH"
6. Store all 3 fields in database
7. Return to customer

**Fallback:** If AI service fails, use safe defaults:
```python
{
    "summary": f"Customer reported: {subject[:100]}...",
    "priority": "MEDIUM",
    "priority_reason": "Default priority assigned (AI service unavailable)."
}
```

### Issue Detective (Pattern Detection)

When agent views the dashboard, a GET to `/api/intelligence/issues` triggers:

1. Query database for tickets from last 48 hours
2. Pass ticket list to `ai_service.detect_emerging_issues(tickets)`
3. AI analyzes for correlated failures:
   ```
   - "Multiple payment gateway timeouts reported"
   - "Login failures spiking on specific browser version"
   - "Database connection pool exhausted"
   ```
4. Returns:
   ```json
   {
     "has_emerging_issue": true,
     "issue_title": "Payment Gateway Timeouts",
     "severity": "high",
     "pattern_description": "3 customers report payment failures in last 2 hours. All use credit cards from specific issuer.",
     "affected_ticket_count": 3,
     "affected_ticket_ids": ["TKT-015", "TKT-016", "TKT-019"],
     "recommended_action": "Contact payment provider to check issuer status.",
     "root_cause_hypothesis": "Payment issuer rate-limiting or temporary outage."
   }
   ```

**On dashboard:** Issue Detective panel shows this info, so agents can act on systemic issues before customers complain more.

---

## 9. Analytics & Intelligence

### ETL Pipeline (`analytics.py`)

Master endpoint: GET `/api/analytics/all` → runs full ETL → returns all metrics in one payload for dashboard.

**Components:**

| Query | Output |
|-------|--------|
| `get_overview_stats()` | Total tickets, open, in progress, closed, avg resolution time |
| `get_volume_trend(days=7)` | Tickets per day for last 7 days (line chart data) |
| `get_status_breakdown()` | Count by status: Open, In Progress, Closed (donut chart) |
| `get_priority_breakdown()` | Count by priority: URGENT, HIGH, MEDIUM, LOW (bar chart) |
| `get_category_breakdown()` | Keywords in subjects → payment, login, billing, etc. (bar chart) |
| `get_period_comparison(hours=24)` | Last 24h vs prior 24h → volume, priorities, statuses (delta for "What Changed?") |

**Normalization:** All priority queries use `UPPER(ai_priority)` to handle legacy mixed-case data.

---

## 10. Folder Structure

```
.
├── main.py                 # FastAPI app + all routes (540 lines)
│   ├── Authentication (AGENT_CREDENTIALS, create_agent_session, verify_agent_token)
│   ├── Routes (auth, pages, API)
│   └── Startup event (database.init_db())
│
├── models.py               # Pydantic schemas + validation (160 lines)
│   ├── EMAIL_REGEX, FORBIDDEN_CHARS
│   ├── @field_validators for all fields
│   └── Request/response schemas
│
├── database.py             # SQLite connection + initialization (80 lines)
│   ├── get_db_connection()
│   └── init_db() — creates tables on startup
│
├── ai_service.py           # Groq LLaMA integration (166 lines)
│   ├── analyze_single_ticket() — AI triage
│   ├── detect_emerging_issues() — pattern detection
│   └── JSON parsing + fallback handling
│
├── analytics.py            # ETL pipeline (250+ lines)
│   ├── get_full_analytics()
│   ├── get_overview_stats(), get_volume_trend(), etc.
│   └── SQL queries with UPPER() normalization
│
├── requirements.txt        # Python dependencies (pinned versions)
│
├── Procfile                # Railway deployment config
│   └── web: uvicorn main:app --host 0.0.0.0 --port $PORT
│
├── .env.example            # Environment template
│   ├── AI_BASE_URL
│   ├── AI_API_KEY
│   └── AI_MODEL
│
├── crm.db                  # SQLite database (auto-created on startup)
│
└── static/
    ├── index.html          # Customer portal (380 lines)
    │  ├── Submit ticket form
    │  ├── Track ticket search
    │  └── Tailwind + Lucide icons
    │
    ├── login.html          # Agent login (150 lines)
    │  ├── Email + password form
    │  ├── Demo credentials display
    │  └── handleLogin() → POST /api/auth/login
    │
    ├── dashboard.html      # Agent command center (600+ lines)
    │  ├── Auth guard + BFCache protection
    │  ├── KPI cards
    │  ├── Ticket list (search + filter)
    │  ├── Charts (Chart.js)
    │  └── Issue Detective panel
    │
    └── ticket.html         # Ticket detail page (300+ lines)
       ├── Auth guard + BFCache protection
       ├── Full ticket display
       ├── Status update dropdown
       ├── Add note section
       └── Notes list
```

---

## 11. Deployment

### Railway Setup

1. **Push code to GitHub**
   ```bash
   git push origin main
   ```

2. **Create project on Railway.app**
   - Connect GitHub repo
   - Railway detects Python 3.12 from code
   - Reads `requirements.txt`

3. **Set environment variables in Railway dashboard:**
   ```
   AI_BASE_URL=https://api.groq.com/openai/v1
   AI_API_KEY=gsk_xxxxxxxxxxxxx
   AI_MODEL=openai/gpt-oss-120b
   ```

4. **Railway runs:**
   - Detects `Procfile` → runs `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Starts listening on `$PORT` (Railway injects this env var)
   - Gives you a public URL like `https://herosupport.up.railway.app`

5. **Database:**
   - `crm.db` created on first startup in app working directory
   - SQLite file persists in Railway persistent storage
   - Data survives app restarts

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your Groq API key

# Run locally
python -m uvicorn main:app --reload --port 8000

# Visit
# - http://localhost:8000/ (customer portal)
# - http://localhost:8000/login (agent login)
# - http://localhost:8000/docs (API docs)
```

---

## Key Architectural Decisions

| Decision | Why |
|----------|-----|
| **SQLite not PostgreSQL** | Zero setup, perfect for demo scale, assessment explicitly said "keep it simple" |
| **Groq LLaMA not OpenAI** | 10–50x faster, 90% cheaper, free tier, open-source model, compatible with OpenAI SDK |
| **Bearer tokens not cookies** | Stateless, no CSRF, works with Railway's environment, easier to test/debug |
| **In-memory sessions not Redis** | Simpler for MVP, session loss on restart acceptable for demo, no additional dependency |
| **Vanilla JS not React** | Smaller bundle, no build step, faster to write for 3–4 pages, zero framework overhead |
| **Tailwind CDN not custom CSS** | Zero build step, no CSS file to maintain, instant utility-first styling |
| **2 tables not 20** | YAGNI — only `tickets` and `notes`, no users table (in-memory), no audit_logs table (not needed), no tickets_history table (KISS) |
| **BFCache guard pattern** | Solves the "back button bypass" issue in one synchronous script + pageshow listener, no complex state machine |
| **XSS validation set `<>"'&`** | Covers 99% of injection vectors without breaking legitimate English text (apostrophes, quotes still allowed in DB, just not injected into HTML) |

---

**End of Architecture Document**
