import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

API_BASE = "http://localhost:8000"


# ─────────────────────────────────────────────────────────────
# NHS LOGO
# ─────────────────────────────────────────────────────────────
def _nhs_logo():
    st.markdown("""
    <div class="nhs-header">
        <span class="nhs-logo-box">NHS</span>
        <span style="font-size:1.15rem">MediFlow</span>
        <span style="font-weight:400;font-size:0.9rem;opacity:0.85;margin-left:6px">
            Hospital Capacity Dashboard
        </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# LOAD REAL HOSPITAL DATA FROM THE BACKEND
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def _load_hospitals():
    try:
        resp = requests.get(f"{API_BASE}/analytics/hospitals", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        return pd.DataFrame(data).rename(columns={
            "name": "Hospital", "capacity": "Capacity", "status": "Status"
        })
    except requests.RequestException:
        return None


@st.cache_data(ttl=30)
def _load_summary():
    try:
        resp = requests.get(f"{API_BASE}/analytics/hospitals/summary", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


def _backend_unavailable_notice():
    st.warning(
        "⚠️ Couldn't reach the backend at "
        f"`{API_BASE}`. Make sure it's running "
        "(`uvicorn app.main:app`) and that the database has been seeded "
        "(`python -m scripts.seed_db`)."
    )


# ─────────────────────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────────────────────
def _kpi_row(summary: dict):
    k1, k2, k3 = st.columns(3)

    with k1:
        st.markdown(f"""
        <div class='stat-card' style='background:var(--nhs-red)'>
            <div class='stat-lbl'>Max Capacity</div>
            <div class='stat-val'>{summary['max_capacity']}%</div>
        </div>""", unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class='stat-card' style='background:var(--nhs-blue)'>
            <div class='stat-lbl'>Average Capacity</div>
            <div class='stat-val'>{summary['avg_capacity']}%</div>
        </div>""", unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class='stat-card' style='background:var(--nhs-green)'>
            <div class='stat-lbl'>Hospitals Available</div>
            <div class='stat-val'>{summary['available_count']}</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# PATIENT LOAD CHART
# ─────────────────────────────────────────────────────────────
# NOTE: there's no real A&E patient-load feed behind this yet — it's a
# plausible illustrative curve, kept clearly separate from the real
# hospital-capacity data above. Swap this for a real endpoint (e.g. an
# /analytics/patient-load route backed by appointment/arrival timestamps)
# once that data exists.
def _patient_load_chart():
    import numpy as np

    hours = pd.date_range("08:00", "23:00", freq="15min")
    np.random.seed(1)
    load = 110 + 40 * np.sin(np.linspace(0, 3 * np.pi, len(hours))) \
           + np.random.normal(0, 5, len(hours))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=load, mode="lines",
        line=dict(color="#005EB8", width=3),
        fill="tozeroy", fillcolor="rgba(0,94,184,0.1)",
        name="Patient Load"
    ))
    fig.update_layout(
        height=260, xaxis_title="Time of Day", yaxis_title="Patients in A&E",
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# CAPACITY DISTRIBUTION
# ─────────────────────────────────────────────────────────────
def _capacity_distribution(df: pd.DataFrame):
    fig = px.histogram(df, x="Capacity", nbins=20, title="Hospital Capacity Distribution")
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
    return fig


# ─────────────────────────────────────────────────────────────
# STATUS PIE
# ─────────────────────────────────────────────────────────────
def _status_chart(df: pd.DataFrame):
    counts = df["Status"].value_counts()
    fig = px.pie(values=counts.values, names=counts.index, title="Hospital Status Breakdown")
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
    return fig


# ─────────────────────────────────────────────────────────────
# MAIN RENDER
# ─────────────────────────────────────────────────────────────
def render():
    _nhs_logo()

    df = _load_hospitals()
    summary = _load_summary()

    if df is None or summary is None:
        _backend_unavailable_notice()
        return

    _kpi_row(summary)

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart, col_summary = st.columns([1.6, 1])

    with col_chart:
        st.markdown("**Patient Load**")
        st.plotly_chart(_patient_load_chart(), width="stretch")

    with col_summary:
        worst = df.sort_values("Capacity", ascending=False).iloc[0]

        st.markdown(f"""
        <div class='nhs-card' style='border-left:4px solid var(--nhs-red)'>
            <b>⚠ Highest Pressure</b><br><br>
            {worst['Hospital']} at {worst['Capacity']}% capacity
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='nhs-card' style='border-left:4px solid var(--nhs-green)'>
            <b>AI Recommendation</b><br><br>
            Redirect non-urgent patients to lower capacity hospitals.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(_capacity_distribution(df), width="stretch")
    with c2:
        st.plotly_chart(_status_chart(df), width="stretch")

    st.markdown("---")
    st.markdown("### All NHS Hospitals")

    for _, row in df.sort_values("Capacity", ascending=False).iterrows():
        color = {"Full": "#DA291C", "Busy": "#ED8B00"}.get(row["Status"], "#007F3B")

        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(row["Hospital"])
        c2.write(f"{row['Capacity']}%")
        c3.markdown(
            f"<span style='background:{color};color:white;padding:3px 10px;"
            f"border-radius:4px;font-weight:700'>{row['Status']}</span>",
            unsafe_allow_html=True
        )
