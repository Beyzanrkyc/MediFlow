from datetime import datetime

import requests
import streamlit as st

API_BASE = "http://localhost:8000"


def _nhs_logo():
    st.markdown("""
    <div class="nhs-header">
        <span class="nhs-logo-box">NHS</span>
        <span style="font-size:1.15rem">MediFlow</span>
        <span style="font-weight:400;font-size:0.9rem;opacity:0.85;margin-left:6px">
            Appointments
        </span>
    </div>
    """, unsafe_allow_html=True)


def _backend_unavailable_notice():
    st.warning(
        f"⚠️ Couldn't reach the backend at `{API_BASE}`. Make sure it's running "
        "(`uvicorn app.main:app`) and seeded (`python -m scripts.seed_db`)."
    )


@st.cache_data(ttl=15)
def _load_appointments():
    try:
        resp = requests.get(f"{API_BASE}/scheduling/appointments", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


@st.cache_data(ttl=15)
def _load_best_slot(specialty: str):
    try:
        resp = requests.get(
            f"{API_BASE}/scheduling/best-slot", params={"specialty": specialty}, timeout=5
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


def _send_reminder(appointment_id: int):
    try:
        resp = requests.post(f"{API_BASE}/scheduling/appointments/{appointment_id}/remind", timeout=5)
        resp.raise_for_status()
        return True
    except requests.RequestException:
        return False


def _fmt_time(iso_str: str) -> str:
    try:
        return datetime.fromisoformat(iso_str).strftime("%a %d %b, %I:%M %p")
    except ValueError:
        return iso_str


def render():
    _nhs_logo()

    appointments = _load_appointments()
    if appointments is None:
        _backend_unavailable_notice()
        return

    col_cal, col_triage = st.columns([1.3, 0.7], gap="medium")

    # ── Scheduling panel ─────────────────────────────────────────────────────
    with col_cal:
        st.markdown("<div class='nhs-card'>", unsafe_allow_html=True)

        st.markdown("**Suggest Best Slot**")
        specialty = st.selectbox(
            "Specialty",
            ["GP Review", "Cardiology", "Follow-up", "Respiratory", "General Medicine"],
            label_visibility="collapsed",
        )
        best = _load_best_slot(specialty)
        if best:
            st.markdown(f"""
            <div style='margin:0.5rem 0 1rem'>
                <b>Recommended slot:</b> {_fmt_time(best['slot'])}<br>
                <small style='color:var(--nhs-grey)'>
                    Estimated no-show risk: {best['estimated_no_show_risk']*100:.0f}%
                </small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No available slots found for this specialty in the next 5 weekdays.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Upcoming Appointments**")

        if not appointments:
            st.info("No appointments yet — run `python -m scripts.seed_db` to add sample data.")
        else:
            high_risk = [a for a in appointments if a["no_show_risk"] >= 0.5]
            if high_risk:
                worst = max(high_risk, key=lambda a: a["no_show_risk"])
                st.markdown(f"""
                <div class='no-show-alert'>
                    ⚠️ <b>No-Show Alert:</b> {worst['patient_name']}'s
                    {worst['specialty']} appointment on {_fmt_time(worst['scheduled_time'])}
                    has a {worst['no_show_risk']*100:.0f}% predicted no-show risk.
                </div>
                """, unsafe_allow_html=True)

            for appt in appointments:
                c1, c2, c3, c4 = st.columns([2.2, 1.3, 1, 1])
                c1.write(appt["patient_name"])
                c2.write(f"{appt['specialty']} · {_fmt_time(appt['scheduled_time'])}")
                risk_color = "#DA291C" if appt["no_show_risk"] >= 0.5 else "#007F3B"
                c3.markdown(
                    f"<span style='color:{risk_color};font-weight:700'>"
                    f"{appt['no_show_risk']*100:.0f}% risk</span>",
                    unsafe_allow_html=True,
                )
                if appt["reminder_sent"]:
                    c4.write("✅ Sent")
                elif c4.button("Remind", key=f"remind_{appt['id']}"):
                    if _send_reminder(appt["id"]):
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to send reminder.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Triage Result panel ───────────────────────────────────────────────────
    with col_triage:
        triage_level = st.session_state.get("triage_level")

        if triage_level == "URGENT" or triage_level is None:
            st.markdown("""
            <div class='triage-urgent'>
                <span class='badge-red' style='font-size:0.8rem'>Triage Result</span>
                <h3 style='color:white;margin:0.5rem 0 0.25rem'>● URGENT<br>Go to A&amp;E</h3>
                <p style='color:white;margin:0;font-size:0.88rem'>
                    From the Symptom Checker's latest assessment.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:var(--nhs-green);color:white;border-radius:6px;
                        padding:1rem 1.25rem;margin-top:0.75rem'>
                <b>Triage Result</b>
                <h3 style='color:white;margin:0.25rem 0'>● LOW RISK</h3>
                <p style='color:white;margin:0;font-size:0.9rem'>
                    Monitor symptoms. Contact GP if no improvement.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.caption(
            "Reflects `st.session_state.triage_level` from the Symptom Checker page — "
            "run a symptom check there first to populate this."
        )
