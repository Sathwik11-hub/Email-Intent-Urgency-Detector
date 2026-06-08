from __future__ import annotations

import json
import streamlit as st

from config import Settings
from model import run_chain
from utils import get_test_cases, sanitize_email_text


# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Email Intent & Urgency Detector",
    page_icon="📧",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM DARK THEME CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&family=Space+Grotesk:wght@600;700&display=swap');

/* ===== Global ===== */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #000000 !important;
    color: #ffffff !important;
}

.stApp {
    background-color: #000000 !important;
    color: #ffffff !important;
}

/* ===== Text ===== */
h1, h2, h3, h4, h5, h6,
p, span, div, label {
    color: #ffffff !important;
}

/* ===== Hero ===== */
.hero {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #1e293b 100%
    );
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 24px;
}

.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    margin-bottom: 6px;
    color: #ffffff;
}

.hero p {
    color: #cbd5e1;
}

/* ===== Inputs ===== */
textarea,
input {
    background-color: #111827 !important;
    color: #ffffff !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
}

/* Text area container */
[data-testid="stTextArea"] textarea {
    background-color: #111827 !important;
    color: #ffffff !important;
}

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* ===== Buttons ===== */
.stButton button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #1d4ed8 !important;
}

.stDownloadButton button {
    background-color: #16a34a !important;
    color: white !important;
    border-radius: 10px !important;
}

/* ===== Tabs ===== */
.stTabs [role="tablist"] {
    gap: 8px;
}

.stTabs [role="tab"] {
    background-color: #111827 !important;
    color: #ffffff !important;
    border-radius: 10px;
    padding: 10px 16px;
}

.stTabs [aria-selected="true"] {
    background-color: #2563eb !important;
}

/* ===== Expander ===== */
.streamlit-expanderHeader {
    background-color: #111827 !important;
    color: #ffffff !important;
}

/* ===== JSON Output ===== */
[data-testid="stJson"] {
    background-color: #111827 !important;
    border-radius: 10px;
    padding: 12px;
}

/* ===== Alerts ===== */
.stAlert {
    background-color: #111827 !important;
    color: #ffffff !important;
    border-radius: 10px;
}

/* ===== Badge ===== */
.badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.9rem;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# INIT SETTINGS
# ─────────────────────────────────────────────────────────────
settings = Settings()

if "history" not in st.session_state:
    st.session_state.history = []

# ─────────────────────────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📧 Email Intent & Urgency Detector</h1>
    <p>
        Analyze email text to classify 
        <b>Intent</b>, <b>Urgency</b>, and 
        <b>Tone</b> using Generative AI.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ Model Settings")

    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        value=settings.groq_api_key
    )

    groq_model = st.text_input(
        "Groq Model",
        value=settings.groq_model
    )

    st.divider()

    st.subheader("🔭 Langfuse Tracing")

    lf_pub = st.text_input(
        "Public Key",
        type="password",
        value=settings.langfuse_public_key
    )

    lf_sec = st.text_input(
        "Secret Key",
        type="password",
        value=settings.langfuse_secret_key
    )

    lf_url = st.text_input(
        "Host URL",
        value=settings.langfuse_base_url
    )

    if lf_pub and lf_sec:
        st.success("Langfuse tracing enabled ✓")
    else:
        st.info("Add Langfuse keys to enable tracing.")

    settings = Settings(
        groq_api_key=groq_key or settings.groq_api_key,
        groq_model=groq_model or settings.groq_model,
        request_timeout=settings.request_timeout,
        max_email_chars=settings.max_email_chars,
        langfuse_public_key=lf_pub or settings.langfuse_public_key,
        langfuse_secret_key=lf_sec or settings.langfuse_secret_key,
        langfuse_base_url=lf_url or settings.langfuse_base_url,
    )

# ─────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2.2, 1], gap="large")

URGENCY_COLORS = {
    "High": "#ef4444",
    "Medium": "#f59e0b",
    "Low": "#22c55e",
}

with col_left:

    email_text = st.text_area(
        "Paste Email Text",
        height=220,
        placeholder="Enter email content here..."
    )

    analyze_clicked = st.button(
        "Analyze",
        type="primary",
        disabled=not settings.groq_api_key
    )

    if analyze_clicked:

        cleaned = sanitize_email_text(
            email_text,
            settings
        )

        if not cleaned:
            st.error(
                "Please provide email text before analyzing."
            )

        else:
            with st.spinner("Analyzing email..."):

                try:
                    result = run_chain(
                        cleaned,
                        settings
                    )

                    st.success(
                        "Analysis complete."
                    )

                    st.json(
                        result.model_dump()
                    )

                    urgency = result.urgency

                    color = URGENCY_COLORS.get(
                        urgency,
                        "#64748b"
                    )

                    st.markdown(
                        f"""
                        <span class='badge'
                        style='background:{color}20;
                        color:{color};
                        border:1px solid {color};'>
                        Urgency: {urgency}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

                    st.download_button(
                        "⬇ Download JSON",
                        data=json.dumps(
                            result.model_dump(),
                            indent=2
                        ),
                        file_name="email_analysis.json",
                        mime="application/json"
                    )

                    st.session_state.history.insert(
                        0,
                        {
                            "email": cleaned,
                            "result": result.model_dump()
                        }
                    )

                except Exception as exc:
                    st.error(
                        f"Error: {exc}"
                    )

    if not settings.groq_api_key:
        st.warning(
            "Add your Groq API key in the sidebar."
        )

# ─────────────────────────────────────────────────────────────
# RIGHT PANEL
# ─────────────────────────────────────────────────────────────
with col_right:

    tab_ex, tab_hist, tab_tips = st.tabs(
        ["Examples", "History", "Tips"]
    )

    with tab_ex:
        for case in get_test_cases():
            with st.expander(case["title"]):
                st.write(case["input"])
                st.caption("Expected Output")
                st.json(case["expected"])

    with tab_hist:
        if not st.session_state.history:
            st.caption("No analyses yet.")

        for item in st.session_state.history[:5]:
            preview = (
                item["email"][:120]
                + (
                    "..."
                    if len(item["email"]) > 120
                    else ""
                )
            )

            st.write(preview)
            st.json(item["result"])
            st.divider()

    with tab_tips:
        st.write("• Keep emails realistic.")
        st.write("• Unclear urgency → Medium.")
        st.write("• Multiple intents → dominant intent selected.")
        st.write("• Traces visible in Langfuse dashboard.")