import streamlit as st
import requests

STREAM_URL = "http://localhost:8000/api/chat-stream"


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
    urgent_kw = ["chest pain", "shortness of breath", "heart", "unconscious",
                 "stroke", "severe", "crushing", "radiating"]
    low_kw = ["headache", "cold", "sore throat", "runny nose", "mild fever",
              "sneezing", "cough"]

    t = text.lower()

    if any(k in t for k in urgent_kw):
        return "URGENT"
    if any(k in t for k in low_kw):
        return "LOW"
    return None


def render():
    _nhs_logo()

    # ✅ SESSION STATE
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "audit" not in st.session_state:
        st.session_state.audit = None

    if "triage_done" not in st.session_state:
        st.session_state.triage_done = False

    if "triage_level" not in st.session_state:
        st.session_state.triage_level = None

    col_chat, col_insight = st.columns([1.1, 0.9], gap="medium")

    # ── CHAT ─────────────────────────────────────────────
    with col_chat:
        st.markdown("<div class='nhs-card'>", unsafe_allow_html=True)

        # Chat history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='chat-bubble-user'>{msg['content']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"""
                <div style='display:flex;gap:0.5rem'>
                    <div>🩺</div>
                    <div class='chat-bubble-ai'>{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)

        # 🔥 FORM (ENTER + BUTTON SUPPORT)
        with st.form(key="chat_form", clear_on_submit=True):

            symptom_input = st.text_input(
                "Symptoms",
                placeholder="Describe your symptoms…",
                label_visibility="collapsed",
                key="symptom_box"
            )

            send = st.form_submit_button("Send")

        # 🚀 HANDLE SEND
        if send and symptom_input.strip():

            st.session_state.messages.append(
                {"role": "user", "content": symptom_input}
            )

            level = _triage(symptom_input)

            full_response = ""

            with st.chat_message("assistant"):
                placeholder = st.empty()

                try:
                    response = requests.post(
                        STREAM_URL,
                        json={"message": symptom_input},
                        stream=True
                    )

                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            text = chunk.decode("utf-8")
                            full_response += text
                            placeholder.markdown(full_response)

                except Exception:
                    full_response = "⚠️ Backend not reachable."

            # TRIAGE
            if level == "URGENT":
                full_response = "⚠️ **URGENT: Go to A&E immediately.**\n\n" + full_response
            elif level == "LOW":
                full_response = "🟢 **Low risk: Monitor symptoms.**\n\n" + full_response

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

            # 🔥 SAVE AUDIT DATA
            st.session_state.audit = {
                "query": symptom_input,
                "note": "Streaming mode currently does not return sources yet",
            }

            st.session_state.triage_done = level is not None
            st.session_state.triage_level = level

            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── INSIGHTS ─────────────────────────────────────────
    with col_insight:
        st.markdown("## Clinical Insights")

        # Audit Trail
        if st.session_state.audit:
            audit = st.session_state.audit

            st.markdown("### Clinical Audit Trail")

            st.markdown(f"""
            <div class='audit-section'>
                <h5>Patient Input</h5>
                <p>{audit['query']}</p>
            </div>
            """, unsafe_allow_html=True)

            st.info("Next step: connect backend sources here 🔥")

        # Triage Panel
        if st.session_state.triage_done:
            if st.session_state.triage_level == "URGENT":
                st.markdown("""
                <div class='triage-urgent'>
                    <h3>URGENT — Go to A&E</h3>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("LOW RISK — Monitor symptoms")

            if st.button("🔄 Reset"):
                st.session_state.messages = []
                st.session_state.audit = None
                st.session_state.triage_done = False
                st.session_state.triage_level = None
                st.rerun()
        else:
            st.info("Enter symptoms to begin triage.")