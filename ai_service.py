"""
ai_service.py
-------------
AI intelligence service for SupportAI CRM.

Provides two tiers of AI capability:
1. Per-Ticket Analysis (Baseline):
   - 2-sentence summary
   - Priority categorization (Low/Medium/High/Urgent) with reasoning

2. Support Intelligence (Differentiator):
   - Issue Detective: detects emerging patterns & spikes across all tickets
   - What Changed: compares ticket volume/categories across time periods
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client pointing to Groq (or OmniRoute/OpenRouter)
client = OpenAI(
    base_url=os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1"),
    api_key=os.getenv("AI_API_KEY", "")
)

MODEL = os.getenv("AI_MODEL", "openai/gpt-oss-120b")


# ==========================================================
# LEVEL 1: SINGLE-TICKET ANALYSIS (Runs when ticket created)
# ==========================================================

def analyze_single_ticket(subject: str, description: str) -> dict:
    """
    Analyzes a single support ticket to generate:
    - 2-sentence plain-English summary
    - Suggested priority with one-line reason

    Fallback: returns graceful defaults if API fails.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.1,  # Low temperature for consistent categorization
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert customer support triage AI.
Analyze the given support ticket and return a JSON object with EXACTLY these keys:
- summary: A clear 2-sentence summary of the core issue.
- priority: Exactly one of "Low", "Medium", "High", "Urgent".
- priority_reason: One sentence explaining why you chose this priority.

Priority guidelines:
- Urgent: System outages, security issues, financial loss, critical blockers.
- High: Core feature broken for a user, unable to login, payment issues.
- Medium: Non-critical bugs with workarounds, billing queries.
- Low: General questions, minor UI glitches, feature suggestions."""
                },
                {
                    "role": "user",
                    "content": f"Subject: {subject}\n\nDescription: {description}"
                }
            ]
        )

        result = json.loads(response.choices[0].message.content)
        return {
            "summary": result.get("summary", "Summary unavailable."),
            "priority": result.get("priority", "Medium"),
            "priority_reason": result.get("priority_reason", "Standard review needed.")
        }

    except Exception as e:
        print(f"⚠️ AI Single-Ticket Analysis failed: {e}")
        # Safe fallback so ticket creation NEVER fails
        return {
            "summary": f"Customer reported: {subject[:100]}...",
            "priority": "Medium",
            "priority_reason": "Default priority assigned (AI service unavailable)."
        }


# ==========================================================
# LEVEL 2: ISSUE DETECTIVE (Cross-ticket pattern detection)
# ==========================================================

def detect_emerging_issues(tickets: list) -> dict:
    """
    Analyzes a list of recent tickets to detect patterns, anomalies,
    and emerging system-wide issues.

    Data Eng + AI intersection: Multi-record reasoning.
    """
    if not tickets or len(tickets) < 3:
        return {
            "has_emerging_issue": False,
            "message": "Not enough recent tickets to detect patterns (minimum 3 required)."
        }

    # Format tickets into a lightweight digest for the LLM
    ticket_digest = []
    for t in tickets[:50]:  # Cap at 50 tickets to keep token usage small
        ticket_digest.append({
            "id": t.get("ticket_id"),
            "subject": t.get("subject"),
            "status": t.get("status"),
            "created_at": t.get("created_at")
        })

    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI Site Reliability & Support Intelligence Analyst.
Analyze recent customer support tickets to detect if there is a systemic pattern or emerging incident.

Return a JSON object with:
- has_emerging_issue: boolean (true if 2+ tickets share a root cause)
- issue_title: string (short title like "Payment Gateway Failures")
- severity: "critical" | "high" | "medium" | "low"
- pattern_description: 2-3 sentences explaining the common pattern
- affected_ticket_count: estimated number of related tickets
- affected_ticket_ids: array of ticket IDs that are part of this issue
- recommended_action: one clear step the team should take
- root_cause_hypothesis: brief technical guess of what broke"""
                },
                {
                    "role": "user",
                    "content": f"Here are the recent support tickets:\n{json.dumps(ticket_digest, indent=2)}"
                }
            ]
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"⚠️ Issue Detective failed: {e}")
        return {
            "has_emerging_issue": False,
            "message": "Pattern detection temporarily unavailable."
        }


# ==========================================================
# TEST BLOCK
# ==========================================================

if __name__ == "__main__":
    print("Testing AI Service with sample ticket...")
    test_result = analyze_single_ticket(
        subject="Payment deducted but order was not placed",
        description="I tried to buy the premium plan for $49. The money was deducted from my HDFC bank account, but my account still shows Free tier and no order confirmation email was received."
    )
    print("\n--- Level 1: Single Ticket Analysis ---")
    print(json.dumps(test_result, indent=2))
