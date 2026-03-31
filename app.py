import streamlit as st
from frontend.components.sidebar import render_sidebar
from frontend.pages.Patients     import render as render_patients
from frontend.pages.Appointments import render as render_appointments
from frontend.pages.Dashboard    import render as render_dashboard
from frontend.pages.Analytics    import render as render_analytics


st.set_page_config(
    page_title="MediFlow",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Global CSS (shared across all pages) ──────────────────────────────────────
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
    --nhs-orange: #ED8B00;
    --nhs-white:  #FFFFFF;
    --nhs-grey:   #768692;
    --bg-light:   #F0F4F5;
}
section[data-testid="stSidebar"] { 
            background: var(--nhs-blue) !important; 
}
section[data-testid="stSidebar"] * { 
            color: white !important; 
}
#MainMenu, footer, header { visibility: hidden; }

.nhs-card {
    background: white;
    color: black;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.12);
    margin-bottom: 1rem;
}
.nhs-header {
    background: var(--nhs-blue);
    color: white !important;
    border-radius: 6px 6px 0 0;
    padding: 0.6rem 1rem;
    font-weight: 700;
    font-size: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
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
.badge-red   { background:var(--nhs-red);   color:white; padding:0.3rem 0.7rem; border-radius:4px; font-weight:700; font-size:0.85rem; }
.badge-blue  { background:var(--nhs-blue);  color:white; padding:0.3rem 0.7rem; border-radius:4px; font-weight:700; font-size:0.85rem; }
.badge-green { background:var(--nhs-green); color:white; padding:0.3rem 0.7rem; border-radius:4px; font-weight:700; font-size:0.85rem; }

.triage-urgent {
    background: var(--nhs-red); color: white;
    border-radius: 6px; padding: 1rem 1.25rem; margin-top: 0.75rem;
}
.triage-urgent h3 { color: white; margin: 0 0 0.25rem; font-size: 1.4rem; }
.triage-urgent p  { color: white; margin: 0; font-size: 0.9rem; }

.stat-card { border-radius:6px; padding:1rem; text-align:center; color:white; font-weight:700; }
.stat-val  { font-size:2rem; line-height:1; }
.stat-lbl  { font-size:0.8rem; font-weight:400; margin-top:0.25rem; }

.audit-section { border:1px solid #ddd; border-radius:6px; padding:0.75rem 1rem; margin-bottom:0.75rem; }
.audit-section h5 { color:var(--nhs-blue); margin:0 0 0.35rem; font-size:0.95rem; }

.chat-bubble-user {
    background:#E8F0FE;
    color: black;
    border-radius:18px 18px 4px 18px;
    padding:0.6rem 1rem; 
    max-width:80%;
    margin-left:auto; 
    margin-bottom:0.5rem; 
    font-size:0.95rem;
}
.chat-bubble-ai {
    background:white; 
    color: black;
    border:1px solid #ddd;
    border-radius:18px 18px 18px 4px;
    padding:0.6rem 1rem; 
    max-width:85%; 
    margin-bottom:0.5rem; 
    font-size:0.95rem;
}
.no-show-alert {
    background:#FFF3CD; 
    border:1px solid #FFC107; 
    border-radius:6px;
    padding:0.5rem 0.75rem; 
    font-size:0.85rem; 
    color:#664d03;
    display:flex; 
    align-items:center; 
    gap:0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "triage_done" not in st.session_state: st.session_state.triage_done = False
if "triage_level"not in st.session_state: st.session_state.triage_level= None

# ── Routing ───────────────────────────────────────────────────────────────────
page = render_sidebar()

if   page == "patients":     render_patients()
elif page == "appointments": render_appointments()
elif page == "dashboard":    render_dashboard()
elif page == "analytics":    render_analytics()