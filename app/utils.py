from __future__ import annotations

from config import Settings


def sanitize_email_text(text: str, settings: Settings) -> str:
    """Normalize smart quotes/dashes and enforce max length."""
    replacements = {"\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
                    "\u2013": "-", "\u2014": "-"}
    normalized = "".join(replacements.get(ch, ch) for ch in text).strip()
    return normalized[: settings.max_email_chars]


def get_test_cases() -> list[dict]:
    return [
        {
            "title": "Urgent Request",
            "input": "Please resolve the server outage immediately. Our clients are affected.",
            "expected": {"intent": "Request", "urgency": "High", "tone": "Urgent"},
        },
        {
            "title": "Informational Email",
            "input": "The meeting has been rescheduled to Monday at 10 AM.",
            "expected": {"intent": "Informational", "urgency": "Low", "tone": "Professional"},
        },
        {
            "title": "Ambiguous Message",
            "input": "We should talk about this soon.",
            "expected": {"intent": "Ambiguous", "urgency": "Medium", "tone": "Neutral"},
        },
    ]