from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

INTENT_CATEGORIES = [
    "Request", "Complaint", "Informational",
    "Follow-up", "Appreciation", "Inquiry",
    "Reminder", "Escalation", "Ambiguous",
]
URGENCY_CATEGORIES = ["High", "Medium", "Low"]
TONE_CATEGORIES    = ["Professional", "Friendly", "Urgent", "Neutral", "Angry", "Polite"]


@dataclass(frozen=True)
class Settings:
    groq_api_key:        str = os.getenv("GROQ_API_KEY", "")
    groq_model:          str = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    request_timeout:     int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    max_email_chars:     int = int(os.getenv("MAX_EMAIL_CHARS", "8000"))
    langfuse_public_key: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    langfuse_secret_key: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    langfuse_base_url:   str = os.getenv("LANGFUSE_BASE_URL", "https://us.cloud.langfuse.com")