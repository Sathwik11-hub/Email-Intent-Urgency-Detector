from __future__ import annotations

import os
import warnings

from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

from config import Settings
from parser import EmailAnalysis, parse_response
from prompt import build_prompt_template


def _get_langfuse_client(settings: Settings):
    """Return a Langfuse client when keys are configured.

    We use direct Langfuse spans so only a single observation is recorded.
    """
    if not (settings.langfuse_public_key and settings.langfuse_secret_key):
        return None

    # Inject credentials into env so the v4 client picks them up automatically
    os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
    os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
    os.environ["LANGFUSE_HOST"] = settings.langfuse_base_url

    try:
        from langfuse import get_client
    except ImportError:
        warnings.warn(
            "langfuse is not installed. Tracing disabled. "
            "Run: pip install langfuse",
            stacklevel=2,
        )
        return None

    return get_client()


def run_chain(email_text: str, settings: Settings | None = None) -> EmailAnalysis:
    settings = settings or Settings()

    if not settings.groq_api_key:
        raise ValueError("Missing GROQ_API_KEY.")

    llm = ChatGroq(
        model=settings.groq_model,
        temperature=0,
        api_key=SecretStr(settings.groq_api_key),
        timeout=settings.request_timeout,
    )

    chain = build_prompt_template() | llm | StrOutputParser()

    langfuse = _get_langfuse_client(settings)
    if langfuse:
        with langfuse.start_as_current_observation(
            as_type="span",
            name="RunnableSequence",
        ) as span:
            span.update(input={"email_text": email_text})
            raw = chain.invoke({"email_text": email_text})
            span.update(output=raw)
    else:
        raw = chain.invoke({"email_text": email_text})
    return parse_response(raw)