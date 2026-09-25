# HeroSupportAI CRM

AI-powered customer support ticketing system with intelligent triage, analytics dashboard, and agent portal.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

---

## Overview

A full-stack web application for managing customer support tickets with:

- **AI Ticket Analysis** - Groq LLaMA automatically analyzes each ticket for priority and summary
- **Issue Detective** - Cross-ticket pattern detection for emerging system issues
- **ETL Analytics** - Dashboard with charts, KPIs, and status breakdowns
- **Agent Portal** - Token-based authentication with session management
- **Customer Portal** - Public ticket submission and tracking

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Database | SQLite |
| Frontend | HTML + Tailwind CSS + Vanilla JS |
| AI | Groq LLaMA (GPT-oss-120b) |
| Deployment | Railway.app |

---

## Features

### Customer Portal (`/`)
- Submit support tickets with customer name, email, subject, and description
- Auto-generated ticket ID (TKT-001, TKT-002, etc.)
- Track existing tickets by entering Ticket ID
- Live status updates and AI-generated summaries

### Agent Portal (`/login`)
- Token-based authentication
- Dashboard with KPIs, volume trends, status breakdowns
- Search across ticket metadata
- Filter by status (Open, In Progress, Closed)
- Update ticket status and priority
- Add internal staff notes
- Logout protection with BFCache guard (prevents back-button bypass)

### AI Features
- **Single-Ticket Analysis** - Priority scoring (URGENT/HIGH/MEDIUM/LOW) with reasoning
- **Issue Detective** - Detects patterns across 50+ recent tickets
- **What Changed?** - Period-over-period comparison (24h vs previous 24h)

---

## Database Schema

### `tickets` table
| Column | Type |
|--------|------|
| id | INTEGER PRIMARY KEY |
| ticket_id | TEXT UNIQUE |
| customer_name | TEXT |
| customer_email | TEXT |
| subject | TEXT |
| description | TEXT |
| status | TEXT (Open/In Progress/Closed) |
| ai_summary | TEXT |
| ai_priority | TEXT |
| ai_priority_reason | TEXT |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

### `notes` table
| Column | Type |
|--------|------|
| id | INTEGER PRIMARY KEY |
| ticket_id | TEXT (FK) |
| note_text | TEXT |
| created_at | TIMESTAMP |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tickets` | POST | Create new ticket |
| `/api/tickets` | GET | List tickets (with search/filter) |
| `/api/tickets/{ticket_id}` | GET | Get ticket details |
| `/api/tickets/{ticket_id}` | PUT | Update ticket status/priority |
| `/api/auth/login` | POST | Agent login |
| `/api/auth/verify` | GET | Verify session |
| `/api/auth/logout` | POST | Logout |
| `/api/intelligence/issues` | GET | Issue Detective |
| `/api/analytics/all` | GET | All analytics data |

---

## Setup & Development

### Prerequisites
- Python 3.12+
- SQLite (built-in)
- Groq API key (free tier available)

### Installation

```bash
# Clone the repository
git clone https://github.com/KetanH-29/HeroSupportAI-CRM.git
cd HeroSupportAI-CRM

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Groq API credentials
cp .env.example .env
# Edit .env with your AI_API_KEY
```

### Environment Variables

```
AI_BASE_URL=https://api.groq.com/openai/v1
AI_API_KEY=your_groq_api_key
AI_MODEL=openai/gpt-oss-120b
```

### Running Locally

```bash
python -m uvicorn main:app --reload --port 8000
```

Visit:
- Customer Portal: http://localhost:8000/
- Agent Login: http://localhost:8000/login
- API Docs: http://localhost:8000/docs

---

## Security Features

### Input Validation
- **XSS Prevention** - Rejects `<>"'&` characters in all text fields
- **Email Validation** - Enforces valid TLDs (com, org, net, edu, gov, co, io, dev, ai, me)
- **Field Length Limits** - Min/max lengths on all inputs

### Authentication
- **Bearer Token Auth** - Session tokens with 7-day expiry
- **BFCache Guard** - Prevents browser back-button bypass after logout
- **Session Invalidation** - Tokens cleared on logout

---

## Deployment (Railway)

1. Create new project from GitHub repo
2. Add environment variables in Railway settings
3. Deploy - Railway auto-detects Python and reads `Procfile`

The `Procfile` contains:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Demo Credentials

Use these to test the agent portal:
- **Email:** `agent@herosupport.ai`
- **Password:** `agent123`

---

## Files

```
.
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic validation schemas
├── database.py          # SQLite connection and initialization
├── ai_service.py        # Groq LLaMA integration for AI analysis
├── analytics.py         # ETL pipeline for dashboard metrics
├── requirements.txt     # Python dependencies
├── Procfile             # Railway deployment config
├── .env.example         # Environment variables template
├── static/
│   ├── index.html       # Customer portal
│   ├── login.html       # Agent login portal
│   ├── dashboard.html   # Agent command center
│   └── ticket.html      # Ticket detail view
└── README.md
```

---

## Author

**Ketan Hadkar**  
GitHub: [@KetanH-29](https://github.com/KetanH-29)
