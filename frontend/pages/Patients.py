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

    # ✅ Session state init
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "sources" not in st.session_state:
        st.session_state.sources = []

    if "triage_done" not in st.session_state:
        st.session_state.triage_done = False

    if "triage_level" not in st.session_state:
        st.session_state.triage_level = None

    col_chat, col_insight = st.columns([1.1, 0.9], gap="medium")

    # ── CHAT PANEL ─────────────────────────────────────────────
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
                <div style='display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.5rem'>
                    <div style='font-size:1.5rem'>🩺</div>
                    <div class='chat-bubble-ai'>{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)

        symptom_input = st.text_input(
            "Symptoms",
            placeholder="Describe your symptoms…",
            label_visibility="collapsed",
            key="symptom_box",
        )

        send = st.button("Send", type="primary")

        # 🔥 SEND MESSAGE
        if send and symptom_input.strip():

            # Save user message
            st.session_state.messages.append(
                {"role": "user", "content": symptom_input}
            )

            level = _triage(symptom_input)

            full_response = ""

            # 🔥 STREAMING RESPONSE
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

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
                            message_placeholder.markdown(full_response)

                except Exception:
                    full_response = "⚠️ Backend not reachable."

            # 🚨 TRIAGE SAFETY LAYER
            if level == "URGENT":
                full_response = "⚠️ **URGENT: Go to A&E immediately.**\n\n" + full_response
            elif level == "LOW":
                full_response = "🟢 **Low risk: Monitor symptoms.**\n\n" + full_response

            # Save assistant response
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

            st.session_state.triage_done = level is not None
            st.session_state.triage_level = level

            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── CLINICAL INSIGHTS ─────────────────────────────────────
    with col_insight:
        st.markdown("**Clinical Insights**")

        # ⚠️ NOTE: Streaming endpoint doesn't return sources
        # (You can upgrade this later if needed)
        if st.session_state.sources:
            st.markdown(
                "<span class='badge-red'>Retrieved Guidelines</span>",
                unsafe_allow_html=True,
            )

            for src in st.session_state.sources:
                st.markdown(f"""
                <div class='nhs-card' style='margin-top:0.5rem'>
                    <b>{src}</b><br>
                    <small style='color:var(--nhs-grey)'>Source</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Streaming mode active — sources not shown yet.")

        # Triage result UI
        if st.session_state.triage_done:
            if st.session_state.triage_level == "URGENT":
                st.markdown("""
                <div class='triage-urgent'>
                    <span class='badge-red'>Triage Result</span>
                    <h3>● URGENT — Go to A&E</h3>
                    <p>Possible serious condition detected.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:var(--nhs-green);color:white;border-radius:6px;
                            padding:1rem 1.25rem;margin-top:0.75rem'>
                    <b>Triage Result</b>
                    <h3 style='color:white;margin:0.25rem 0'>● LOW RISK</h3>
                    <p style='color:white;margin:0;font-size:0.9rem'>
                        Monitor symptoms and contact GP if needed.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🔄 Clear & Start Again"):
                st.session_state.messages = []
                st.session_state.sources = []
                st.session_state.triage_done = False
                st.session_state.triage_level = None
                st.rerun()
        else:
            st.info("Complete the symptom assessment to receive a triage result.")