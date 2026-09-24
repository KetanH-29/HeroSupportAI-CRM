# Datastraw CRM System — Complete Architecture & Design Document

> **Author:** Ketan Hadkar  
> **Project:** Datastraw AI + Tech Intern Assessment  
> **Document Type:** Architecture Reference (read this before touching any code)  
> **Last Updated:** September 22, 2026

---

## Table of Contents

1. [What We Are Building](#1-what-we-are-building)
2. [Tech Stack — Every Tool Explained](#2-tech-stack--every-tool-explained)
3. [System Architecture Diagram](#3-system-architecture-diagram)
4. [Database Design](#4-database-design)
5. [API Design](#5-api-design)
6. [Frontend Pages & UI Design](#6-frontend-pages--ui-design)
7. [Motion Primitives & Animation Plan](#7-motion-primitives--animation-plan)
8. [AI Feature — Summary + Priority](#8-ai-feature--summary--priority)
9. [Folder Structure](#9-folder-structure)
10. [Build Order (Component by Component)](#10-build-order-component-by-component)
11. [Deployment Plan](#11-deployment-plan)

---

## 1. What We Are Building

A **Customer Support Ticketing CRM** — a web application that lets a support team manage customer issues end-to-end.

### The 5 Required Features (Assessment Mandatory)

| # | Feature | What It Does |
|---|---------|-------------|
| 1 | **Create Ticket** | Form → auto ID (TKT-001) → saved to DB |
| 2 | **List All Tickets** | Dashboard table: ID, Name, Subject, Status, Date |
| 3 | **Live Search** | Type → filter tickets by name/email/ID/description |
| 4 | **Filter by Status** | Show only Open / In Progress / Closed |
| 5 | **View & Update** | Click ticket → full details → change status + add notes |

### The Bonus Feature (Stand-Out)

| Feature | What It Does |
|---------|-------------|
| **AI Summary + Suggested Priority** | When a ticket is created, Claude reads the description and returns: (a) a 2-sentence plain-English summary of the issue, and (b) a suggested priority (Low / Medium / High / Urgent) with a one-line reason why. Both are stored and shown on the ticket. |

---

## 2. Tech Stack — Every Tool Explained

### Why These Tools (For a Data Engineer)

As a data engineer you are comfortable with Python and SQL. Every choice below maps to something you already understand or is the simplest possible version of the concept.

---

### Backend: Python + FastAPI

**What is FastAPI?**

FastAPI is a Python library that lets you turn Python functions into API endpoints. Think of it like this — in data engineering you write a Python function to process data. FastAPI makes that function available over HTTP so a browser can call it.

```
# Data engineering mindset (a function that does work)
def get_all_tickets(status=None, search=None):
    return db.query("SELECT * FROM tickets WHERE ...")

# FastAPI mindset (same function, now a URL the browser can call)
@app.get("/api/tickets")
def get_all_tickets(status=None, search=None):
    return db.query("SELECT * FROM tickets WHERE ...")
```

**Why FastAPI over Flask/Django?**
- Auto-generates interactive API docs at `/docs` (you can test every endpoint without writing any frontend first)
- Built on Python type hints you already know
- Much simpler than Django, more modern than Flask

---

### Database: SQLite

**What is SQLite?**

SQLite is a database that lives in a single `.db` file. You know SQL — this is just SQL with no server to manage. You can open it in DB Browser for SQLite to inspect data visually.

**Why not PostgreSQL?**
- PostgreSQL requires a running server process, user accounts, and connection strings
- SQLite is a file — zero setup, works everywhere, perfect for this project size
- When deployed on Railway, SQLite works fine for demo-scale traffic

---

### Frontend: HTML + Tailwind CSS + Vanilla JS

**What is Tailwind CSS?**

Tailwind is a CSS library where instead of writing `.button { color: white; background: blue; padding: 8px }` in a separate file, you put the style directly on the element as short class names:

```html
<!-- Without Tailwind (you write CSS in a separate file) -->
<button class="my-button">Click</button>

<!-- With Tailwind (style is in the class names directly) -->
<button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
  Click
</button>
```

You never write a CSS file. You just add class names. Tailwind provides the CDN — one `<script>` tag and it works.

**What is Vanilla JS?**

Plain JavaScript — no React, no Vue, no framework. You write `fetch('/api/tickets')` to call your backend, get the data back as JSON, and use `document.getElementById` to update the page. That's it.

**Why not React?**
- React has a steep learning curve (components, hooks, JSX, build tools)
- For 3–4 pages, plain JS is actually faster to write and fully adequate
- Datastraw explicitly lists "HTML + Tailwind" as a valid stack for Python

---

### Motion Animations: Motion.dev (Framer Motion for Vanilla JS)

**What is Motion.dev?**

It is the vanilla JavaScript version of Framer Motion (the most popular React animation library). One CDN script tag, and you can animate any HTML element with smooth, GPU-accelerated motion.

We will pull specific animation patterns from two sources:
- **[motion-primitives.com](https://motion-primitives.com)** — pre-built animation components (text effects, in-view reveals, border trails)
- **[magicui.design](https://magicui.design)** — animated backgrounds, shimmer effects, typing animations

We will **port these patterns to vanilla JS** since we are not using React.

---

### AI Integration: Anthropic Claude API (claude-haiku-4-5)

**Why Haiku?**
- Fastest and cheapest Claude model
- More than capable of summarizing a support ticket description
- A single API call costs less than $0.001

**What it returns:**

```json
{
  "summary": "Customer cannot log into their account after a password reset. The issue appears to be a session token not being cleared properly.",
  "priority": "High",
  "priority_reason": "Login failures block the customer entirely from using the product."
}
```

---

### Deployment: Railway.app

**What is Railway?**

Railway is like "Heroku but modern". You connect your GitHub repo, it detects Python, installs requirements.txt, and runs your app. It gives you a public URL like `https://datastraw-crm.up.railway.app`.

You do not need to understand servers, containers, nginx, or Linux. Railway handles all of it.

---

## 3. System Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                        USER'S BROWSER                               ║
║                                                                      ║
║  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   ║
║  │  LANDING     │    │  DASHBOARD   │    │   TICKET DETAIL      │   ║
║  │  PAGE        │    │  /tickets    │    │   /tickets/TKT-001   │   ║
║  │              │    │              │    │                      │   ║
║  │ • AI video   │    │ • Ticket list│    │ • Full ticket info   │   ║
║  │   guide      │    │ • Search bar │    │ • AI summary         │   ║
║  │ • "Open CRM" │    │ • Status tabs│    │ • Priority badge     │   ║
║  │   button     │    │ • Create btn │    │ • Update status form │   ║
║  │              │    │              │    │ • Notes/comments     │   ║
║  └──────┬───────┘    └──────┬───────┘    └──────────┬───────────┘   ║
╚═════════╪═══════════════════╪════════════════════════╪══════════════╝
          │                   │                        │
          │         JavaScript fetch() calls           │
          │         (HTTP requests to the API)         │
          ▼                   ▼                        ▼
╔══════════════════════════════════════════════════════════════════════╗
║                      FASTAPI BACKEND                                ║
║                       (main.py)                                     ║
║                                                                      ║
║  POST /api/tickets         ← Create new ticket                      ║
║  GET  /api/tickets         ← List tickets (+ search & filter)       ║
║  GET  /api/tickets/{id}    ← Get one ticket's full details          ║
║  PUT  /api/tickets/{id}    ← Update status + add note              ║
║                                                                      ║
║  GET  /                    ← Serve index.html (landing page)       ║
║  GET  /tickets             ← Serve dashboard.html                  ║
║  GET  /tickets/{id}        ← Serve ticket.html                     ║
╚═══════════════╤══════════════════════════╤═══════════════════════════╝
                │                          │
                │ SQL (sqlite3)            │ HTTP (anthropic SDK)
                ▼                          ▼
╔══════════════════════════╗    ╔═══════════════════════════════════╗
║      SQLite DATABASE     ║    ║      CLAUDE API (Haiku)           ║
║      (crm.db)            ║    ║                                   ║
║                          ║    ║  Input: ticket subject +          ║
║  tickets table           ║    ║         description               ║
║  notes table             ║    ║                                   ║
║                          ║    ║  Output: { summary, priority,     ║
║                          ║    ║           priority_reason }       ║
╚══════════════════════════╝    ╚═══════════════════════════════════╝
                │
                ▼
╔══════════════════════════════════════════════════════════════════════╗
║                      RAILWAY.APP                                    ║
║           (hosts everything — DB + API + Frontend)                  ║
║           Public URL: https://your-app.up.railway.app              ║
╚══════════════════════════════════════════════════════════════════════╝
```

### How a "Create Ticket" Request Flows End-to-End

```
User fills form → clicks Submit
        │
        ▼
[Browser JS] fetch('POST /api/tickets', { customer_name, email, subject, description })
        │
        ▼
[FastAPI] receives request → validates fields
        │
        ├──► [Claude API] send subject + description
        │              └──► returns { summary, priority, priority_reason }
        │
        ▼
[SQLite] INSERT INTO tickets (ticket_id, customer_name, ..., ai_summary, ai_priority)
        │
        ▼
[FastAPI] returns { ticket_id: "TKT-004", created_at: "..." }
        │
        ▼
[Browser JS] redirects user to /tickets/TKT-004
        │
        ▼
User sees their ticket with AI summary and priority badge
```

---

## 4. Database Design

### Why SQLite (Not PostgreSQL)

SQLite is a file-based database. When FastAPI starts, it creates `crm.db` if it doesn't exist. There's no password, no port, no server process. You query it with standard SQL — exactly what you know from data engineering.

### Table 1: `tickets`

```sql
CREATE TABLE tickets (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id     TEXT UNIQUE NOT NULL,        -- "TKT-001", "TKT-002", etc.
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    subject       TEXT NOT NULL,
    description   TEXT NOT NULL,
    status        TEXT DEFAULT 'Open',          -- 'Open' | 'In Progress' | 'Closed'
    ai_summary    TEXT,                         -- Claude's 2-sentence summary
    ai_priority   TEXT,                         -- 'Low' | 'Medium' | 'High' | 'Urgent'
    ai_priority_reason TEXT,                    -- Why Claude chose this priority
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Column-by-column explanation:**

| Column | Type | Why |
|--------|------|-----|
| `id` | INTEGER PK | Internal auto-number (1, 2, 3...) for SQL joins |
| `ticket_id` | TEXT UNIQUE | Human-readable ID shown in the UI (TKT-001) |
| `customer_name/email` | TEXT | Who raised the ticket |
| `subject` | TEXT | One-line title of the issue |
| `description` | TEXT | Full problem description |
| `status` | TEXT | Workflow state — only 3 valid values |
| `ai_summary` | TEXT | Claude's plain-English summary (stored, not re-generated) |
| `ai_priority` | TEXT | Claude's priority suggestion |
| `ai_priority_reason` | TEXT | One-line justification from Claude |
| `created_at` | TIMESTAMP | When ticket was created |
| `updated_at` | TIMESTAMP | When ticket was last changed |

### Table 2: `notes`

```sql
CREATE TABLE notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id  TEXT NOT NULL REFERENCES tickets(ticket_id),
    note_text  TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Why a separate table?**

One ticket can have many notes (one analyst adds an update, another adds a follow-up). If you stored notes in the tickets table as a text field, you'd have to concatenate strings — messy and hard to query. Separate table = clean one-to-many relationship.

```
tickets              notes
────────             ──────────────────────
TKT-001   ◄──────── ticket_id = TKT-001, "Customer called back"
TKT-001   ◄──────── ticket_id = TKT-001, "Escalated to senior team"
TKT-002   ◄──────── ticket_id = TKT-002, "Issue resolved"
```

---

## 5. API Design

### Endpoint 1: Create a Ticket

```
POST /api/tickets

Request body (JSON):
{
  "customer_name": "Rahul Sharma",
  "customer_email": "rahul@example.com",
  "subject": "Cannot login after password reset",
  "description": "I reset my password yesterday but still can't log in..."
}

What happens inside:
  1. Validate all fields are present
  2. Generate ticket_id: count existing tickets + 1 → format as "TKT-001"
  3. Call Claude API → get ai_summary, ai_priority, ai_priority_reason
  4. INSERT into tickets table
  5. Return the new ticket_id

Response (JSON):
{
  "ticket_id": "TKT-004",
  "created_at": "2026-09-22T19:00:00"
}
```

### Endpoint 2: List All Tickets

```
GET /api/tickets
GET /api/tickets?status=Open
GET /api/tickets?search=rahul
GET /api/tickets?status=In+Progress&search=login

What happens inside:
  1. Build SQL query dynamically based on query params
  2. If search → WHERE customer_name LIKE '%term%' OR customer_email LIKE '%term%' ...
  3. If status → AND status = 'Open'
  4. Return array of ticket summaries

Response (JSON):
[
  {
    "ticket_id": "TKT-004",
    "customer_name": "Rahul Sharma",
    "subject": "Cannot login after password reset",
    "status": "Open",
    "ai_priority": "High",
    "created_at": "2026-09-22T19:00:00"
  },
  ...
]
```

### Endpoint 3: Get Single Ticket

```
GET /api/tickets/TKT-004

What happens inside:
  1. SELECT * FROM tickets WHERE ticket_id = 'TKT-004'
  2. SELECT * FROM notes WHERE ticket_id = 'TKT-004' ORDER BY created_at
  3. Combine and return

Response (JSON):
{
  "ticket_id": "TKT-004",
  "customer_name": "Rahul Sharma",
  "customer_email": "rahul@example.com",
  "subject": "Cannot login after password reset",
  "description": "I reset my password yesterday but...",
  "status": "Open",
  "ai_summary": "Customer is unable to log in after a password reset...",
  "ai_priority": "High",
  "ai_priority_reason": "Login failure completely blocks product access.",
  "created_at": "2026-09-22T19:00:00",
  "updated_at": "2026-09-22T19:00:00",
  "notes": [
    { "note_text": "Customer called back", "created_at": "..." }
  ]
}
```

### Endpoint 4: Update a Ticket

```
PUT /api/tickets/TKT-004

Request body (JSON):
{
  "status": "In Progress",         ← optional
  "note": "Escalated to dev team"  ← optional
}

What happens inside:
  1. If status provided → UPDATE tickets SET status=?, updated_at=NOW()
  2. If note provided → INSERT INTO notes (ticket_id, note_text)
  3. Return success

Response (JSON):
{
  "success": true,
  "updated_at": "2026-09-22T20:00:00"
}
```

---

## 6. Frontend Pages & UI Design

We have **3 HTML pages** + **FastAPI serves them**.

### Page 1: Landing Page (`/`) — The "Wow" First Impression

**Purpose:** The first thing anyone sees. Sets the tone. Has a video guide and a CTA button.

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  HEADER: "Datastraw CRM" logo    [Open CRM →] button       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   ✦ Animated headline (Text Morph / Word Rotate)           │
│     "Resolve Faster." → "Support Smarter." → "Ship More." │
│                                                            │
│   Subtitle with shimmer text effect                        │
│   "AI-powered support ticketing for modern teams"          │
│                                                            │
├─────────────────────┬──────────────────────────────────────┤
│                     │                                      │
│  VIDEO GUIDE BOX    │   FEATURE HIGHLIGHTS                │
│  (AI avatar or      │                                      │
│   screen recording  │   ✦ Create tickets in seconds       │
│   placeholder)      │   ✦ AI auto-summary + priority      │
│                     │   ✦ Search & filter instantly       │
│  [▶ Watch Guide]    │   ✦ Team notes & collaboration      │
│                     │                                      │
├─────────────────────┴──────────────────────────────────────┤
│   [Open CRM Dashboard →]    [Create First Ticket →]        │
└────────────────────────────────────────────────────────────┘
```

**Motion effects on this page:**
- **Background:** Particles or Flickering Grid (MagicUI) — subtle, dark-themed
- **Headline:** Word Rotate (cycles through phrases) from Motion Primitives
- **Subtitle:** Text Shimmer Wave
- **Feature list:** In-View animation (items slide in as page loads)
- **CTA buttons:** Shimmer Button effect (border beam)
- **Video box:** Border Trail animation on the video container border

---

### Page 2: Dashboard (`/tickets`) — The Main Workspace

**Purpose:** Where the support team spends 90% of their time.

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  HEADER: "Datastraw CRM"    [+ New Ticket]  button         │
├────────────────────────────────────────────────────────────┤
│  SEARCH BAR: [🔍 Search tickets...]                        │
│  STATUS TABS: [All] [Open] [In Progress] [Closed]          │
│  STATS ROW:   12 Open  |  4 In Progress  |  38 Closed      │
├────────────────────────────────────────────────────────────┤
│  TICKETS TABLE:                                            │
│  ┌─────────┬──────────────┬────────────────┬─────┬───────┐ │
│  │ ID      │ Customer     │ Subject        │ Pri │Status │ │
│  ├─────────┼──────────────┼────────────────┼─────┼───────┤ │
│  │ TKT-004 │ Rahul Sharma │ Cannot login.. │ 🔴H │ Open  │ │
│  │ TKT-003 │ Priya Nair   │ Billing error  │ 🟡M │ InPrg │ │
│  │ TKT-002 │ Amit Patel   │ Feature req..  │ 🟢L │Closed │ │
│  └─────────┴──────────────┴────────────────┴─────┴───────┘ │
└────────────────────────────────────────────────────────────┘
```

**Motion effects:**
- **Stats row:** Number Ticker (numbers count up on load)
- **Table rows:** Blur Fade (rows fade in sequentially on load)
- **Status badge:** Color-coded pill (Urgent=red, High=orange, Medium=yellow, Low=green)
- **Search input:** Instant filter with smooth CSS transition (no page reload)
- **[+ New Ticket] button:** Shimmer / Pulsating button effect

---

### Page 3: Ticket Detail (`/tickets/TKT-001`) — The Deep-Dive View

**Purpose:** See everything about one ticket, update it, add notes.

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  ← Back to Dashboard             TKT-004  [🔴 HIGH]       │
├───────────────────────────┬────────────────────────────────┤
│  TICKET DETAILS           │  AI INSIGHTS CARD              │
│  ─────────────────────    │  ──────────────────────────    │
│  Customer: Rahul Sharma   │  🤖 AI Summary                │
│  Email: rahul@...         │  "Customer cannot log in       │
│  Subject: Cannot login..  │   after password reset. The    │
│  Status: [Open ▼]         │   issue appears to be a        │
│                           │   session token problem."      │
│  Description:             │                                │
│  "I reset my password     │  📊 Suggested Priority: HIGH   │
│   yesterday but still     │  "Login failures completely    │
│   can't log in..."        │   block product access."       │
│                           │                                │
│  Created: Sep 22, 7PM     │  [Update Status] [Add Note]    │
├───────────────────────────┴────────────────────────────────┤
│  NOTES / ACTIVITY TIMELINE                                 │
│  ─────────────────────────────────────────────────────    │
│  🕐 Sep 22, 8PM — "Customer called back, still stuck"     │
│  🕐 Sep 22, 9PM — "Escalated to senior engineer"          │
│                                                            │
│  [Add a note...                              ] [Post Note] │
└────────────────────────────────────────────────────────────┘
```

**Motion effects:**
- **AI Insights card:** Morphing Dialog / Border Beam glow on the card
- **Priority badge:** Glow Effect in the badge color
- **Notes timeline:** Animated List (each note slides in)
- **Status update:** Smooth transition when status changes
- **"AI Summary" text:** Text Shimmer on first load

---

## 7. Motion Primitives & Animation Plan

### Sources

| Source | What We Use | How |
|--------|------------|-----|
| [motion-primitives.com](https://motion-primitives.com) | Word Rotate, Text Shimmer, In-View, Border Trail, Animated Number | Port CSS + JS logic to vanilla JS |
| [magicui.design](https://magicui.design) | Flickering Grid BG, Border Beam, Number Ticker, Blur Fade, Shimmer Button | CSS animations + Motion.dev |
| [motion.dev](https://motion.dev) | Core animation engine | CDN script tag |

### CDN Setup (No Build Tools Needed)

```html
<!-- Motion.dev (vanilla JS animation engine) -->
<script type="module">
  import { animate, inView } from "https://cdn.jsdelivr.net/npm/motion@latest/+esm"
  window.Motion = { animate, inView }
</script>

<!-- Tailwind CSS (utility styling) -->
<script src="https://cdn.tailwindcss.com"></script>
```

### Animation Assignments Per Page

**Landing Page**
```
Element              Animation              Library
─────────────────────────────────────────────────────
Page background      Flickering Grid        MagicUI CSS
Hero headline        Word Rotate            Motion Primitives
Subtitle             Text Shimmer Wave      Motion Primitives
Feature list items   In-View (stagger)      Motion.dev
Video box border     Border Trail           Motion Primitives
CTA buttons          Border Beam            MagicUI CSS
```

**Dashboard**
```
Element              Animation              Library
─────────────────────────────────────────────────────
Stats numbers        Number Ticker          MagicUI
Table rows           Blur Fade (staggered)  Motion.dev
New Ticket button    Shimmer Button         MagicUI CSS
Search bar           Smooth transition      CSS only
```

**Ticket Detail**
```
Element              Animation              Library
─────────────────────────────────────────────────────
AI card              Border Beam glow       MagicUI CSS
Priority badge       Glow Effect            CSS box-shadow
Notes list           Animated List          Motion.dev
AI summary text      Text Shimmer           Motion Primitives CSS
```

---

## 8. AI Feature — Summary + Priority

### How It Works (Step by Step)

```
User submits ticket
      │
      ▼
FastAPI receives: { subject: "...", description: "..." }
      │
      ▼
Claude API call (claude-haiku-4-5-20251001):

  System prompt:
  "You are a customer support triage assistant.
   Analyze the support ticket and return a JSON object with:
   - summary: 2-sentence plain English summary of the issue
   - priority: one of 'Low', 'Medium', 'High', 'Urgent'
   - priority_reason: one sentence explaining the priority choice"

  User message:
  "Subject: Cannot login after password reset
   Description: I reset my password yesterday but still can't log in..."

      │
      ▼
Claude returns (forced JSON via response_format):
{
  "summary": "Customer is unable to log in after performing a password reset. The issue may be caused by an uncleared session token or a propagation delay in the auth system.",
  "priority": "High",
  "priority_reason": "Login failures completely block the customer from accessing the product."
}
      │
      ▼
FastAPI stores all 3 fields in the tickets table
      │
      ▼
Returned to browser with the ticket → displayed as AI Insights card
```

### Priority Logic Claude Uses

| Priority | When Claude assigns it | UI Color |
|----------|----------------------|----------|
| **Urgent** | System down, data loss, security breach, production blocked | 🔴 Red |
| **High** | User completely blocked, login failure, payment issue | 🟠 Orange |
| **Medium** | Feature broken but workaround exists, billing question | 🟡 Yellow |
| **Low** | Feature request, cosmetic issue, general question | 🟢 Green |

### Claude API Call (Python)

```python
import anthropic
import json

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def get_ai_insights(subject: str, description: str) -> dict:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system="""You are a customer support triage assistant.
Analyze the support ticket and return ONLY a JSON object with these exact keys:
- summary: 2-sentence plain English summary of the customer's issue
- priority: exactly one of 'Low', 'Medium', 'High', 'Urgent'
- priority_reason: one sentence explaining why you chose this priority""",
        messages=[{
            "role": "user",
            "content": f"Subject: {subject}\n\nDescription: {description}"
        }]
    )
    return json.loads(message.content[0].text)
```

---

## 9. Folder Structure

```
Datastraw_CRM_System/
│
├── main.py              ← FastAPI app: all routes + serves HTML files
├── database.py          ← SQLite: create tables, get connection
├── models.py            ← Pydantic: request/response data shapes
├── ai_service.py        ← Claude API: get_ai_insights() function
│
├── static/
│   ├── index.html       ← Landing page (/)
│   ├── dashboard.html   ← Ticket list (/tickets)
│   ├── ticket.html      ← Single ticket (/tickets/{id})
│   └── css/
│       └── animations.css  ← Custom animation keyframes
│
├── requirements.txt     ← fastapi, uvicorn, anthropic, aiosqlite
├── .env                 ← ANTHROPIC_API_KEY=... (never committed)
├── .env.example         ← ANTHROPIC_API_KEY=your_key_here
├── .gitignore           ← .env, __pycache__/, *.db, .venv/
├── Procfile             ← web: uvicorn main:app --host 0.0.0.0 --port $PORT
├── README.md            ← Setup + run instructions for evaluators
└── PLAN.md              ← This document
```

**File responsibilities (plain English):**

| File | Responsibility |
|------|---------------|
| `main.py` | The "router" — maps URLs to Python functions |
| `database.py` | The "DB manager" — creates tables, runs SQL queries |
| `models.py` | The "contract" — defines what shape data must be in |
| `ai_service.py` | The "AI caller" — one function that calls Claude |
| `static/*.html` | The "screens" — what the user sees |

---

## 10. Build Order (Component by Component)

We build in this order so every piece is testable before moving to the next:

```
Step 1: Project Setup (15 min)
  └── Create virtual env, install packages, create folder structure

Step 2: database.py (20 min)
  └── Create SQLite connection + CREATE TABLE statements
  └── Test: run python database.py → crm.db file appears, tables exist

Step 3: models.py (20 min)
  └── Pydantic models for request/response shapes
  └── Test: import them in Python shell, no errors

Step 4: ai_service.py (30 min)
  └── get_ai_insights() function
  └── Test: call with a sample ticket, see JSON back from Claude

Step 5: main.py — POST /api/tickets (30 min)
  └── First endpoint: create a ticket
  └── Test: http://localhost:8000/docs → try the POST endpoint

Step 6: main.py — GET /api/tickets (20 min)
  └── Second endpoint: list tickets with search + filter
  └── Test: verify search and status filter work

Step 7: main.py — GET + PUT ticket endpoints (20 min)
  └── Single ticket view + update
  └── Test: view a ticket, update its status

Step 8: Landing Page HTML (45 min)
  └── index.html with animations
  └── Test: open in browser — animations play, video box shows

Step 9: Dashboard HTML (45 min)
  └── dashboard.html with table, search, filter
  └── Test: search works, filter works, rows animate in

Step 10: Ticket Detail HTML (45 min)
  └── ticket.html with AI card, notes, update form
  └── Test: all data shows, can add note, change status

Step 11: Polish & Edge Cases (1 hour)
  └── Error handling (what if Claude API fails?)
  └── Empty states (no tickets yet → show empty illustration)
  └── Mobile responsiveness check

Step 12: Deploy to Railway (30 min)
  └── Push to GitHub → connect Railway → set ANTHROPIC_API_KEY env var

Step 13: Record Demo Video (45 min)
  └── 3–5 min: show landing page → create ticket → search → detail view

Step 14: Submit (15 min)
  └── Send email with all 3 links + LinkedIn
```

---

## 11. Deployment Plan

### Railway.app Setup

1. Push code to a new GitHub repository
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your repo → Railway auto-detects Python
4. Set environment variable: `ANTHROPIC_API_KEY = sk-ant-...`
5. Railway reads `Procfile` and runs: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. In ~2 minutes you get a URL like `https://datastraw-crm-production.up.railway.app`

### What Goes in Each Required File

**requirements.txt**
```
fastapi
uvicorn[standard]
anthropic
python-multipart
```

**Procfile**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**.env.example**
```
ANTHROPIC_API_KEY=your_claude_api_key_here
```

**.gitignore**
```
.env
__pycache__/
*.db
.venv/
*.pyc
```

---

## Decision Log (Why We Made Each Choice)

| Decision | Alternative | Why We Chose This |
|----------|------------|------------------|
| FastAPI over Flask | Flask is simpler | FastAPI auto-docs at /docs is invaluable for testing without frontend. Also faster |
| SQLite over PostgreSQL | PostgreSQL is more production-ready | Zero setup, perfect for this scale, works on Railway |
| Vanilla JS over React | React is industry standard | React has a steep learning curve. Plain JS is adequate for 3 pages and faster to write |
| Motion.dev CDN over npm | npm build pipeline | No build tools = no Node.js = simpler deployment |
| Claude Haiku over Sonnet | Sonnet is smarter | Haiku is 10x cheaper, fast enough, and ticket triage doesn't need frontier-level reasoning |
| HTML served by FastAPI | Separate frontend server | Simpler deployment (one Railway service, not two) |

---

*Document complete. Ready to begin Step 1: Project Setup.*
