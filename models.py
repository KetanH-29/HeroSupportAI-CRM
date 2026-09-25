"""
models.py
---------
Defines Pydantic models (data schemas) for request validation
and response formatting.

In data engineering terms:
These are like PySpark StructTypes or Delta table schemas.
They enforce strict types and ensure bad data never reaches your database.
"""

import html
import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

# Strict validation: Only allow common TLDs to prevent .come, .gadget, etc.
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(com|org|net|edu|gov|co|io|dev|ai|me)$")
FORBIDDEN_CHARS = re.compile(r"[<>\"'&]")


# ==========================================
# 1. REQUEST SCHEMAS (Data coming into the API)
# ==========================================

class TicketCreate(BaseModel):
    """
    Schema for creating a new ticket (POST /api/tickets).
    These 4 fields are mandatory from the frontend form.
    """
    customer_name: str = Field(..., min_length=2, max_length=100, description="Customer full name")
    customer_email: str = Field(..., min_length=5, max_length=120, description="Valid customer email")
    subject: str = Field(..., min_length=5, max_length=200, description="Ticket summary/subject")
    description: str = Field(..., min_length=10, max_length=4000, description="Detailed description of the issue")

    @field_validator("customer_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Customer name must be at least 2 characters long.")
        if FORBIDDEN_CHARS.search(v):
            raise ValueError("Customer name cannot contain special characters like <, >, \", ', or &.")
        return html.escape(v)

    @field_validator("customer_email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if FORBIDDEN_CHARS.search(v):
            raise ValueError("Email cannot contain special characters.")
        if not EMAIL_REGEX.match(v):
            raise ValueError("Please provide a valid email address with a valid domain (e.g., user@example.com).")
        return html.escape(v)

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Subject must be at least 5 characters long.")
        if FORBIDDEN_CHARS.search(v):
            raise ValueError("Subject cannot contain special characters like <, >, \", ', or &.")
        return html.escape(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Description must be at least 10 characters long to provide sufficient detail.")
        return html.escape(v)


class LoginRequest(BaseModel):
    """
    Schema for Agent Authentication (POST /api/auth/login).
    """
    email: str = Field(..., min_length=5, max_length=120)
    password: str = Field(..., min_length=4, max_length=100)


class TicketUpdateRequest(BaseModel):
    """
    Schema for updating ticket status or priority, or adding internal notes.
    """
    status: Optional[str] = None
    priority: Optional[str] = None
    note: Optional[str] = None

    @field_validator("note")
    @classmethod
    def sanitize_note(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return html.escape(v.strip())
        return v




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
