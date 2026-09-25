# Development Log - HeroSupportAI CRM

## Timeline of Work

### Day 1: Initial Setup & Assessment

**Task:** Understand the assessment requirements and build the foundation.

**Completed:**
- Reviewed Datastraw AI + Tech Intern Assessment Test PDF
- Set up FastAPI backend with SQLite database
- Created HTML pages with Tailwind CSS
- Implemented basic ticket submission flow
- Set up Groq LLaMA AI integration

**Commit:** `fcecf9f` - Complete HeroSupportAI CRM - AI ticket triage + analytics dashboard

---

### Day 2: Assessment Compliance

**Task:** Ensure all assessment requirements are met.

**Completed:**
- Added search functionality
- Added filter by status (Open, In Progress, Closed)
- Implemented ticket detail page with notes
- Set up railway deployment config (Procfile)
- Added .env.example for deployment guidance

**Commit:** `cd66bf1` - Pin Python version to 3.12 for Railway deployment
**Commit:** `deb3915` - Add missing openai dependency for AI service
**Commit:** `961e51b` - Simplify UI text - remove technical jargon

---

### Day 3: Security Hardening & Authentication

**Issue #1: XSS Vulnerability in Frontend**
- **Problem:** Frontend validation used over-restrictive regex `/[<>\"'&script]/i` which blocked legitimate English text containing apostrophes, quotes, or letters `s, c, r, i, p, t`
- **Solution:** Removed XSS_PATTERN regex from frontend; backend `models.py` handles all security validation
- **Result:** Customer can submit tickets with valid English text; malicious input still blocked at backend

**Issue #2: Invalid Email TLDs Accepted**
- **Problem:** Emails like `test@site.come` or `test@site.comusjsjsjsnsjsjsjsksjssjsjsisjsj` were accepted
- **Solution:** Added `EMAIL_REGEX` in `models.py` to restrict TLDs to: com, org, net, edu, gov, co, io, dev, ai, me
- **Result:** Invalid TLDs now rejected with clear error message

**Issue #3: Browser Back-Button Authentication Bypass**
- **Problem:** After logout, pressing browser Back button showed dashboard without login
- **Solution:** 
  - Added synchronous guard script in `<head>` of dashboard.html and ticket.html
  - Implemented `sessionStorage` flags (`dashboard_accessed`, `ticket_accessed`)
  - Added `pageshow` event listener for BFCache protection
  - Logout clears both localStorage and sessionStorage
- **Result:** Back-button navigation redirects to `/login` immediately

**Issue #4: Agent Authentication Missing**
- **Problem:** Dashboard was publicly accessible without login
- **Solution:**
  - Added `/login` page with demo credentials
  - Created `/api/auth/login`, `/api/auth/verify`, `/api/auth/logout` endpoints
  - Added `verify_agent_token` dependency for protected routes
  - Frontend stores token in `localStorage` and sends `Authorization: Bearer <token>` header
- **Result:** Only authenticated agents can access dashboard and ticket management

**Issue #5: Customer Ticket Lookup Not Working**
- **Problem:** Customer portal ticket tracking returned "Ticket not found" error
- **Root Cause:** `GET /api/tickets/{ticket_id}` was protected with `verify_agent_token`, but customers don't have tokens
- **Solution:** Made ticket lookup endpoint public with conditional data return:
  - Customers get basic ticket info only
  - Agents (with valid token) get full details including internal notes
- **Result:** Customers can track their tickets; agents retain note privacy

**Issue #6: "Lookup" Button Text**
- **Problem:** Technical term "Lookup" used on customer-facing page
- **Solution:** Changed button text from "Lookup" to "Search" for better UX

---

### Day 4: Final Polish & Documentation

**Issue #7: AI Priority Not Normalized**
- **Problem:** Dashboard priority distribution chart showed:
  - URGENT: 1
  - HIGH: 2
  - MEDIUM: 0 (incorrect)
  - LOW: 13
- **Root Cause:** Groq LLaMA returned mixed-case priorities: "High", "Low", "URGENT"
  - Database stored them as-is
  - Analytics query used `UPPER()` but "High" → "HIGH", "Low" → "LOW"
  - No tickets had "MEDIUM" in the database
- **Solution:**
  - Added `.upper()` to priority normalization in `ai_service.py`
  - Ran SQL update: `UPDATE tickets SET ai_priority = UPPER(ai_priority)`
- **Result:** All priorities now consistently uppercase (URGENT, HIGH, MEDIUM, LOW)

**Issue #8: README.md Empty**
- **Problem:** Required deliverable was missing
- **Solution:** Created comprehensive README.md with:
  - Feature overview
  - Tech stack
  - Database schema
  - API endpoints
  - Setup instructions
  - Security features
  - Deployment guide

---

## Key Decisions

### Why SQLite over PostgreSQL?
- Simpler for MVP (2-table schema)
- No database server required
- Railway supports SQLite easily
- Assessment explicitly said "keep it simple"

### Why Groq LLaMA over OpenAI?
- Free tier available
- Very fast inference
- Good reasoning capabilities
- Compatible with OpenAI SDK (drop-in replacement)

### Why Bearer Token over Cookies?
- Simpler for single-page app
- No CORS issues with Railway
- Easier to debug
- Assessment said "basic auth is fine"

### Why No Frontend Validation?
- Backend validation is the source of truth
- Frontend validation can be bypassed
- One source of truth at API boundary
- Better developer experience

---

## Lessons Learned

1. **Always test email validation** - TLD regex is easy to get wrong
2. **BFCache is tricky** - Browser back button doesn't reload page; use `pageshow` event
3. **AI outputs are inconsistent** - Always normalize returned data (uppercase priorities)
4. **Read assessment requirements carefully** - Made sure we hit every checkbox
5. **Security first** - XSS, email validation, and auth should be in place before adding features

---

## Final Stats

- **Total Commits:** 5
- **Python Files:** 5 (main.py, models.py, database.py, ai_service.py, analytics.py)
- **HTML Files:** 4 (index.html, login.html, dashboard.html, ticket.html)
- **API Endpoints:** 12
- **Database Tables:** 2
- **Security Features:** XSS validation, email TLD validation, BFCache guards, token auth

---

## Deployment Status

- ✅ Code pushed to GitHub
- ✅ Deployed on Railway.app
- ✅ README.md created
- 📝 Demo video pending

---

**End of Development Log**
