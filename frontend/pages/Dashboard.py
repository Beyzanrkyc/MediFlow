import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def _nhs_logo():
    st.markdown("""
    <div class="nhs-header">
        <span class="nhs-logo-box">NHS</span>
        <span style="font-size:1.15rem">MediFlow</span>
        <span style="font-weight:400;font-size:0.9rem;opacity:0.85;margin-left:6px">
            Operational Dashboard
        </span>
    </div>
    """, unsafe_allow_html=True)


def _kpi_row():
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown("""
        <div class='stat-card' style='background:var(--nhs-red)'>
            <div class='stat-lbl'>A&amp;E Capacity</div>
            <div class='stat-val'>94%</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown("""
        <div class='stat-card' style='background:var(--nhs-blue)'>
            <div class='stat-lbl'>Avg. Wait Time</div>
            <div class='stat-val'>3h 20m</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown("""
        <div class='stat-card' style='background:var(--nhs-blue)'>
            <div class='stat-lbl'>No-Show Rate</div>
            <div class='stat-val'>18%</div>
        </div>""", unsafe_allow_html=True)


def _patient_load_chart():
    np.random.seed(42)
    x = np.linspace(0, 4 * np.pi, 80)
    y = 120 + 60 * np.sin(x) + np.random.normal(0, 10, 80)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(80)), y=y,
        mode="lines",
        line=dict(color="#005EB8", width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(0,94,184,0.12)",
        name="Patient Load",
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=10, b=30),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            tickvals=[0, 19, 37, 60, 79],
            ticktext=["19pm", "14pm", "17pm", "25pm", "32pm"],
            showgrid=False, zeroline=False,
        ),
        yaxis=dict(
            tickvals=[90, 150, 250],
            showgrid=True, gridcolor="#eee", zeroline=False,
        ),
        showlegend=False,
    )
    return fig


def _hospital_table():
    data = {
        "Hospital":  ["Royal South Hants", "Basingstoke General", "St. Mary's Hospital"],
        "Capacity":  ["94%", "63%", "57%"],
        "Status":    ["Full", "Available", "Available"],
    }
    return pd.DataFrame(data)


def render():
    _nhs_logo()
    _kpi_row()

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart, col_summary = st.columns([1.6, 1], gap="medium")

    with col_chart:
        st.markdown("**Patient Load**")
        fig = _patient_load_chart()
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with col_summary:
        st.markdown("""
        <div class='nhs-card' style='border-left:4px solid var(--nhs-orange)'>
            <b>🔵 Summary</b><br><br>
            Cardiology at Royal South is at 94% capacity.
            Recommend redirecting patients to Basingstoke General.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='nhs-card' style='border-left:4px solid var(--nhs-green)'>
            <b>✅ Action Taken</b><br><br>
            3 patients redirected to Basingstoke General this afternoon.
        </div>
        """, unsafe_allow_html=True)

    # ── Hospital capacity table ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Hospital Capacity**")

    col_h, col_c, col_s = st.columns([2, 1, 1])
    col_h.markdown("**Hospital**")
    col_c.markdown("**Capacity**")
    col_s.markdown("**Status**")

    hospitals = [
        ("Royal South Hants",    "94%", "Full",      "#DA291C"),
        ("Basingstoke General",  "63%", "Available", "#007F3B"),
        ("St. Mary's Hospital",  "57%", "Available", "#007F3B"),
    ]

    for name, cap, status, colour in hospitals:
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(name)
        c2.write(cap)
        c3.markdown(
            f"<span style='background:{colour};color:white;padding:2px 10px;"
            f"border-radius:4px;font-size:0.85rem;font-weight:700'>{status}</span>",
            unsafe_allow_html=True,
        )