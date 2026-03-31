import streamlit as st
import time


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


_CALENDAR_HTML = """
<style>
.cal-table { border-collapse:collapse; width:100%; }
.cal-table th { text-align:center; padding:4px 8px; font-size:0.85rem; color:#555; }
.cal-table td { text-align:center; padding:4px 6px; }
.slot-avail { background:#DBEAFE; border-radius:4px; height:28px; width:100%; display:block; }
.slot-busy  { background:#FEE2E2; border-radius:4px; height:28px; width:100%; display:block; }
.slot-best  {
    background:#16A34A; border-radius:4px; height:28px; width:100%; display:block;
    color:white; font-size:0.7rem; font-weight:700; line-height:28px;
}
</style>
<table class='cal-table'>
  <tr><th></th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th></tr>
  <tr>
    <td style='font-size:0.8rem;color:#555;white-space:nowrap'>1 pm</td>
    <td><span class='slot-avail'></span></td>
    <td><span class='slot-avail'></span></td>
    <td><span class='slot-avail'></span></td>
    <td><span class='slot-avail'></span></td>
    <td><span class='slot-avail'></span></td>
  </tr>
  <tr>
    <td style='font-size:0.8rem;color:#555;white-space:nowrap'>2 pm</td>
    <td><span class='slot-avail'></span></td>
    <td><span class='slot-best'>Best Slot<br>10:30 AM</span></td>
    <td><span class='slot-busy'></span></td>
    <td><span class='slot-busy'></span></td>
    <td><span class='slot-avail'></span></td>
  </tr>
  <tr>
    <td style='font-size:0.8rem;color:#555;white-space:nowrap'>3 pm</td>
    <td><span class='slot-avail'></span></td>
    <td><span class='slot-avail'></span></td>
    <td><span class='slot-avail'></span></td>
    <td><span class='slot-avail'></span></td>
    <td><span class='slot-avail'></span></td>
  </tr>
</table>
"""


def render():
    _nhs_logo()

    col_cal, col_triage = st.columns([1.3, 0.7], gap="medium")

    # ── Calendar panel ────────────────────────────────────────────────────────
    with col_cal:
        st.markdown("<div class='nhs-card'>", unsafe_allow_html=True)

        # Retrieved guidelines summary
        st.markdown("**Retrieved Guidelines**")
        st.markdown("""
        <div style='margin:0.5rem 0 1rem'>
            <b>NICE Guideline CG95: Chest Pain</b><br>
            <small style='color:var(--nhs-grey)'>Confidence: 92%</small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(_CALENDAR_HTML, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class='no-show-alert'>
            ⚠️ <b>No-Show Alert:</b> High risk of cancellation. Send reminder to patient.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📩 Send Reminder", type="primary"):
            st.success("Reminder sent to patient successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Triage Result panel ───────────────────────────────────────────────────
    with col_triage:
        triage_level = st.session_state.get("triage_level", "URGENT")

        if triage_level == "URGENT" or triage_level is None:
            st.markdown("""
            <div class='triage-urgent'>
                <span class='badge-red' style='font-size:0.8rem'>Triage Result</span>
                <h3 style='color:white;margin:0.5rem 0 0.25rem'>● URGENT<br>Go to A&amp;E</h3>
                <p style='color:white;margin:0;font-size:0.88rem'>
                    Possible cardiac issue detected.<br>Immediate action required.
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

        st.markdown("<br><b>Risk Level</b>", unsafe_allow_html=True)
        risk_val = 82 if (triage_level == "URGENT" or triage_level is None) else 30
        st.progress(risk_val / 100)

        st.markdown("""
        <div style='display:flex;gap:4px;margin-top:4px'>
            <div style='flex:3;height:8px;background:#22C55E;border-radius:3px'></div>
            <div style='flex:3;height:8px;background:#F59E0B;border-radius:3px'></div>
            <div style='flex:3;height:8px;background:#EF4444;border-radius:3px'></div>
            <div style='flex:2;height:8px;background:#ddd;border-radius:3px'></div>
        </div>
        <div style='display:flex;justify-content:space-between;font-size:0.7rem;color:#777;margin-top:2px'>
            <span>Low</span><span>Medium</span><span>High</span><span>Critical</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Upcoming Appointments**")
        st.markdown("""
        | Time     | Patient        | Type     |
        |----------|---------------|----------|
        | 10:30 AM | W. Werhclor   | Cardiology |
        | 11:15 AM | J. Smith      | GP Review  |
        | 2:00 PM  | A. Patel      | Follow-up  |
        """)