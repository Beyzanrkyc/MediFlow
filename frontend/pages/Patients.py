import streamlit as st


def _nhs_logo():
    st.markdown("""
    <div class="nhs-header">
        <span class="nhs-logo-box">NHS</span>
        <span style="font-size:1.15rem">MediFlow</span>
        <span style="font-weight:400;font-size:0.9rem;opacity:0.85;margin-left:6px">
            AI Symptom Checker
        </span>
    </div>
    """, unsafe_allow_html=True)


def _triage(text: str):
    """Simple rule-based triage for demo purposes."""
    urgent_kw = ["chest pain", "shortness of breath", "heart", "unconscious",
                 "stroke", "severe", "crushing", "radiating"]
    low_kw    = ["headache", "cold", "sore throat", "runny nose", "mild fever",
                 "sneezing", "cough"]
    t = text.lower()
    if any(k in t for k in urgent_kw):
        return "URGENT"
    if any(k in t for k in low_kw):
        return "LOW"
    return None


def render():
    _nhs_logo()

    col_chat, col_insight = st.columns([1.1, 0.9], gap="medium")

    # ── Chat panel ────────────────────────────────────────────────────────────
    with col_chat:
        st.markdown("<div class='nhs-card'>", unsafe_allow_html=True)

        # Render chat history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='chat-bubble-user'>{msg['content']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"""
                <div style='display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.5rem'>
                    <div style='font-size:1.5rem'>🩺</div>
                    <div class='chat-bubble-ai'>{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)

        symptom_input = st.text_input(
            "Symptoms", placeholder="Describe your symptoms…",
            label_visibility="collapsed", key="symptom_box",
        )
        send = st.button("Send", type="primary")

        if send and symptom_input.strip():
            st.session_state.messages.append(
                {"role": "user", "content": symptom_input}
            )

            level = _triage(symptom_input)
            if level == "URGENT":
                reply = (
                    "Based on NHS guidelines, it's recommended you go to the "
                    "emergency department as soon as possible. You may be "
                    "experiencing a serious heart issue."
                )
            elif level == "LOW":
                reply = (
                    "Your symptoms appear mild. Rest, stay hydrated and monitor "
                    "your condition. Contact your GP if symptoms worsen over 48 hours."
                )
            else:
                reply = (
                    "Thank you for describing your symptoms. Could you tell me "
                    "more? For example, how long have you had these symptoms and "
                    "how severe are they on a scale of 1–10?"
                )
                level = None

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
            st.session_state.triage_done  = level is not None
            st.session_state.triage_level = level
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Clinical Insights panel ───────────────────────────────────────────────
    with col_insight:
        st.markdown("**Clinical Insights**")

        st.markdown(
            "<span class='badge-red'>Retrieved Guidelines</span>",
            unsafe_allow_html=True,
        )
        st.markdown("""
        <div class='nhs-card' style='margin-top:0.5rem'>
            <b>NICE Guideline CG95: Chest Pain</b><br>
            <small style='color:var(--nhs-grey)'>Confidence: 92%</small>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.triage_done:
            if st.session_state.triage_level == "URGENT":
                st.markdown("""
                <div class='triage-urgent'>
                    <span class='badge-red' style='font-size:0.8rem'>Triage Result</span>
                    <h3>● URGENT<br>Go to A&amp;E</h3>
                    <p>Possible cardiac issue detected.<br>Immediate action required.</p>
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

            if st.button("🔄 Clear & Start Again"):
                st.session_state.messages     = []
                st.session_state.triage_done  = False
                st.session_state.triage_level = None
                st.rerun()
        else:
            st.info("Complete the symptom assessment to receive a triage result.")