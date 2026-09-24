"""
main.py
-------
FastAPI application entry point for SupportAI CRM.

This file contains:
1. API routes for CRUD operations on tickets
2. API routes for Support Intelligence (Issue Detective, What Changed)
3. Static file serving (HTML pages)
4. Database initialization on startup
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
from typing import Optional

import database
import ai_service
import analytics
from models import *

# ==========================================================
# FASTAPI APP INITIALIZATION
# ==========================================================

app = FastAPI(
    title="HeroSupportAI CRM",
    description="AI-powered customer support ticketing with intelligence & analytics layer",
    version="1.0.0"
)

# Serve static files (CSS, JS, images) from /static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


# ==========================================================
# STARTUP EVENT: Initialize Database
# ==========================================================

@app.on_event("startup")
def startup_event():
    database.init_db()


# ==========================================================
# HTML PAGE ROUTES (Frontend)
# ==========================================================

@app.get("/", include_in_schema=False)
def landing_page():
    """
    Serves the landing page (index.html) at the root URL.
    include_in_schema=False hides this from the auto-generated /docs
    """
    return FileResponse("static/index.html")


@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    """
    Serves the main dashboard (ticket list) page.
    """
    return FileResponse("static/dashboard.html")


@app.get("/tickets/{ticket_id}", include_in_schema=False)
def ticket_detail_page(ticket_id: str):
    """
    Serves the ticket detail page.
    The actual ticket data is loaded via JavaScript calling /api/tickets/{ticket_id}
    """
    return FileResponse("static/ticket.html")


# ==========================================================
# API ROUTES: TICKET CRUD OPERATIONS
# ==========================================================

@app.post("/api/tickets", response_model=dict)
def create_ticket(ticket: TicketCreate):
    """
    Creates a new support ticket.

    Flow:
    1. Generate unique ticket_id (TKT-001, TKT-002, etc.)
    2. Call AI service to get summary + priority
    3. Insert into database
    4. Return the new ticket_id
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Generate ticket ID
    count = cursor.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    ticket_id = f"TKT-{str(count + 1).zfill(3)}"

    # Get AI analysis
    ai_result = ai_service.analyze_single_ticket(
        subject=ticket.subject,
        description=ticket.description
    )

    # Insert into database
    cursor.execute("""
        INSERT INTO tickets (
            ticket_id, customer_name, customer_email, subject, description,
            ai_summary, ai_priority, ai_priority_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        ticket.customer_name,
        ticket.customer_email,
        ticket.subject,
        ticket.description,
        ai_result["summary"],
        ai_result["priority"],
        ai_result["priority_reason"]
    ))

    conn.commit()
    conn.close()

    return {
        "ticket_id": ticket_id,
        "created_at": datetime.now().isoformat(),
        "ai_summary": ai_result["summary"],
        "ai_priority": ai_result["priority"]
    }


@app.get("/api/tickets", response_model=list[TicketSummaryResponse])
def get_all_tickets(
    status: Optional[str] = Query(None, description="Filter by status: Open, In Progress, Closed"),
    search: Optional[str] = Query(None, description="Search across name, email, subject, description")
):
    """
    Lists all tickets with optional filtering.

    Query parameters:
    - status: Filter by ticket status
    - search: Search term (matches customer_name, email, subject, description)
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    # Apply status filter
    if status:
        query += " AND status = ?"
        params.append(status)

    # Apply search filter
    if search:
        query += """ AND (
            customer_name LIKE ? OR
            customer_email LIKE ? OR
            subject LIKE ? OR
            description LIKE ?
        )"""
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term, search_term])

    query += " ORDER BY created_at DESC"

    results = cursor.execute(query, params).fetchall()
    conn.close()

    return [
        TicketSummaryResponse(
            ticket_id=row["ticket_id"],
            customer_name=row["customer_name"],
            customer_email=row["customer_email"],
            subject=row["subject"],
            status=row["status"],
            ai_priority=row["ai_priority"],
            created_at=row["created_at"]
        )
        for row in results
    ]


