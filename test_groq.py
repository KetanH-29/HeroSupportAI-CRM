"""
test_groq.py
------------
Quick test script to discover available Groq AI models.

This was used during initial setup to find the correct model name
after "llama-3.3-70b-versatile" returned a 404 error.

Run: python test_groq.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = OpenAI(
    base_url=os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1"),
    api_key=os.getenv("AI_API_KEY", "")
)

print("=" * 60)
print("GROQ API MODEL DISCOVERY")
print("=" * 60)
print()

try:
    # List available models
    print("Fetching available models from Groq API...")
    models = client.models.list()

    print(f"\n✅ Found {len(models.data)} available models:\n")

    for idx, model in enumerate(models.data, 1):
        print(f"{idx}. {model.id}")
        if hasattr(model, 'owned_by'):
            print(f"   Owner: {model.owned_by}")
        if hasattr(model, 'created'):
            print(f"   Created: {model.created}")
        print()

    print("-" * 60)
    print("RECOMMENDED FOR THIS PROJECT:")
    print("Model: openai/gpt-oss-120b")
    print("Reason: Best balance of speed + reasoning for ticket triage")
    print("-" * 60)

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check your GROQ_API_KEY in .env")
    print("2. Verify AI_BASE_URL is correct")
    print("3. Check internet connection")

print()
print("=" * 60)
print("Update your .env file with the chosen model:")
print('AI_MODEL=openai/gpt-oss-120b')
print("=" * 60)
