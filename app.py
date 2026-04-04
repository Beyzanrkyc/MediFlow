import streamlit as st
from frontend.pages.Patients     import render as render_patients
from frontend.pages.Appointments import render as render_appointments
from frontend.pages.Dashboard    import render as render_dashboard
from frontend.pages.Analytics    import render as render_analytics


st.set_page_config(
    page_title="MediFlow",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Fira Sans', sans-serif;
}
:root {
    --nhs-blue:   #005EB8;
    --nhs-dark:   #003087;
    --nhs-red:    #DA291C;
    --nhs-green:  #007F3B;
    --nhs-grey:   #768692;
}
            
section[data-testid="stSidebar"] { 
    background: var(--nhs-blue) !important; 
}
             
section[data-testid="stSidebar"] * { 
    color: white !important; 
}

#MainMenu, footer, header { visibility: hidden; }

div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

div[role="radiogroup"] label {
    display: flex !important;
    align-items: center;
    padding: 0.6rem 0.9rem;
    border-radius: 6px;
    margin-bottom: 6px;
    cursor: pointer;
    font-size: 0.95rem;
}

div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.15);
}

div[role="radiogroup"] label[data-checked="true"] {
    background: rgba(255,255,255,0.22);
    font-weight: 700;
    border-left: 3px solid white;
}

.nhs-logo-box {
    background: var(--nhs-blue);
    color: white;
    font-weight: 900;
    font-size: 1rem;
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 1px;
    display: inline-block;
    margin-right: 6px;
}

.chat-bubble-user {
    background:#E8F0FE;
    color: black;
    border-radius:18px 18px 4px 18px;
    padding:0.6rem 1rem; 
    max-width:80%;
    margin-left:auto; 
    margin-bottom:0.5rem; 
}
            
.chat-bubble-ai {
    background:white; 
    color: black;
    border:1px solid #ddd;
    border-radius:18px 18px 18px 4px;
    padding:0.6rem 1rem; 
    max-width:85%; 
    margin-bottom:0.5rem; 
}

</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "triage_done" not in st.session_state:
    st.session_state.triage_done = False

if "triage_level" not in st.session_state:
    st.session_state.triage_level = None

if "active_page" not in st.session_state:
    st.session_state.active_page = "patients"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo
    st.markdown("""
    <div style='padding:0.75rem 0 1.5rem'>
        <span class='nhs-logo-box' style='font-size:1.1rem'>NHS</span>
        <span style='font-size:1.2rem;font-weight:700'>MediFlow</span>
    </div>
    """, unsafe_allow_html=True)

    options = [
        "💬 Symptom Checker",
        "📅 Appointments",
        "📊 Dashboard",
        "📈 Analytics",
    ]

    mapping = {
        "💬 Symptom Checker": "patients",
        "📅 Appointments": "appointments",
        "📊 Dashboard": "dashboard",
        "📈 Analytics": "analytics",
    }

    reverse_mapping = {v: k for k, v in mapping.items()}

    selected = st.radio(
        "Navigation",
        options,
        index=options.index(reverse_mapping[st.session_state.active_page])
    )

    st.session_state.active_page = mapping[selected]

# ── Routing ───────────────────────────────────────────────────────────────────
page = st.session_state.active_page

if page == "patients":
    render_patients()
elif page == "appointments":
    render_appointments()
elif page == "dashboard":
    render_dashboard()
elif page == "analytics":
    render_analytics()