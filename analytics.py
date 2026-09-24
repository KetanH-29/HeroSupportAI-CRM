"""
analytics.py
------------
ETL Analytics Pipeline for SupportAI CRM.

This module acts as the data transformation layer between
raw SQLite ticket data and the dashboard metrics.

Pipeline flow:
    EXTRACT  → Read raw tickets from SQLite
    TRANSFORM → Aggregate, group, calculate metrics
    LOAD      → Return clean JSON for dashboard charts

Data Engineering analogy:
    This is like a PySpark transformation job that reads from
    a raw data lake table and writes aggregated metrics to a
    data warehouse — except here the "warehouse" is JSON served
    directly to the browser dashboard.
"""

import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import database


# ==========================================================
# CATEGORY KEYWORD RULES
# (Like a dimension/lookup table in dimensional modeling)
# ==========================================================

CATEGORY_KEYWORDS = {
    "Payment":  ["payment", "charge", "billing", "refund", "invoice",
                 "transaction", "deducted", "charged", "subscription"],
    "Login":    ["login", "password", "access", "account", "sign in",
                 "auth", "otp", "credentials", "locked out"],
    "Order":    ["order", "delivery", "shipping", "tracking", "dispatch",
                 "not delivered", "missing order", "shipment"],
    "Bug":      ["bug", "error", "crash", "broken", "not working",
                 "glitch", "issue", "fail", "failed"],
    "Feature":  ["feature", "request", "suggestion", "improve",
                 "add option", "would like", "enhance"],
    "Refund":   ["refund", "money back", "return", "cancel",
                 "cancellation", "chargeback"]
}


def categorize_ticket(subject: str, description: str) -> str:
    """
    Categorizes a ticket based on keyword matching.

    Transform step: Converts unstructured text into a structured
    category dimension — same concept as a lookup/dimension table
    in a data warehouse.
    """
    text = (subject + " " + description).lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "Other"


# ==========================================================
# PIPELINE FUNCTION 1: Overview KPI Stats
# Powers: Stat tiles at top of dashboard
# ==========================================================

def get_overview_stats() -> dict:
    """
    EXTRACT  → All tickets from SQLite
    TRANSFORM → Count by status, calculate avg resolution time
    LOAD      → Return KPI metrics dict

    Dashboard output:
        Total Tickets | Open | In Progress | Closed | Avg Resolve Time
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Total tickets
    total = cursor.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]

    # Count by status
    open_count = cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'Open'"
    ).fetchone()[0]

    in_progress_count = cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'In Progress'"
    ).fetchone()[0]

    closed_count = cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'Closed'"
    ).fetchone()[0]

    # Average resolution time in hours (only for closed tickets)
    # julianday() converts timestamp to decimal days → multiply by 24 for hours
    avg_resolution = cursor.execute("""
        SELECT AVG(
            (julianday(updated_at) - julianday(created_at)) * 24
        )
        FROM tickets
        WHERE status = 'Closed'
    """).fetchone()[0]

    # Tickets created in last 24 hours (for "new today" metric)
    cutoff_24h = (datetime.now() - timedelta(hours=24)).isoformat()
    new_today = cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE created_at >= ?",
        (cutoff_24h,)
    ).fetchone()[0]

    conn.close()

    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress_count,
        "closed": closed_count,
        "avg_resolution_hours": round(avg_resolution, 1) if avg_resolution else 0,
        "new_today": new_today
    }


# ==========================================================
# PIPELINE FUNCTION 2: Ticket Volume Trend
# Powers: Line chart (tickets per day, last 7 days)
# ==========================================================

def get_volume_trend(days: int = 7) -> dict:
    """
    EXTRACT  → Tickets created in the last N days
    TRANSFORM → Group by date, count per day
               Fill missing days with 0 (like forward-filling in pandas)
    LOAD      → Return Chart.js-ready {labels, values} format

    Dashboard output:
        Line chart showing ticket volume across the last 7 days
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Get ticket counts grouped by day
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    raw_results = cursor.execute("""
        SELECT
            DATE(created_at) as day,
            COUNT(*) as ticket_count
        FROM tickets
        WHERE created_at >= ?
        GROUP BY DATE(created_at)
        ORDER BY day ASC
    """, (cutoff,)).fetchall()

    conn.close()

    # Transform: Build a complete date range (fill missing days with 0)
    # This is like a date dimension join in a data warehouse
    date_map = {row["day"]: row["ticket_count"] for row in raw_results}

    labels = []
    values = []

    for i in range(days - 1, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        display_label = (datetime.now() - timedelta(days=i)).strftime("%b %d")
        labels.append(display_label)
        values.append(date_map.get(date, 0))  # 0 if no tickets that day

    return {
        "labels": labels,
        "values": values,
        "period_days": days
    }


# ==========================================================
# PIPELINE FUNCTION 3: Status Breakdown
# Powers: Donut chart (Open vs In Progress vs Closed %)
# ==========================================================

def get_status_breakdown() -> dict:
    """
    EXTRACT  → All tickets
    TRANSFORM → Group by status, calculate percentage
    LOAD      → Return {labels, values, percentages}
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    results = cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM tickets
        GROUP BY status
        ORDER BY count DESC
    """).fetchall()

    conn.close()

    total = sum(row["count"] for row in results)

    labels = []
    values = []
    percentages = []

    for row in results:
        labels.append(row["status"])
        values.append(row["count"])
        pct = round((row["count"] / total * 100), 1) if total > 0 else 0
        percentages.append(pct)

    return {
        "labels": labels,
        "values": values,
        "percentages": percentages,
        "total": total
    }


