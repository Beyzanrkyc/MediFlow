import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

API_BASE = "http://localhost:8000"


def _nhs_logo():
    st.markdown("""
    <div class="nhs-header">
        <span class="nhs-logo-box">NHS</span>
        <span style="font-size:1.15rem">MediFlow</span>
        <span style="font-weight:400;font-size:0.9rem;opacity:0.85;margin-left:6px">
            Clinical Audit Trail &amp; Analytics
        </span>
    </div>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=15)
def _load_audit_trail(limit=5):
    try:
        resp = requests.get(f"{API_BASE}/analytics/audit-trail", params={"limit": limit}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


@st.cache_data(ttl=15)
def _load_triage_distribution():
    try:
        resp = requests.get(f"{API_BASE}/analytics/triage-distribution", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


@st.cache_data(ttl=15)
def _load_guideline_confidence():
    try:
        resp = requests.get(f"{API_BASE}/analytics/guideline-confidence", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


def _audit_trail():
    st.markdown("## Clinical Audit Trail")

    sessions = _load_audit_trail(limit=3)

    if sessions is None:
        st.warning(f"⚠️ Couldn't reach the backend at `{API_BASE}`.")
        return

    if not sessions:
        st.info("No symptom-checker sessions logged yet — use the Symptom Checker page to generate some.")
        return

    latest = sessions[0]

    st.markdown(f"""
    <div class='audit-section'>
        <h5>Patient Input</h5>
        <p style='margin:0'>{latest['query']}</p>
        <small style='color:#888'>Recorded: {latest['created_at']}</small>
    </div>
    """, unsafe_allow_html=True)

    sources_html = "".join(f"<li>{s}</li>" for s in latest["sources"]) or "<li>No guidelines retrieved</li>"
    st.markdown(f"""
    <div class='audit-section'>
        <h5>Retrieved Guidelines</h5>
        <ul style='margin:0;padding-left:1.2rem'>{sources_html}</ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='audit-section'>
        <h5>AI Reasoning Summary</h5>
        <p style='margin:0'>{latest['answer']}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Recent Sessions (JSON)"):
        st.json(sessions)


def _analytics_charts():
    st.markdown("---")
    st.markdown("## Analytics Overview")

    distribution = _load_triage_distribution()
    confidence_rows = _load_guideline_confidence()

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("**Triage Level Distribution (all logged sessions)**")
        if distribution and distribution["total"] > 0:
            fig1 = go.Figure(go.Pie(
                labels=["URGENT", "LOW", "Unclassified"],
                values=[distribution["urgent"], distribution["low"], distribution["unknown"]],
                marker_colors=["#DA291C", "#007F3B", "#768692"],
                hole=0.45,
                textinfo="label+percent",
            ))
            fig1.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False, paper_bgcolor="white",
            )
            st.plotly_chart(fig1, width="stretch", config={"displayModeBar": False})
        else:
            st.info("No triage sessions logged yet.")

    with col2:
        st.markdown("**No-Show Rate Trend**")
        st.info(
            "No no-show outcome data is tracked yet — appointments only "
            "store a predicted risk, not a confirmed outcome. Wire this up "
            "once appointment outcomes are recorded."
        )

    st.markdown("**Retrieved Guidelines – Avg. Confidence & Retrieval Count**")
    st.caption(
        "'Confidence' is a heuristic derived from vector-similarity distance, "
        "not a calibrated clinical score."
    )
    if confidence_rows:
        df = pd.DataFrame(confidence_rows).rename(columns={
            "guideline": "Guideline", "avg_confidence": "Avg. Confidence", "retrievals": "Retrievals"
        })
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("No guideline retrievals logged yet.")


def render():
    _nhs_logo()
    _audit_trail()
    _analytics_charts()
