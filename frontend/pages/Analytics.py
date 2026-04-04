import streamlit as st
import plotly.graph_objects as go
import numpy as np


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


def _audit_trail():
    st.markdown("## Clinical Audit Trail")

    st.markdown("""
    <div class='audit-section'>
        <h5>Patient Input</h5>
        <p style='margin:0'>Symptoms: Chest pain, shortness of breath</p>
        <small style='color:#888'>Recorded: 2024-01-15 · 14:32 UTC</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='audit-section'>
        <h5>Retrieved Guidelines</h5>
        <ul style='margin:0;padding-left:1.2rem'>
            <li>NICE Guideline CG95: Chest Pain</li>
            <li>Confidence Score: 92%</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='audit-section'>
        <h5>AI Reasoning Summary</h5>
        <p style='margin:0'>
            Based on the reported symptoms, urgent intervention is required to rule out
            a serious cardiac event. Immediate A&amp;E referral is recommended.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Full Audit Log (JSON)"):
        st.json({
            "session_id":          "MF-2024-78432",
            "timestamp":           "2024-01-15T14:32:11Z",
            "patient":             {"id": "P-10291", "name": "Whaltad Werhclor"},
            "input":               {"symptoms": ["chest pain", "shortness of breath"],
                                    "duration": "30 minutes"},
            "guideline_retrieved": {"id": "CG95", "title": "Chest Pain",
                                    "confidence": 0.92},
            "triage_result":       {"level": "URGENT", "action": "Go to A&E"},
            "ai_reasoning":        "Possible ACS/cardiac event. Immediate intervention required.",
        })


def _analytics_charts():
    st.markdown("---")
    st.markdown("## Analytics Overview")

    col1, col2 = st.columns(2, gap="medium")

    # ── Triage level distribution ─────────────────────────────────────────────
    with col1:
        st.markdown("**Triage Level Distribution (Last 30 days)**")
        fig1 = go.Figure(go.Pie(
            labels=["URGENT", "MEDIUM", "LOW"],
            values=[34, 41, 25],
            marker_colors=["#DA291C", "#ED8B00", "#007F3B"],
            hole=0.45,
            textinfo="label+percent",
        ))
        fig1.update_layout(
            height=260, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False, paper_bgcolor="white",
        )
        st.plotly_chart(fig1, width="stretch", config={"displayModeBar": False})

    # ── No-show trend ─────────────────────────────────────────────────────────
    with col2:
        st.markdown("**No-Show Rate Trend (Last 12 weeks)**")
        weeks = [f"W{i}" for i in range(1, 13)]
        rates = [22, 19, 21, 18, 20, 17, 15, 18, 16, 14, 18, 18]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=weeks, y=rates,
            marker_color=["#DA291C" if r > 18 else "#005EB8" for r in rates],
        ))
        fig2.update_layout(
            height=260, margin=dict(l=10, r=10, t=10, b=30),
            paper_bgcolor="white", plot_bgcolor="white",
            yaxis=dict(title="Rate (%)", showgrid=True, gridcolor="black"),
            xaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

    # ── Guideline confidence scores ───────────────────────────────────────────
    st.markdown("**Top Retrieved Guidelines – Confidence Scores**")
    guidelines = {
        "Guideline": [
            "CG95 – Chest Pain",
            "NG185 – COVID-19",
            "CG180 – Atrial Fibrillation",
            "NG12 – Suspected Cancer",
            "CG109 – Transient Loss of Consciousness",
        ],
        "Confidence": [92, 88, 81, 76, 70],
        "Retrievals": [142, 98, 74, 61, 53],
    }
    import pandas as pd
    df = pd.DataFrame(guidelines)
    st.dataframe(df, width="stretch", hide_index=True)


def render():
    _nhs_logo()
    _audit_trail()
    _analytics_charts()