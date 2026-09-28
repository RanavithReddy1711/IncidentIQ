# 🚨 IncidentIQ — AI Incident Response Assistant

**Investigate incidents. Learn from past experience. Make informed decisions.**

IncidentIQ is an AI-powered incident response assistant designed to help DevOps engineers, developers, and Site Reliability Engineering (SRE) teams investigate application and infrastructure incidents.

When a production service fails or becomes slow, engineers need to understand what happened, find the likely cause, and decide what to do next.

IncidentIQ helps by analyzing incident descriptions, recalling relevant historical incidents, and generating structured investigation and remediation recommendations.

It combines AI reasoning with persistent operational memory to make incident investigation more context-aware.

---

## 📖 Table of Contents

- [What Is IncidentIQ?](#-what-is-incidentiq)
- [Why IncidentIQ?](#-why-incidentiq)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [Using the Dashboard](#-using-the-dashboard)
- [Memory Evaluation](#-memory-evaluation)
- [Limitations and Safety](#-limitations-and-safety)
- [Future Improvements](#-future-improvements)
- [Author](#-author)

## 💡 What Is IncidentIQ?

Imagine an online shopping application suddenly starts returning errors. Customers cannot complete purchases, and the engineering team needs to investigate quickly.

An engineer might need to check application logs, database performance, recent deployments, and previous incidents.

IncidentIQ helps organize this investigation.

An engineer can provide the incident details, and IncidentIQ can:

1. Analyze the reported symptoms using an AI model.
2. Search persistent memory for relevant past incidents.
3. Generate a likely root cause and investigation steps.
4. Suggest immediate actions and preventive measures.
5. Save engineer-provided resolution notes for future reference.

**In simple terms:** IncidentIQ is an AI assistant that helps engineers investigate problems and reuse knowledge from previous incidents.

It supports engineers; it does not replace their judgment.

## 🎯 Why IncidentIQ?

Traditional incident investigation often depends on engineers finding the right documentation, searching old incident reports, and remembering how similar problems were resolved.

IncidentIQ aims to make this process more organized by combining AI-generated analysis with persistent operational memory.

| Challenge | How IncidentIQ helps |
|---|---|
| Engineers need to investigate errors quickly | Generates structured incident analysis |
| Previous incident knowledge is difficult to find | Retrieves relevant memories using Hindsight |
| AI may lack historical context | Supplies retrieved incident history to the model |
| Recommended changes need human oversight | Provides a simulated human-review workflow |
| Incident knowledge can be lost after resolution | Saves engineer-provided postmortem notes |

## ✨ Features

### 1. AI-Powered Incident Diagnosis

Uses the Groq API with the configured language model to generate:

- Incident summary
- Suggested severity
- Likely root cause
- Qualitative confidence estimate
- Immediate actions
- Investigation steps
- Prevention recommendations

The output is structured so engineers can review each part of the diagnosis.

### 2. Persistent Operational Memory

Uses Hindsight to store and recall incident knowledge.

When a new incident is submitted, IncidentIQ searches for relevant historical records, such as similar symptoms, root causes, and documented resolutions.

The retrieved information is provided to the AI as additional context.

This allows the assistant to reference previous experience instead of relying only on the current incident description.

### 3. Supporting Evidence

Engineers can provide additional information such as:

- Sanitized application logs
- Error messages and stack traces
- Alerts and metric readings
- Deployment details
- Relevant investigation notes

The AI can use this information during its analysis.

The evidence is user-provided and is not independently verified by the application.

### 4. Human-Reviewed Remediation Planning

IncidentIQ presents proposed actions for an engineer to review.

The dashboard includes a simulated approval workflow where a reviewer can select an action and record an approval note.

**Important:** Approval is simulated. IncidentIQ does not execute commands or make changes to production infrastructure.

### 5. Postmortem Learning Loop

After an incident has been investigated, an engineer can enter resolution notes and save them to Hindsight.

These notes can be recalled during future investigations.

The quality of the memory depends on the accuracy and completeness of the information entered by engineers.

### 6. Memory vs. No-Memory Comparison

Runs the same incident through the same configured model:

- Once without historical memory
- Once with recalled Hindsight memory

The results can be compared to observe differences in diagnoses and recommendations.

This is a demonstration of memory's influence, not a verified accuracy measurement.

### 7. Interactive Dashboard

Includes a Streamlit dashboard with:

- Dark and light appearance modes
- Sample incident scenarios
- Incident analysis results
- Hindsight memory trace
- Postmortem submission
- Memory comparison results

## 🔄 How It Works

The application follows this workflow:

```text
Engineer reports an incident
           |
           v
Incident description + supporting evidence
           |
           v
Hindsight retrieves relevant past incidents
           |
           v
Groq AI analyzes the current incident
using the supplied memory and evidence
           |
           v
Structured diagnosis and recommendations
           |
           v
Engineer reviews proposed actions
           |
           v
Simulated approval and resolution notes
           |
           v
Engineer-provided notes saved to Hindsight
           |
           v
Memory available for future investigations
```

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and backend |
| Streamlit | Interactive web dashboard |
| Groq API | Language model inference |
| Hindsight | Persistent memory, retention, and recall |
| python-dotenv | Loads API credentials from environment variables |

### Technical Architecture

The application is organized around three primary components:

**1. Presentation layer — Streamlit**

Collects incident descriptions and supporting evidence, displays diagnosis results, and provides memory and simulated approval interfaces.

**2. Reasoning layer — Groq**

Receives the current incident and retrieved memory context, then generates a structured JSON diagnosis.

**3. Memory layer — Hindsight**

Stores incident and resolution notes and retrieves relevant records for subsequent incidents.

The current implementation is a Python application using external AI and memory services. It does not include a production telemetry ingestion pipeline or automated infrastructure integrations.

## 🚀 Getting Started

Follow these steps to run IncidentIQ locally.

### Prerequisites

You will need:

- Python 3.10 or later
- Git
- A Groq API key
- A Hindsight Cloud API key
- A configured Hindsight memory bank

### Step 1 — Clone the repository

Open a terminal and run:

```bash
git clone https://github.com/RanavithReddy1711/IncidentIQ.git
cd IncidentIQ
```

### Step 2 — Create a virtual environment

For Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

For macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install dependencies

Install the required Python packages:

```bash
pip install streamlit groq python-dotenv hindsight-client
```

### Step 4 — Configure API credentials

Create a file named `.env` in the project root, alongside `app.py`.

Add your own credentials:

```env
GROQ_API_KEY=your_groq_api_key
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
```

Replace the example values with your actual API credentials.

The application uses the Hindsight memory bank configured in its source code. Make sure the bank exists and is accessible through your Hindsight account.

**Security:** Never commit your real `.env` file, API keys, passwords, or access tokens to GitHub.

### Step 5 — Run IncidentIQ

Start the Streamlit application:

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal, usually:

`http://localhost:8501`

Open that address in your browser to access the dashboard.

## 🖥️ Using the Dashboard

### 1. Select an incident

Choose a sample incident from the dropdown or enter a custom incident description.

Examples include database connection problems, Redis errors, payment gateway failures, and Kubernetes pod restarts.

### 2. Provide supporting evidence

Optionally paste relevant logs, alerts, metrics, or investigation notes.

Remove secrets and sensitive customer information before submitting evidence.

### 3. Analyze the incident

Click **Analyze Incident**.

IncidentIQ retrieves relevant memory and asks the configured AI model to generate its diagnosis.

### 4. Review the diagnosis and memory

Review the severity, likely root cause, immediate actions, investigation steps, and prevention recommendations.

Inspect the Hindsight memory trace to see which historical records were retrieved.

### 5. Review simulated remediation

Select a proposed action and record a reviewer note.

This is a demonstration workflow only. No production system is modified.

### 6. Save the resolution

After investigating the incident, enter the engineer-confirmed resolution and postmortem notes.

Submit them to Hindsight so they can be recalled during future investigations.

## 🧪 Memory Evaluation

IncidentIQ includes a controlled comparison that uses the same incident and configured model with and without retrieved historical memory.

The purpose is to explore how historical context affects generated output.

For a meaningful accuracy evaluation, a test dataset should contain:

- Representative incident descriptions
- Engineer-verified root causes
- Confirmed resolutions
- Consistent evaluation criteria

Possible evaluation metrics include:

| Metric | What it measures |
|---|---|
| Root-cause match rate | How often the predicted cause matches the verified cause |
| Resolution relevance | Whether recommendations align with the confirmed resolution |
| Evidence grounding | Whether statements are supported by provided evidence |
| Investigation usefulness | Engineer assessment of the proposed investigation steps |

The current memory comparison does not calculate these ground-truth metrics. Model confidence is qualitative and is not a calibrated probability.

## 🔐 Limitations and Safety

IncidentIQ is an AI-assisted investigation tool. Its outputs require human review.

- AI-generated diagnoses and recommendations may be incorrect or incomplete.
- Incident evidence is user-provided and is not independently verified.
- Retrieved memories may contain inaccurate, outdated, or duplicate information.
- A suggested root cause is a hypothesis until verified against actual system evidence.
- Remediation approval is simulated and does not execute production changes.
- The current application does not directly ingest live logs, metrics, traces, or infrastructure telemetry.

Always validate diagnoses and proposed actions with your incident response team before making production changes.

Do not submit API keys, passwords, access tokens, or sensitive customer information.

## 🔭 Future Improvements

Potential development directions include:

- Integration with observability platforms for live logs, metrics, and traces
- Automated ingestion of verified incident postmortems
- A curated and deduplicated operational knowledge base
- A larger ground-truth incident evaluation dataset
- More detailed evidence citations and diagnosis traceability
- Secure integrations with incident management and infrastructure tools
- Real remediation integrations with strict permissions, approval gates, and audit logs

These are future development directions and are not currently implemented.

## 👤 Author

**Ranavith Reddy**

GitHub: [@RanavithReddy1711](https://github.com/RanavithReddy1711)

---

Built to help engineering teams turn incident experience into reusable operational knowledge.
