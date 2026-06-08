from __future__ import annotations

import json
import re
from typing import Literal

from pydantic import BaseModel, ValidationError


class EmailAnalysis(BaseModel):
    intent: Literal[
        "Request", "Complaint", "Informational", "Follow-up",
        "Appreciation", "Inquiry", "Reminder", "Escalation", "Ambiguous",
    ]
    urgency: Literal["High", "Medium", "Low"]
    tone: Literal["Professional", "Friendly", "Urgent", "Neutral", "Angry", "Polite"]


def parse_response(raw_text: str) -> EmailAnalysis:
    """Parse raw LLM text → validated EmailAnalysis. Handles JSON embedded in prose."""
    text = raw_text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```[a-z]*\n?", "", text).rstrip("`").strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in model output.")
        data = json.loads(match.group(0))

    try:
        return EmailAnalysis.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"Output failed schema validation: {exc}") from exc