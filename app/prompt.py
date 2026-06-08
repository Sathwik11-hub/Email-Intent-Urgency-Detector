from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from config import INTENT_CATEGORIES, URGENCY_CATEGORIES, TONE_CATEGORIES


def build_prompt_template() -> ChatPromptTemplate:
    system = (
        "You are an email intent, urgency, and tone classifier.\n"
        "Analyze only the provided email text. Do not use outside knowledge.\n"
        "Return ONLY a JSON object with exactly these keys: intent, urgency, tone.\n"
        "No markdown, no code fences, no extra text or keys.\n"
        f"intent  → one of: {', '.join(INTENT_CATEGORIES)}\n"
        f"urgency → one of: {', '.join(URGENCY_CATEGORIES)}\n"
        f"tone    → one of: {', '.join(TONE_CATEGORIES)}\n"
        "If intent is unclear use 'Ambiguous'. If multiple intents exist, pick the dominant one."
    )
    return ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", 'Email text:\n"""{email_text}"""'),
    ])