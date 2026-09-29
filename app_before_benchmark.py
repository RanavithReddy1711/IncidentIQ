
import os
import json
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

# Load API keys from .env
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_API_URL = os.getenv(
    "HINDSIGHT_API_URL",
    "https://api.hindsight.vectorize.io"
)

# Your Hindsight bank ID from the dashboard URL:
# /banks/incident
BANK_ID = "incidentiq"

st.set_page_config(
    page_title="IncidentIQ",
    page_icon="🚨",
    layout="wide"
)

# IncidentIQ Command Center styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { --bg:#080d18; --panel:#101a2b; --line:#26364d; --cyan:#51e5ff; --purple:#a78bfa; --muted:#91a4bd; }
html, body, [class*="css"] { font-family:'Space Grotesk',sans-serif; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #142b48 0%, #080d18 48%, #080d18 100%); color:#edf6ff; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0e192a,#080d18); border-right:1px solid var(--line); }
.block-container { padding-top:2rem; max-width:1450px; }
h1,h2,h3 { letter-spacing:-.04em; }
h1 { font-size:2.55rem !important; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,#13243a,#0d1524); border:1px solid #2a4562; padding:18px 20px; border-radius:16px; box-shadow:0 0 24px #51e5ff0b; }
div[data-testid="stMetricLabel"] { color:#9bb2cc; }
div[data-testid="stMetricValue"] { color:var(--cyan); font-family:'DM Mono',monospace; }
div[data-testid="stAlert"] { border-radius:14px; }
.stButton>button { border:1px solid #4bdcf6; border-radius:12px; background:linear-gradient(100deg,#123e59,#30265b); color:#f3fbff; font-weight:700; transition:all .2s ease; box-shadow:0 0 18px #51e5ff14; }
.stButton>button:hover { border-color:#b7f6ff; transform:translateY(-2px); box-shadow:0 0 25px #51e5ff30; color:white; }
div[data-baseweb="select"]>div, .stTextArea textarea { background:#0d1727; border:1px solid #2b405a; border-radius:12px; color:#edf6ff; }
hr { border-color:#26364d; }
.iiq-hero { border:1px solid #294762; border-radius:22px; padding:24px 28px; margin:8px 0 26px; background:linear-gradient(110deg,#10263bdf,#17132fdf); position:relative; overflow:hidden; }
.iiq-hero:after { content:""; position:absolute; width:220px;height:220px;right:-80px;top:-110px;border-radius:50%;background:#51e5ff18;filter:blur(2px); }
.iiq-kicker { color:#51e5ff; font:500 11px 'DM Mono',monospace; letter-spacing:.18em; text-transform:uppercase; }
.iiq-sub { color:#a7bad0; margin-top:7px; font-size:15px; }
.iiq-chip { display:inline-block; border:1px solid #31536b; border-radius:999px; padding:5px 11px; color:#9feeff; font:12px 'DM Mono',monospace; margin:8px 7px 0 0; background:#0d2234; }
.iiq-stage { border:1px solid #2b405a; background:#0d1727; border-radius:14px; padding:14px 16px; margin:6px 0; }
.iiq-stage-title { color:#dcecff; font-weight:700; }
.iiq-stage-detail { color:#91a4bd; font-size:13px; margin-top:4px; }
div[data-testid="stProgress"] > div > div { background:linear-gradient(90deg,#51e5ff,#a78bfa); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="iiq-hero">
  <div class="iiq-kicker">● INCIDENTIQ / AI OPERATIONS CENTER</div>
  <h1 style="margin:8px 0 0;color:#f2f8ff;">IncidentIQ <span style="color:#51e5ff;">Command Center</span></h1>
  <div class="iiq-sub">An AI incident response agent with persistent operational memory.</div>
  <span class="iiq-chip">GROQ REASONING</span>
  <span class="iiq-chip">HINDSIGHT MEMORY</span>
  <span class="iiq-chip">HUMAN-VERIFIED REMEDIATION</span>
</div>
""", unsafe_allow_html=True)

# Check API keys
if not GROQ_API_KEY or not HINDSIGHT_API_KEY:
    st.error(
        "API keys are missing. Check your .env file "
        "and make sure both keys are saved."
    )
    st.stop()

# Initialize clients
try:
    groq_client = Groq(api_key=GROQ_API_KEY)

    hindsight = Hindsight(
        base_url=HINDSIGHT_API_URL,
        api_key=HINDSIGHT_API_KEY
    )

except Exception as e:
    st.error(f"Could not initialize clients: {e}")
    st.stop()


def get_memory_context(incident_text):
    """Retrieve relevant past incidents from Hindsight."""
    result = hindsight.recall(
        bank_id=BANK_ID,
        query=(
            "Find previous production incidents, their root causes, "
            "diagnostic steps, and successful resolutions related to: "
            + incident_text
        )
    )

    memories = [
        memory.text
        for memory in result.results
    ]

    return "\n".join(memories) if memories else "No relevant memories found."


def analyze_incident(incident_text, memory_context):
    """Ask Groq to analyze the incident using recalled memories."""

    prompt = f"""
You are IncidentIQ, an AI incident response assistant
for DevOps and Site Reliability Engineering teams.

Analyze the production incident below.

INCIDENT:
{incident_text}

RELEVANT PAST INCIDENT MEMORIES FROM HINDSIGHT:
{memory_context}

Use past incidents as evidence when relevant.
Do not invent facts about the current system.
Clearly label uncertain conclusions.

Return a JSON object with these keys:
- summary
- severity
- likely_root_cause
- confidence
- immediate_actions (list of strings)
- investigation_steps (list of strings)
- memory_used
- prevention (list of strings)

The memory_used field should explain which past experience
was relevant, or say no relevant memory was found.

Return only valid JSON.
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are an expert SRE incident response agent."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    return json.loads(content)


def save_postmortem(incident_text, diagnosis, resolution):
    """Store the incident and resolution in persistent memory."""

    memory = f"""
Production incident:
{incident_text}

AI diagnosis:
{json.dumps(diagnosis, indent=2)}

Confirmed resolution and engineer notes:
{resolution}

Use this experience to help diagnose similar incidents
in the future. Treat the resolution as confirmed only
to the extent stated in the engineer notes.
"""

    hindsight.retain(
        bank_id=BANK_ID,
        content=memory,
        context="IncidentIQ production incident postmortem"
    )


# Sidebar
with st.sidebar:
    st.markdown("### 🧠 MEMORY CORE")
    st.success("● Hindsight connected")
    st.info(f"ACTIVE BANK  /  {BANK_ID}")
    st.write(
        "IncidentIQ recalls previous incidents before "
        "generating its diagnosis."
    )

    st.divider()
    st.caption("Demo: Submit an incident, analyze it, and save the resolution.")

# Demo incident data
demo_incidents = {
    "Checkout database connection leak": (
        "Production checkout API is returning HTTP 500 errors. "
        "Database connection pool is exhausted. "
        "Errors started after the latest deployment. "
        "Checkout latency is above 8 seconds."
    ),
    "Database timeout": (
        "The production order service is experiencing database "
        "timeouts. Query latency has increased and API requests "
        "are failing intermittently."
    ),
    "Redis outage": (
        "The application is reporting Redis connection errors. "
        "Session lookups are failing and user requests are timing out."
    )
}

st.markdown('<div class="iiq-kicker">01 / INTAKE</div>', unsafe_allow_html=True)
st.header("Report a production incident")

selected_demo = st.selectbox(
    "Load a demo incident",
    ["Custom incident"] + list(demo_incidents.keys())
)

default_text = ""
if selected_demo != "Custom incident":
    default_text = demo_incidents[selected_demo]

incident_text = st.text_area(
    "Incident description",
    value=default_text,
    height=160,
    placeholder="Describe the production incident, symptoms, logs, and recent changes..."
)

analyze_button = st.button(
    "🔍 Analyze Incident",
    type="primary",
    disabled=not incident_text.strip()
)

if analyze_button:
    try:
        stage = st.empty()
        stage.markdown("""
        <div class="iiq-stage"><div class="iiq-stage-title">◉ Connecting to memory core</div>
        <div class="iiq-stage-detail">Searching previous incident records and verified resolutions…</div></div>
        """, unsafe_allow_html=True)
        with st.spinner("Recalling relevant incidents from Hindsight..."):
            memory_context = get_memory_context(incident_text)
        stage.markdown("""
        <div class="iiq-stage"><div class="iiq-stage-title">◉ Memory context assembled</div>
        <div class="iiq-stage-detail">Relevant operational history retrieved. Preparing AI investigation…</div></div>
        """, unsafe_allow_html=True)

        st.session_state["memory_context"] = memory_context
        st.session_state["incident_text"] = incident_text

        with st.spinner("Groq is analyzing the incident..."):
            diagnosis = analyze_incident(
                incident_text,
                memory_context
            )

        st.session_state["diagnosis"] = diagnosis
        stage.markdown("""
        <div class="iiq-stage"><div class="iiq-stage-title">✓ Investigation complete</div>
        <div class="iiq-stage-detail">Diagnosis generated. Review recommendations before taking action.</div></div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Incident analysis failed: {e}")


# Display results
if "diagnosis" in st.session_state:
    diagnosis = st.session_state["diagnosis"]

    st.divider()
    st.markdown('<div class="iiq-kicker">02 / AI INVESTIGATION</div>', unsafe_allow_html=True)
    st.header("Incident diagnosis")

    st.markdown("""
    <div class="iiq-stage">
      <div class="iiq-stage-title">✦ Diagnostic report generated</div>
      <div class="iiq-stage-detail">AI-generated assessment · Validate against live telemetry and your incident procedures.</div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Severity",
            diagnosis.get("severity", "Not determined")
        )

    with col2:
        st.metric(
            "Confidence",
            diagnosis.get("confidence", "Not determined")
        )

    st.subheader("Summary")
    st.write(diagnosis.get("summary", ""))

    st.subheader("Likely root cause")
    st.write(diagnosis.get("likely_root_cause", ""))

    st.subheader("Immediate actions")
    for action in diagnosis.get("immediate_actions", []):
        st.write(f"- {action}")

    st.subheader("Investigation steps")
    for step in diagnosis.get("investigation_steps", []):
        st.write(f"- {step}")

    st.subheader("Prevention")
    for item in diagnosis.get("prevention", []):
        st.write(f"- {item}")

    st.divider()
    st.markdown('<div class="iiq-kicker">03 / MEMORY TRACE</div>', unsafe_allow_html=True)
    st.header("Hindsight memory")

    st.write("Memories retrieved for this incident:")
    st.info(st.session_state.get("memory_context", ""))

    st.write("How the AI used memory:")
    st.write(diagnosis.get("memory_used", ""))

    st.divider()
    st.markdown('<div class="iiq-kicker">04 / LEARNING LOOP</div>', unsafe_allow_html=True)
    st.header("Save the confirmed resolution")

    resolution = st.text_area(
        "Engineer-confirmed resolution / postmortem notes",
        placeholder=(
            "Enter what actually fixed the incident, "
            "what was verified, and any prevention steps."
        ),
        height=130,
        key="resolution_input"
    )

    if st.button(
        "💾 Save Postmortem to Hindsight",
        type="primary",
        disabled=not resolution.strip()
    ):
        try:
            with st.spinner("Saving incident experience to Hindsight..."):
                save_postmortem(
                    st.session_state["incident_text"],
                    diagnosis,
                    resolution
                )

            st.success(
                "Postmortem submitted to Hindsight. "
                "It can be recalled for future incidents."
            )

        except Exception as e:
            st.error(f"Could not save postmortem: {e}")


st.divider()
st.caption(
    "IncidentIQ is a hackathon prototype. "
    "Verify diagnoses and actions with your incident response team "
    "before making production changes."
)