# ==========================================================
# PIPELINE FUNCTION 4: Priority Breakdown
# Powers: Horizontal bar chart (Urgent/High/Medium/Low counts)
# ==========================================================

def get_priority_breakdown() -> dict:
    """
    EXTRACT  → All tickets with AI priority set
    TRANSFORM → Group by priority level, order by severity
    LOAD      → Return ordered {labels, values}

    Always returns all 4 priority levels (URGENT, HIGH, MEDIUM, LOW)
    even if some have 0 tickets — needed for consistent chart display.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    results = cursor.execute("""
        SELECT
            UPPER(COALESCE(ai_priority, 'Unclassified')) as priority,
            COUNT(*) as count
        FROM tickets
        GROUP BY UPPER(ai_priority)
    """).fetchall()

    conn.close()

    # Define priority order (most severe first — like sorting by SLA breach risk)
    priority_order = ["URGENT", "HIGH", "MEDIUM", "LOW"]

    # Build map from database results (normalize to uppercase)
    priority_map = {}
    for row in results:
        priority_map[row["priority"]] = row["count"]

    labels = []
    values = []
    colors = []

    color_map = {
        "URGENT":  "#ef4444",  # Red
        "HIGH":    "#f97316",  # Orange
        "MEDIUM":  "#eab308",  # Yellow
        "LOW":     "#22c55e",  # Green
    }

    # Always include all 4 priorities, fill missing ones with 0
    for priority in priority_order:
        labels.append(priority.capitalize())
        values.append(priority_map.get(priority, 0))  # 0 if priority not in database
        colors.append(color_map[priority])

    return {
        "labels": labels,
        "values": values,
        "colors": colors
    }


# ==========================================================
# PIPELINE FUNCTION 5: Category Breakdown
# Powers: Bar chart (Payment/Login/Bug/etc. counts)
# ==========================================================

def get_category_breakdown() -> dict:
    """
    EXTRACT  → All tickets (subject + description)
    TRANSFORM → Apply keyword categorization to each ticket
               Count tickets per category
    LOAD      → Return {labels, values}

    Note: This is an in-memory transformation since SQLite
    doesn't have native text classification. In a production
    system this category would be stored as a column after
    being computed by a scheduled ETL job.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    tickets = cursor.execute(
        "SELECT subject, description FROM tickets"
    ).fetchall()

    conn.close()

    # Apply categorization transformation to each ticket
    category_counts = defaultdict(int)

    for ticket in tickets:
        category = categorize_ticket(
            ticket["subject"],
            ticket["description"]
        )
        category_counts[category] += 1

    # Sort by count descending (highest volume category first)
    sorted_categories = sorted(
        category_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "labels": [item[0] for item in sorted_categories],
        "values": [item[1] for item in sorted_categories]
    }


# ==========================================================
# PIPELINE FUNCTION 6: What Changed? (Time Comparison)
# Powers: "What Changed?" intelligence card on dashboard
# ==========================================================

