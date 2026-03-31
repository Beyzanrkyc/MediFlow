import streamlit as st


def render_sidebar() -> str:
    """Render the NHS MediFlow sidebar with button-style navigation."""

    # Init active page in session state
    if "active_page" not in st.session_state:
        st.session_state.active_page = "patients"

    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────────────
        st.markdown("""
        <div style='padding:0.75rem 0 1.5rem'>
            <span class='nhs-logo-box' style='font-size:1.1rem'>NHS</span>
            <span style='font-size:1.2rem;font-weight:700'>MediFlow</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Button CSS ────────────────────────────────────────────────────────
        st.markdown("""
        <style>
        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            text-align: left !important;
            background: transparent;
            color: white !important;
            border: none;
            border-radius: 6px;
            padding: 0.55rem 0.9rem;
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 4px;
            cursor: pointer;
            transition: background 0.15s ease;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.15) !important;
            color: white !important;
            border: none;
        }
        section[data-testid="stSidebar"] .stButton > button:focus {
            box-shadow: none;
            outline: none;
        }
        section[data-testid="stSidebar"] .nav-active .stButton > button {
            background: rgba(255,255,255,0.22) !important;
            font-weight: 700 !important;
            border-left: 3px solid white !important;
            padding-left: calc(0.9rem - 3px) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # ── Nav buttons ───────────────────────────────────────────────────────
        nav_items = [
            ("patients",     "💬  Symptom Checker"),
            ("appointments", "📅  Appointments"),
            ("dashboard",    "📊  Dashboard"),
            ("analytics",    "📈  Analytics"),
        ]

        for page_key, label in nav_items:
            is_active = st.session_state.active_page == page_key
            if is_active:
                st.markdown("<div class='nav-active'>", unsafe_allow_html=True)
            if st.button(label, key=f"nav_{page_key}"):
                st.session_state.active_page = page_key
                st.rerun()
            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)

        # ── Footer ────────────────────────────────────────────────────────────
        st.markdown("---")
        # st.markdown(
        #     "<small>Logged in as<br><b>Whaltad Werhclor</b></small>",
        #     unsafe_allow_html=True,
        # )

    return st.session_state.active_page