"""
Streamlit UI for the IT Incident Ticket Classification & Resolution Assistant.

Run from the project root (with venv activated):
    streamlit run app.py

This calls SupervisorAgent.process_ticket(subject, description) directly,
so it uses the exact same pipeline as agents/test_supervisor.py.
"""

import streamlit as st

from agents.supervisor_agent import SupervisorAgent


st.set_page_config(
    page_title="IT Incident Assistant",
    page_icon="🛠️",
    layout="wide",
)


# --------------------------------------------------------------------
# Load the pipeline once and cache it (agents are slow to initialize,
# we don't want to reload them on every button click / rerun).
# --------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_supervisor(use_llm: bool):
    return SupervisorAgent(load_llm=use_llm)


def render_classification(data):
    st.subheader("Classification")

    if not data:
        st.info("No output returned.")
        return

    st.markdown(f"**Category:** {data.get('category', '—')}")
    st.markdown(f"**Subcategory:** {data.get('subcategory', '—')}")

    confidence = data.get("confidence")
    if isinstance(confidence, (int, float)):
        st.caption(f"Confidence: {confidence:.0%}")

    reason = data.get("reason")
    if reason:
        with st.expander("Why"):
            st.write(reason)


def render_priority(data):
    st.subheader("Priority")

    if not data:
        st.info("No output returned.")
        return

    st.markdown(f"**Priority:** {data.get('priority', '—')}")

    confidence = data.get("confidence")
    if isinstance(confidence, (int, float)):
        st.caption(f"Confidence: {confidence:.0%}")

    reason = data.get("reason")
    if reason:
        with st.expander("Why"):
            st.write(reason)


def render_assignment(data):
    st.subheader("Assignment")

    if not data:
        st.info("No output returned.")
        return

    st.markdown(f"**Recommended Category:** {data.get('recommended_category', '—')}")
    st.markdown(f"**Recommended Subcategory:** {data.get('recommended_subcategory', '—')}")

    confidence = data.get("confidence")
    if isinstance(confidence, (int, float)):
        st.caption(f"Confidence: {confidence:.0%}")

    reason = data.get("reason")
    if reason:
        with st.expander("Why"):
            st.write(reason)


def render_similar_tickets(similar_tickets):
    st.subheader("Similar Historical Tickets")

    if not similar_tickets:
        st.info("No similar tickets found.")
        return

    for i, ticket in enumerate(similar_tickets, start=1):
        score = ticket.get("similarity_score") if isinstance(ticket, dict) else None
        label = f"Match {i}" + (f" — similarity {score:.2f}" if isinstance(score, (int, float)) else "")

        with st.expander(label):
            st.markdown(f"**Ticket ID:** {ticket.get('ticket_id', '—')}")
            st.markdown(f"**Subject:** {ticket.get('subject', '—')}")
            st.markdown(f"**Description:** {ticket.get('description', '—')}")
            st.markdown(
                f"**Category / Subcategory:** "
                f"{ticket.get('category', '—')} / {ticket.get('subcategory', '—')}"
            )
            st.markdown(f"**Priority:** {ticket.get('priority', '—')}")
            resolution_text = ticket.get("resolution")
            if resolution_text:
                st.markdown(f"**Historical Resolution:** {resolution_text}")


def render_resolution(resolution):
    st.subheader("Recommended Resolution")

    if not resolution:
        st.info("No resolution generated.")
        return

    if isinstance(resolution, dict):
        mode = resolution.get("mode")
        if mode:
            st.caption(f"Mode: {mode}")
        text = resolution.get("resolution") or resolution.get("response")
        if text:
            st.markdown(text)
        else:
            st.json(resolution)
    else:
        st.markdown(str(resolution))


# --------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------
st.sidebar.title("Settings")
use_llm = st.sidebar.toggle(
    "Use Groq (live generation)",
    value=True,
    help="On: real generation via Groq for novel tickets. "
         "Off: fast RAG-only demo mode, historical matches only.",
)
st.sidebar.caption(
    "Turning this off skips loading the LLM and only surfaces "
    "historical matches (faster, but no live generation)."
)

# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------
st.title("🛠️ IT Incident Ticket Assistant")
st.write(
    "Enter a ticket below to run it through the full multi-agent "
    "pipeline: retrieval, classification, priority, assignment, "
    "and resolution."
)

with st.spinner("Loading agents..."):
    supervisor = load_supervisor(use_llm)

with st.form("ticket_form"):
    subject = st.text_input("Subject", placeholder="e.g. VPN disconnects every 12 minutes")
    description = st.text_area(
        "Description",
        placeholder="Describe the issue in detail...",
        height=150,
    )
    submitted = st.form_submit_button("Analyze Ticket", type="primary")

if submitted:
    if not subject and not description:
        st.error("Please enter a subject and/or description.")
    else:
        with st.spinner("Running pipeline..."):
            try:
                result = supervisor.process_ticket(subject, description)
            except Exception as e:
                st.error(f"Pipeline error: {e}")
                result = None

        if result:
            st.success("Done!")

            col1, col2, col3 = st.columns(3)
            with col1:
                render_classification(result.get("classification"))
            with col2:
                render_priority(result.get("priority"))
            with col3:
                render_assignment(result.get("assignment"))

            st.divider()
            render_resolution(result.get("resolution"))

            st.divider()
            render_similar_tickets(result.get("similar_tickets"))