# Datastraw AI + Tech Intern Assessment — Project Plan

> **Prepared for:** Ketan Hadkar  
> **Date Started:** September 22, 2026  
> **Deadline:** September 25–26, 2026 (3–4 days from start)  
> **Submitted to:** ozair.shaikh@datastraw.in | aryan.jaiswal@datastraw.in | CC: talent@datastraw.in

---

## 1. What Is This Assessment?

Datastraw wants to see **one thing**: Can you take a requirement, build a working solution, deploy it to the internet, and explain what you built?

You need to build a **Customer Support Ticketing CRM System** — a web app where a support team can:
- Create support tickets when customers have issues
- See a list of all tickets
- Search/filter tickets
- View ticket details
- Update ticket status and add notes

Think of it like a simplified version of tools like Zendesk or Freshdesk.

---

## 2. Assessment Breakdown (Plain English)

```
┌─────────────────────────────────────────────────────────────┐
│                  WHAT YOU MUST DELIVER                      │
├─────────────────┬───────────────────────────────────────────┤
│  1. Live URL    │  App deployed and working on the internet │
│  2. GitHub Repo │  Clean code + README + .env.example       │
│  3. Demo Video  │  3–5 min showing the app + code walkthru  │
│  4. Email       │  2–3 sentence explanation of approach     │
└─────────────────┴───────────────────────────────────────────┘
```

---

## 3. System Architecture (What We're Building)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                           │
│              (HTML + Tailwind CSS + Vanilla JS)                 │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Home Page   │  │ Create Ticket│  │  Ticket Detail Page  │  │
│  │ (List View)  │  │    Form      │  │  (View + Update)     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼────────────────────┼──────────────┘
          │   HTTP Requests (Fetch API / AJAX)    │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND API                                 │
│                  Python + FastAPI                               │
│                                                                 │
│  POST /api/tickets      → Create new ticket                     │
│  GET  /api/tickets      → List all (with search & filter)       │
│  GET  /api/tickets/{id} → Get single ticket details             │
│  PUT  /api/tickets/{id} → Update status / add notes             │
└───────────────────────────┬─────────────────────────────────────┘
                            │ SQL Queries
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE                                   │
│                       SQLite                                    │
│                                                                 │
│  tickets table          notes table (optional but good)         │
│  ─────────────          ────────────────────────────            │
│  id (PK)                id (PK)                                 │
│  ticket_id (unique)     ticket_id (FK → tickets)                │
│  customer_name          note_text                               │
│  customer_email         created_at                              │
│  subject                                                        │
│  description                                                    │
│  status                                                         │
│  created_at                                                     │
│  updated_at                                                     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT                                  │
│                    Railway.app (free)                           │
│             Everything runs together on one server              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Tech Stack Decision (Why This Stack for You)

Based on your background (Python, SQL, data engineering — no full-stack experience), here is the stack we'll use:

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend/API** | Python + FastAPI | You already know Python. FastAPI is beginner-friendly, auto-generates API docs |
| **Database** | SQLite | Zero setup, single file, works everywhere. Perfect for this project size |
| **Frontend** | HTML + Tailwind CSS + Vanilla JS | No framework to learn. Tailwind makes it look professional with minimal effort |
| **Deployment** | Railway.app | Simplest free deployment for Python apps. Works in one click |

> **You don't need to learn React, Node, or any JS framework.** Plain HTML + JS is perfectly acceptable and is what Datastraw suggests.

---

## 5. Project Folder Structure

```
Datastraw_CRM_System/
│
├── main.py                  ← FastAPI app entry point (all API routes)
├── database.py              ← SQLite connection + table creation
├── models.py                ← Pydantic models (request/response shapes)
│
├── static/                  ← Frontend files served by FastAPI
│   ├── index.html           ← Home page (list of all tickets)
│   ├── create.html          ← Create new ticket form
│   ├── ticket.html          ← Single ticket detail + update
│   └── style.css            ← Any custom CSS (Tailwind via CDN)
│
├── requirements.txt         ← fastapi, uvicorn, aiosqlite
├── .env.example             ← Template for environment variables
├── .gitignore               ← Ignore .env, __pycache__, *.db
├── README.md                ← Setup instructions for evaluators
├── Procfile                 ← Railway deployment config
└── PLAN.md                  ← This file (your working notes)
```

---

## 6. Core Features (What We MUST Build)