@app.get("/api/tickets/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket_detail(ticket_id: str):
    """
    Returns full details of a single ticket including all notes.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Get ticket
    ticket = cursor.execute(
        "SELECT * FROM tickets WHERE ticket_id = ?",
        (ticket_id,)
    ).fetchone()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Get notes
    notes = cursor.execute(
        "SELECT * FROM notes WHERE ticket_id = ? ORDER BY created_at ASC",
        (ticket_id,)
    ).fetchall()

    conn.close()

    return TicketDetailResponse(
        id=ticket["id"],
        ticket_id=ticket["ticket_id"],
        customer_name=ticket["customer_name"],
        customer_email=ticket["customer_email"],
        subject=ticket["subject"],
        description=ticket["description"],
        status=ticket["status"],
        ai_summary=ticket["ai_summary"],
        ai_priority=ticket["ai_priority"],
        ai_priority_reason=ticket["ai_priority_reason"],
        created_at=ticket["created_at"],
        updated_at=ticket["updated_at"],
        notes=[
            NoteResponse(
                id=note["id"],
                ticket_id=note["ticket_id"],
                note_text=note["note_text"],
                created_at=note["created_at"]
            )
            for note in notes
        ]
    )


@app.put("/api/tickets/{ticket_id}", response_model=dict)
def update_ticket(ticket_id: str, update: dict):
    """
    Updates a ticket's status and/or adds a note.

    Body can contain:
    - status: new status value
    - note: note text to add
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Check ticket exists
    ticket = cursor.execute(
        "SELECT * FROM tickets WHERE ticket_id = ?",
        (ticket_id,)
    ).fetchone()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Update status if provided
    if update.get("status"):
        cursor.execute(
            "UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?",
            (update["status"], ticket_id)
        )

    # Update priority if provided (agent override of AI classification)
    if update.get("priority"):
        cursor.execute(
            "UPDATE tickets SET ai_priority = ?, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?",
            (update["priority"], ticket_id)
        )

    # Add note if provided
    if update.get("note"):
        cursor.execute(
            "INSERT INTO notes (ticket_id, note_text) VALUES (?, ?)",
            (ticket_id, update["note"])
        )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "ticket_id": ticket_id,
        "updated_at": datetime.now().isoformat()
    }


# ==========================================================
# API ROUTES: SUPPORT INTELLIGENCE (AI Issue Detective)
# ==========================================================

@app.get("/api/intelligence/issues", response_model=dict)
def detect_issues():
    """
    AI Issue Detective: Analyzes all recent tickets to detect patterns
    and emerging system-wide issues.

    This is the STANDOUT FEATURE that differentiates your CRM.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Get tickets from last 48 hours
    cutoff_time = (datetime.now() - timedelta(hours=48)).isoformat()
    recent_tickets = cursor.execute(
        "SELECT * FROM tickets WHERE created_at >= ? ORDER BY created_at DESC",
        (cutoff_time,)
    ).fetchall()

    conn.close()

    if len(recent_tickets) < 3:
        return {
            "has_emerging_issue": False,
            "message": "Not enough recent data to detect patterns (minimum 3 tickets required)"
        }

    # Convert to list of dicts for AI service
    tickets_list = [dict(ticket) for ticket in recent_tickets]

    # Call AI Issue Detective
    result = ai_service.detect_emerging_issues(tickets_list)

    return result


# ==========================================================
# API ROUTES: ETL ANALYTICS PIPELINE (Power BI/Kibana Layer)
# ==========================================================

@app.get("/api/analytics/all")
def get_all_analytics_data():
    """
    Master Analytics Endpoint: Runs the complete ETL pipeline
    and returns all metrics in a single payload.

    Used by the dashboard to load all charts & KPIs at once.
    """
    return analytics.get_full_analytics()


@app.get("/api/analytics/overview")
def get_overview_kpis():
    """
    Returns top-level KPI metrics (total, open, closed, avg resolution time).
    """
    return analytics.get_overview_stats()


@app.get("/api/analytics/volume")
def get_volume_trend_data(days: int = 7):
    """
    Returns time-series ticket counts per day for the volume line chart.
    """
    return analytics.get_volume_trend(days=days)


@app.get("/api/analytics/status")
def get_status_breakdown_data():
    """
    Returns status distribution for the donut chart.
    """
    return analytics.get_status_breakdown()


@app.get("/api/analytics/priority")
def get_priority_breakdown_data():
    """
    Returns AI priority distribution for the priority bar chart.
    """
    return analytics.get_priority_breakdown()


@app.get("/api/analytics/categories")
def get_category_breakdown_data():
    """
    Returns keyword-based category distribution for the category bar chart.
    """
    return analytics.get_category_breakdown()


@app.get("/api/analytics/changes")
def get_period_changes(hours: int = 24):
    """
    Returns period-over-period comparison metrics for "What Changed?" analysis.
    """
    return analytics.get_period_comparison(hours=hours)


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
def health_check():
    """
    Simple health check endpoint for deployment monitoring.
    """
    return {
        "status": "healthy",
        "service": "HeroSupportAI CRM",
        "timestamp": datetime.now().isoformat()
    }
