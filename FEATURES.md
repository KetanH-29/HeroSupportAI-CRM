# SupportAI — Feature Specification

> **Product Vision:** A customer support CRM that doesn't just manage tickets — it helps teams understand what's happening across them.

---

## Feature Hierarchy

### Tier 1: Core CRM (Assessment Required ✅)
These are table stakes — required by Datastraw assessment.

| Feature | What It Does | Implementation |
|---------|-------------|----------------|
| Create Ticket | Form → auto-generate TKT-ID → save to DB | `POST /api/tickets` |
| List Tickets | Table view with search + status filter | `GET /api/tickets` |
| View Ticket | Full ticket details + notes timeline | `GET /api/tickets/{id}` |
| Update Ticket | Change status + add notes | `PUT /api/tickets/{id}` |
| AI Summary (per-ticket) | 2-sentence summary of individual ticket | Groq API call on create |

---

### Tier 2: Support Intelligence (Differentiator 🌟)
This is what makes your submission stand out.

#### Feature 5: AI Issue Detective

**What it does:**
Analyzes ALL tickets in the database to detect emerging patterns, spikes, and related incidents.

**Dashboard Card Example:**
```
┌──────────────────────────────────────────────────────┐
│  🔴 EMERGING ISSUE DETECTED                          │
├──────────────────────────────────────────────────────┤
│  Payment failures increased 340% in last 24h         │
│                                                      │
│  📊 Stats:                                           │
│  • 27 related tickets                                │
│  • 19 affected customers                             │
│  • 3.4× normal volume                                │
│                                                      │
│  🔍 Common Pattern:                                  │
│  "Payment successful → Order not created"            │
│  Mostly Android users                                │
│  Peak time: 14:00 - 18:00                           │
│                                                      │
│  [ View Related Tickets ]  [ Mark as Investigating ] │
└──────────────────────────────────────────────────────┘
```

**API Endpoint:**
```
GET /api/intelligence/issues
```

**How it works:**
1. Query ALL tickets from database
2. Group by keywords/categories (payment, login, refund, etc.)
3. Send to Groq: "Analyze these ticket summaries. Detect patterns, spikes, or emerging issues."
4. Groq returns JSON with detected issues, affected ticket IDs, severity

---

#### Feature 6: "What Changed?" Time Comparison

**What it does:**
Compares ticket volume and categories across two time periods (yesterday vs today, last week vs this week).

**Dashboard Card Example:**
```
┌──────────────────────────────────────────────────────┐
│  📈 WHAT CHANGED? (Last 24h vs Previous 24h)        │
├──────────────────────────────────────────────────────┤
│  Category         Yesterday  Today   Change          │
│  ───────────────────────────────────────────────────  │
│  Payment issues       4        31    🔴 +675%        │
│  Login issues         7         6    ─ -14%          │
│  Refund requests      5         4    ─ -20%          │
│                                                      │
│  💡 AI Analysis:                                     │
│  Payment-related tickets spiked at 14:20.            │
│  24 of 27 mention "order not created after payment." │
│  Potential incident in payment→order workflow.       │
└──────────────────────────────────────────────────────┘
```

**API Endpoint:**
```
GET /api/intelligence/changes?period=24h
```

---

#### Feature 7: Similar Incidents Search

**What it does:**
When viewing a ticket, show historically similar tickets with resolution patterns.

**API Endpoint:**
```
GET /api/tickets/{ticket_id}/similar
```

---

## Implementation Priority (3-Day Timeline)

### Day 1 (Backend Foundation)
- ✅ database.py
- ✅ models.py  
- ⏳ ai_service.py (both single-ticket + multi-ticket analysis)
- ⏳ main.py (Core CRUD + Intelligence endpoints)

### Day 2 (Frontend + Core Features)
- ⏳ Landing page
- ⏳ Dashboard with ticket table + Intelligence cards
- ⏳ Ticket detail page

### Day 3 (Polish + Deploy)
- ⏳ AI Issue Detective card on dashboard
- ⏳ "What Changed?" widget
- ⏳ Deploy to Railway
- ⏳ Demo video

---

## Why This Approach Wins

| Aspect | Basic CRM | SupportAI |
|--------|-----------|-----------|
| **Complexity** | Single-ticket | Multi-ticket pattern detection |
| **Data Engineering** | CRUD | Time-series analysis, anomaly detection |
| **AI** | Summarization | Pattern recognition, reasoning |
| **Demo Impact** | "Here's a summary" | "AI detected payment system issue" |
| **Role Alignment** | Generic | AI + Data Engineer (exact title!) |
