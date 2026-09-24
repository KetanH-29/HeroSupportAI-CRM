"""
models.py
---------
Defines Pydantic models (data schemas) for request validation
and response formatting.

In data engineering terms:
These are like PySpark StructTypes or Delta table schemas.
They enforce strict types and ensure bad data never reaches your database.
"""

from pydantic import BaseModel
from typing import Optional, List


# ==========================================
# 1. REQUEST SCHEMAS (Data coming into the API)
# ==========================================

class TicketCreate(BaseModel):
    """
    Schema for creating a new ticket (POST /api/tickets).
    These 4 fields are mandatory from the frontend form.
    """
    customer_name: str
    customer_email: str
    subject: str
    description: str




# ==========================================
# 2. RESPONSE SCHEMAS (Data returned by the API)
# ==========================================

class NoteResponse(BaseModel):
    """
    Schema for a single note returned in API responses.
    """
    id: int
    ticket_id: str
    note_text: str
    created_at: str


class TicketSummaryResponse(BaseModel):
    """
    Compact ticket schema for the Dashboard table (GET /api/tickets).
    Contains just enough info to show the row in the table.
    """
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    status: str
    ai_priority: Optional[str] = None
    created_at: str


class TicketDetailResponse(BaseModel):
    """
    Complete ticket schema for the Detail page (GET /api/tickets/{ticket_id}).
    Includes full description, AI insights, and all notes.
    """
    id: int
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    ai_summary: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_priority_reason: Optional[str] = None
    created_at: str
    updated_at: str
    notes: List[NoteResponse] = []
