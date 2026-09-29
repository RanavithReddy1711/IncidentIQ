
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

st.title("🚨 IncidentIQ")
st.caption(
    "AI Incident Response Agent powered by Groq and Hindsight memory"
)

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
    st.header("Memory System")
    st.success("Hindsight connected")
    st.info(f"Memory bank: {BANK_ID}")
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

st.header("1. Report a production incident")

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
        with st.spinner("Recalling relevant incidents from Hindsight..."):
            memory_context = get_memory_context(incident_text)

        st.session_state["memory_context"] = memory_context
        st.session_state["incident_text"] = incident_text

        with st.spinner("Groq is analyzing the incident..."):
            diagnosis = analyze_incident(
                incident_text,
                memory_context
            )

        st.session_state["diagnosis"] = diagnosis

    except Exception as e:
        st.error(f"Incident analysis failed: {e}")


# Display results
if "diagnosis" in st.session_state:
    diagnosis = st.session_state["diagnosis"]

    st.divider()
    st.header("2. Incident diagnosis")

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
    st.header("3. Hindsight memory")

    st.write("Memories retrieved for this incident:")
    st.info(st.session_state.get("memory_context", ""))

    st.write("How the AI used memory:")
    st.write(diagnosis.get("memory_used", ""))

    st.divider()
    st.header("4. Save the confirmed resolution")

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