"""Sharp Interview - Questions & Analysis with Full Auth"""
import streamlit as st
import requests
import os

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("user"): return {"success": True, "message": "✅ Check your email to confirm!"}
        return {"success": False, "message": data.get("error_description") or "Sign up failed"}
    except Exception as e: return {"success": False, "message": str(e)}

def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"): return {"success": True, "user": data.get("user")}
        return {"success": False, "message": data.get("error_description") or "Invalid credentials"}
    except Exception as e: return {"success": False, "message": str(e)}

def supabase_magic_link(email):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email}, timeout=10)
        if r.status_code == 200: return {"success": True, "message": "✨ Magic link sent!"}
        return {"success": False, "message": "Failed to send"}
    except Exception as e: return {"success": False, "message": str(e)}

def init_session():
    for k, v in [('authenticated', False), ('user', None), ('is_god', False)]:
        if k not in st.session_state: st.session_state[k] = v

def get_user_email():
    if st.session_state.is_god: return "GOD MODE"
    if st.session_state.user: return st.session_state.user.get("email", "User")
    return "User"

def call_claude(prompt, max_tokens=2500):
    if not ANTHROPIC_API_KEY: return "Error: API key not set"
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200: return r.json()["content"][0]["text"]
        return f"Error: {r.status_code}"
    except Exception as e: return f"Error: {str(e)}"

def render_auth():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%); }
    * { font-family: 'Nunito', sans-serif !important; }
    .stTextInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(99,102,241,0.3) !important; border-radius: 10px !important; color: white !important; }
    .stButton > button { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 6px; }
    .stTabs [data-baseweb="tab"] { background: transparent !important; color: #9ca3af !important; border-radius: 8px !important; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; }
    </style>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:50px 0 40px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="color:white;margin:0 0 8px;">Sharp Interview</h1><p style="color:#9ca3af;">Questions & Analysis</p></div>""", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@company.com", key="le")
            password = st.text_input("Password", type="password", key="lp")
            if st.button("🚀 Log In", use_container_width=True):
                if password == GOD_PASSWORD: st.session_state.authenticated = True; st.session_state.is_god = True; st.session_state.user = {"email": "GOD"}; st.rerun()
                elif email and password:
                    r = supabase_sign_in(email, password)
                    if r["success"]: st.session_state.authenticated = True; st.session_state.user = r["user"]; st.rerun()
                    else: st.error(r["message"])
            st.markdown("<p style='text-align:center;color:#6b7280;margin:16px 0;'>— or —</p>", unsafe_allow_html=True)
            magic = st.text_input("", placeholder="Email for magic link", key="me", label_visibility="collapsed")
            if st.button("✨ Send Magic Link", use_container_width=True, key="ml"):
                if magic: r = supabase_magic_link(magic); st.success(r["message"]) if r["success"] else st.error(r["message"])
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            se, sp, sc = st.text_input("Email", key="se"), st.text_input("Password", type="password", key="sp"), st.text_input("Confirm", type="password", key="sc")
            if st.button("🎉 Create Account", use_container_width=True):
                if sp != sc: st.error("Passwords don't match")
                elif len(sp) < 6: st.warning("6+ characters required")
                elif se and sp: r = supabase_sign_up(se, sp); st.success(r["message"]) if r["success"] else st.error(r["message"])

st.set_page_config(page_title="Sharp Interview", page_icon="🎯", layout="wide")
init_session()
if not st.session_state.authenticated: render_auth(); st.stop()

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%); }
h1,h2,h3 { color: white !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; }
.output-box { background: rgba(255,255,255,0.03); border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 24px; margin: 16px 0; }
p,span,label { color: #e5e5e5 !important; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<div style='padding:16px;background:rgba(99,102,241,0.1);border-radius:12px;'><p style='color:#9ca3af;margin:0;font-size:0.75rem;'>Logged in as</p><p style='color:white;margin:0;'>{get_user_email()}</p></div>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True): st.session_state.authenticated = False; st.session_state.user = None; st.session_state.is_god = False; st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:24px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:32px;"><img src="https://sharphuman.com/logo1-3.png" style="width:50px;"><div><h1 style="margin:0;">Sharp Interview</h1><p style="color:#9ca3af;margin:0;">Questions • Analysis • Scorecards</p></div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["❓ Generate Questions", "📝 Analyze Interview", "📋 Scorecard"])

with tab1:
    c1, c2 = st.columns([2, 1])
    title = c1.text_input("Job Title", placeholder="Senior Software Engineer")
    jd = c1.text_area("Job Requirements", height=150, placeholder="Key requirements and responsibilities...")
    stage = c2.selectbox("Interview Stage", ["Phone Screen", "Technical", "Hiring Manager", "Culture/Values", "Final Round"])
    duration = c2.select_slider("Duration", ["15 min", "30 min", "45 min", "60 min"], value="45 min")
    focus = c2.multiselect("Focus Areas", ["Technical Skills", "Behavioral", "Problem Solving", "Leadership", "Culture Fit"])
    if st.button("⚡ Generate Questions", type="primary", use_container_width=True):
        if title:
            with st.spinner("⚡ Generating..."): st.markdown(f'<div class="output-box">{call_claude(f"Generate {stage} interview questions for {title} role, {duration} duration. Focus: {focus}. JD: {jd}. Include: opening questions, 8-10 core questions with follow-ups, closing questions, what to look for in good answers, red flags to watch.")}</div>', unsafe_allow_html=True)

with tab2:
    transcript = st.text_area("📝 Interview Transcript", height=300, placeholder="Paste interview transcript or notes...")
    role = st.text_input("Role", placeholder="Senior Software Engineer", key="role2")
    if st.button("🔍 Analyze Interview", type="primary", use_container_width=True, key="analyze"):
        if transcript:
            with st.spinner("🔍 Analyzing..."): st.markdown(f'<div class="output-box">{call_claude(f"Analyze this interview for {role} role.\n\nTranscript:\n{transcript}\n\nProvide: Overall assessment, green flags, red flags, follow-up recommendations, hire/no-hire recommendation with reasoning.")}</div>', unsafe_allow_html=True)

with tab3:
    sc_role = st.text_input("Role", placeholder="Senior Software Engineer", key="role3")
    competencies = st.text_area("Competencies to Evaluate", height=100, placeholder="Technical skills, communication, leadership...")
    if st.button("📋 Generate Scorecard", type="primary", use_container_width=True, key="scorecard"):
        if sc_role:
            with st.spinner("📋 Generating..."): st.markdown(f'<div class="output-box"><pre>{call_claude(f"Create interview scorecard for {sc_role}. Competencies: {competencies or 'Technical, Communication, Problem Solving, Culture Fit'}. Include: 1-5 rating scale for each competency, behavioral indicators, space for notes, overall recommendation section.")}</pre></div>', unsafe_allow_html=True)
