"""
Sharp Screen - CV Screening, Ranking & Anonymization
STANDALONE VERSION
"""
import streamlit as st
import requests
import os

# ============== CONFIG ==============
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOD_PASSWORD = "G0DHum@n101!!!"
DEMO_PASSWORD = "D3M0Human101!!!"

def call_claude(prompt, max_tokens=4096):
    if not ANTHROPIC_API_KEY: return "Error: ANTHROPIC_API_KEY not set", 0, 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200: return r.json()["content"][0]["text"], 0, 0
        return f"API Error: {r.status_code}", 0, 0
    except Exception as e: return f"Error: {str(e)}", 0, 0

def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.access_level = None
    return st.session_state.authenticated

def login_form():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:60px 0 40px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="color:white;">Sharp Screen</h1><p style="color:#9ca3af;">CV Screening & Analysis</p></div>""", unsafe_allow_html=True)
        password = st.text_input("Enter Access Password", type="password", key="pwd")
        if st.button("🚀 Access Sharp Suite", type="primary", use_container_width=True):
            if password == GOD_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.access_level = "god"
                st.rerun()
            elif password == DEMO_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.access_level = "demo"
                st.rerun()
            else: st.error("Invalid password")
        st.markdown('<p style="text-align:center;color:#6b7280;margin-top:24px;">Need access? <a href="mailto:sharpsuite@sharphuman.com" style="color:#6366f1;">sharpsuite@sharphuman.com</a></p>', unsafe_allow_html=True)

def apply_styles():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}h1,h2,h3{color:#fff!important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;border-radius:8px!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;border-radius:8px!important;}.output-box{background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:24px;margin:16px 0;}p,span,label{color:#e5e5e5!important;}[data-testid="stSidebar"]{background:#0a0a0f;}</style>""", unsafe_allow_html=True)

st.set_page_config(page_title="Sharp Screen | CV Screening", page_icon="🔍", layout="wide")

if not check_auth():
    login_form()
    st.stop()

apply_styles()

with st.sidebar:
    st.markdown(f"**{st.session_state.access_level.upper()}** access")
    if st.button("🚪 Logout"): st.session_state.authenticated = False; st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;font-size:1.8rem;color:white;">Sharp Screen</h1><p style="color:#9ca3af;margin:0;">CV Screening • Anonymization • GitHub Analysis</p></div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Screen & Rank", "👤 Blind Resume", "💻 GitHub"])

with tab1:
    st.markdown("### Screen candidates against JD")
    col1, col2 = st.columns(2)
    with col1:
        jd = st.text_area("📋 Job Description", height=200, placeholder="Paste JD here...")
    with col2:
        cvs = st.text_area("📄 CVs (separate with ---)", height=200, placeholder="CANDIDATE 1:\n...\n---\nCANDIDATE 2:\n...")
    
    c1, c2, c3 = st.columns(3)
    bias_free = c1.checkbox("🎯 Bias-free ranking", value=True)
    contacts = c2.checkbox("📞 Extract contacts", value=True)
    detailed = c3.checkbox("📊 Detailed analysis", value=False)
    
    if st.button("⚡ Screen Candidates", type="primary", use_container_width=True, key="screen"):
        if not jd or not cvs: st.error("Please provide JD and CVs")
        else:
            prompt = f"""Analyze candidates against JD.
JOB: {jd}
CANDIDATES: {cvs}
{"Ignore names, gender, age - focus on skills/experience only." if bias_free else ""}
For each: Rank, Match %, {"Contact info," if contacts else ""} Strengths, Concerns, Recommendation.
{"Detailed analysis." if detailed else ""} Start with ranking table."""
            with st.spinner("🔍 Analyzing..."):
                resp, _, _ = call_claude(prompt, 3000)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)
                st.download_button("📥 Download", resp, "screening.txt")

with tab2:
    st.markdown("### Anonymize resume")
    resume = st.text_area("Paste resume", height=300, placeholder="Full resume text...")
    company = st.text_input("Your company (for header)", placeholder="Sharp Human")
    
    if st.button("👤 Anonymize", type="primary", use_container_width=True, key="blind"):
        if resume:
            prompt = f"Anonymize this resume. Remove: name, email, phone, age, graduation years. Keep: skills, experience, achievements. {'Header: '+company if company else ''}\n\n{resume}"
            with st.spinner("👤 Anonymizing..."):
                resp, _, _ = call_claude(prompt, 2000)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("### Analyze GitHub profile")
    github = st.text_input("GitHub URL", placeholder="https://github.com/username")
    context = st.text_area("Context", height=80, placeholder="Role, skills to check...")
    
    if st.button("💻 Analyze", type="primary", use_container_width=True, key="github"):
        if github:
            user = github.rstrip('/').split('/')[-1]
            prompt = f"Analyze GitHub {github} for recruiting. Username: {user}. {'Context: '+context if context else ''}\nProvide: Level (Jr/Mid/Sr), Activity, Tech stack, Red flags, 3 interview questions."
            with st.spinner("💻 Analyzing..."):
                resp, _, _ = call_claude(prompt, 1500)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)

st.markdown('<a href="mailto:sharpsuite@sharphuman.com?subject=Feedback" style="position:fixed;bottom:20px;right:20px;background:#6366f1;color:white;padding:12px 20px;border-radius:30px;text-decoration:none;font-weight:600;">💬 Feedback</a>', unsafe_allow_html=True)