### Feature 1 — Create Ticket ✅
- Form with: Customer Name, Email, Issue Title, Description
- On submit: auto-generate `TKT-001` style ID + timestamp
- Store in database, redirect to ticket detail

### Feature 2 — List All Tickets ✅
- Table/card view showing: Ticket ID, Name, Subject, Status, Date
- Clean, mobile-friendly layout

### Feature 3 — Search Functionality ✅
- Live search bar (types → filters instantly)
- Search across: name, email, ticket ID, description

### Feature 4 — Filter by Status ✅
- Dropdown/tabs: All | Open | In Progress | Closed
- Can combine with search

### Feature 5 — View & Update Ticket ✅
- Click a ticket → see full details
- Change status (Open → In Progress → Closed)
- Add a note/comment to the ticket

---

## 7. API Endpoints (What Backend Must Expose)

```
POST   /api/tickets                    → Create a new ticket
GET    /api/tickets?status=X&search=Y  → List all tickets (with filters)
GET    /api/tickets/{ticket_id}        → Get one ticket's full details
PUT    /api/tickets/{ticket_id}        → Update status + add note
```

---

## 8. Bonus / Stand-Out Feature (We Will Add One)

**Plan: Add an AI-powered ticket priority classifier using Claude API**

When a ticket is created:
- The description is sent to Claude (Haiku model — cheap + fast)
- Claude returns a priority: `Low`, `Medium`, `High`, `Urgent`
- This priority is stored and shown on the ticket list

**Why this is smart:**
- It directly matches what Datastraw does (AI + Tech intern)
- It shows you understand AI integration (your actual background)
- It's one thoughtful extra — not five shallow ones
- Claude Haiku costs almost nothing (fractions of a cent per call)

---

## 9. Build Timeline (3-Day Plan)

### Day 1 — Backend + Database (Today, Sep 22)
- [ ] Set up Python project and install dependencies
- [ ] Create `database.py` — SQLite tables
- [ ] Create `models.py` — Pydantic schemas
- [ ] Create `main.py` — all 4 API endpoints
- [ ] Test with FastAPI's auto-generated docs (http://localhost:8000/docs)

### Day 2 — Frontend (Sep 23)
- [ ] Build `index.html` — ticket list with search + filter
- [ ] Build `create.html` — ticket creation form
- [ ] Build `ticket.html` — detail + update page
- [ ] Wire frontend JS to backend API with `fetch()`

### Day 3 — Polish + Deploy + Video (Sep 24)
- [ ] Add AI priority classifier (bonus)
- [ ] Fix any UI issues, test all flows
- [ ] Deploy to Railway.app
- [ ] Record 3–5 min demo video
- [ ] Write README.md
- [ ] Send submission email

---

## 10. Evaluation Criteria (How They'll Score You)

| Criteria | What "Strong" Means |
|----------|-------------------|
| Deployed & Working | All features stable, no crashes |
| Code & API | Clean code, error handling, proper HTTP responses |
| Features & DB | All 5 features + clean 2-table schema |
| Frontend | Professional-looking UI, mobile-friendly |
| Initiative | AI priority classifier — explained with reasoning |

---

## 11. Things to NOT Overthink

- ❌ Don't add authentication (waste of time for this)
- ❌ Don't use PostgreSQL or a complicated DB (SQLite is perfect)
- ❌ Don't use React (HTML + JS is fine)
- ❌ Don't build 10 bonus features (one good one is better)
- ✅ DO make sure it actually works and is deployed
- ✅ DO make sure you can explain every piece of code
- ✅ DO have a clean README with setup instructions

---

## 12. Key Links (Fill As You Go)

| Resource | Link |
|---------|------|
| Live App URL | _TBD after deployment_ |
| GitHub Repository | _TBD_ |
| Demo Video | _TBD_ |
| Railway Dashboard | https://railway.app |
| FastAPI Docs | https://fastapi.tiangolo.com |
| Tailwind CDN | https://cdn.tailwindcss.com |
| Claude API Docs | https://docs.anthropic.com |

---

## 13. Submission Checklist

- [ ] Live deployed URL works (create/search/filter/update all functional)
- [ ] GitHub repo has: source code, README.md, .env.example, .gitignore
- [ ] Demo video: 3–5 min, shows all features + brief code explanation
- [ ] Email sent to ozair.shaikh@datastraw.in & aryan.jaiswal@datastraw.in
- [ ] CC: talent@datastraw.in
- [ ] LinkedIn profile link included in email
- [ ] 2–3 sentence technical approach explanation in email body