def get_period_comparison(hours: int = 24) -> dict:
    """
    EXTRACT  → Two time windows of ticket data
    TRANSFORM → Compare volume and category distribution
               Calculate percentage change per category
    LOAD      → Return comparison table + change signals

    This is like a period-over-period comparison in Power BI
    or a change detection job in a data pipeline.

    Example output:
        Payment issues: 4 → 31   (+675% 🔴)
        Login issues:   7 → 6    (-14%  ─ )
        Bug reports:    5 → 4    (-20%  ─ )
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    now = datetime.now()
    current_start = (now - timedelta(hours=hours)).isoformat()
    previous_start = (now - timedelta(hours=hours * 2)).isoformat()

    # Current period tickets
    current_tickets = cursor.execute(
        "SELECT subject, description FROM tickets WHERE created_at >= ?",
        (current_start,)
    ).fetchall()

    # Previous period tickets
    previous_tickets = cursor.execute(
        "SELECT subject, description FROM tickets WHERE created_at >= ? AND created_at < ?",
        (previous_start, current_start)
    ).fetchall()

    conn.close()

    # Categorize both periods
    current_counts = defaultdict(int)
    previous_counts = defaultdict(int)

    for ticket in current_tickets:
        cat = categorize_ticket(ticket["subject"], ticket["description"])
        current_counts[cat] += 1

    for ticket in previous_tickets:
        cat = categorize_ticket(ticket["subject"], ticket["description"])
        previous_counts[cat] += 1

    # Build comparison rows
    all_categories = set(list(current_counts.keys()) + list(previous_counts.keys()))
    comparison = []

    for category in all_categories:
        current_val = current_counts.get(category, 0)
        previous_val = previous_counts.get(category, 0)

        # Calculate percentage change
        if previous_val == 0 and current_val > 0:
            change_pct = 100.0
            signal = "new"
        elif previous_val == 0:
            change_pct = 0.0
            signal = "stable"
        else:
            change_pct = round(((current_val - previous_val) / previous_val) * 100, 1)
            if change_pct >= 50:
                signal = "spike"      # 🔴 Major increase
            elif change_pct >= 20:
                signal = "rising"     # 🟠 Moderate increase
            elif change_pct <= -20:
                signal = "dropping"   # 🟢 Decreasing
            else:
                signal = "stable"     # ─  No significant change

        comparison.append({
            "category": category,
            "previous": previous_val,
            "current": current_val,
            "change_pct": change_pct,
            "signal": signal
        })

    # Sort by current volume descending
    comparison.sort(key=lambda x: x["current"], reverse=True)

    return {
        "period_hours": hours,
        "current_period_total": sum(current_counts.values()),
        "previous_period_total": sum(previous_counts.values()),
        "comparison": comparison
    }


# ==========================================================
# MASTER PIPELINE: Run all transforms at once
# Called by /api/analytics/all endpoint
# ==========================================================

def get_full_analytics() -> dict:
    """
    Runs the complete analytics pipeline and returns all
    dashboard metrics in a single response.

    This is like a master ETL job that runs all
    transformation tasks and produces a unified output.
    """
    return {
        "overview": get_overview_stats(),
        "volume_trend": get_volume_trend(days=7),
        "status_breakdown": get_status_breakdown(),
        "priority_breakdown": get_priority_breakdown(),
        "category_breakdown": get_category_breakdown(),
        "period_comparison": get_period_comparison(hours=24)
    }


# ==========================================================
# TEST BLOCK
# ==========================================================

if __name__ == "__main__":
    import json

    print("🔄 Running Analytics ETL Pipeline...")
    print()

    print("📊 Overview Stats:")
    print(json.dumps(get_overview_stats(), indent=2))
    print()

    print("📈 Volume Trend (Last 7 Days):")
    print(json.dumps(get_volume_trend(), indent=2))
    print()

    print("🍩 Status Breakdown:")
    print(json.dumps(get_status_breakdown(), indent=2))
    print()

    print("🎯 Priority Breakdown:")
    print(json.dumps(get_priority_breakdown(), indent=2))
    print()

    print("🏷️  Category Breakdown:")
    print(json.dumps(get_category_breakdown(), indent=2))
    print()

    print("📅 Period Comparison (Last 24h vs Previous 24h):")
    print(json.dumps(get_period_comparison(), indent=2))
