"""
Sharp Interview - Questions & Analysis
STANDALONE VERSION
"""
import streamlit as st
import requests
import os

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
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False; st.session_state.access_level = None
    return st.session_state.authenticated

def login_form():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:60px 0 40px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="color:white;">Sharp Interview</h1><p style="color:#9ca3af;">Interview Prep & Analysis</p></div>""", unsafe_allow_html=True)
        password = st.text_input("Enter Access Password", type="password", key="pwd")
        if st.button("🚀 Access", type="primary", use_container_width=True):
            if password == GOD_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "god"; st.rerun()
            elif password == DEMO_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "demo"; st.rerun()
            else: st.error("Invalid password")

def apply_styles():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}h1,h2,h3{color:#fff!important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}.output-box{background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:24px;margin:16px 0;}p,span,label{color:#e5e5e5!important;}</style>""", unsafe_allow_html=True)

st.set_page_config(page_title="Sharp Interview", page_icon="🎯", layout="wide")

if not check_auth(): login_form(); st.stop()

apply_styles()

with st.sidebar:
    st.markdown(f"**{st.session_state.access_level.upper()}**")
    if st.button("🚪 Logout"): st.session_state.authenticated = False; st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;color:white;">Sharp Interview</h1><p style="color:#9ca3af;margin:0;">Questions • Analysis • Scorecards</p></div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["❓ Questions", "📝 Analyze", "📋 Scorecard"])

with tab1:
    st.markdown("### Generate interview questions")
    col1, col2 = st.columns([2, 1])
    with col1:
        title = st.text_input("Job Title", placeholder="Senior Software Engineer")
        jd = st.text_area("JD / Requirements", height=150)
        bg = st.text_area("Candidate Background", height=100)
    with col2:
        stage = st.selectbox("Stage", ["Phone Screen", "Technical", "Hiring Manager", "Culture Fit", "Final"])
        duration = st.select_slider("Duration", ["15 min", "30 min", "45 min", "60 min"], value="45 min")
        tech = st.checkbox("Technical", value=True)
        behav = st.checkbox("Behavioral", value=True)
    
    if st.button("⚡ Generate Questions", type="primary", use_container_width=True, key="q"):
        if title:
            focus = []
            if tech: focus.append("technical")
            if behav: focus.append("behavioral/STAR")
            prompt = f"Generate interview questions: {title}, {stage}, {duration}, focus: {', '.join(focus)}. JD: {jd or 'N/A'}. Candidate: {bg or 'N/A'}. Include opening, 10 core questions with what to look for, closing, red flags."
            with st.spinner("⚡ Generating..."):
                resp, _, _ = call_claude(prompt, 2500)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("### Analyze transcript")
    transcript = st.text_area("Paste transcript", height=300, placeholder="INTERVIEWER: ...\nCANDIDATE: ...")
    role = st.text_input("Role", placeholder="Product Manager")
    
    if st.button("🔍 Analyze", type="primary", use_container_width=True, key="a"):
        if transcript:
            prompt = f"Analyze interview for {role or 'this role'}:\n{transcript}\n\nProvide: Overall assessment, Green flags, Red flags, Strengths, Concerns, Follow-up questions, Final recommendation."
            with st.spinner("🔍 Analyzing..."):
                resp, _, _ = call_claude(prompt, 2500)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("### Generate scorecard")
    role = st.text_input("Role", placeholder="Engineer", key="sr")
    comp = st.text_area("Competencies", placeholder="Technical\nCommunication\nProblem solving", height=100)
    fmt = st.radio("Format", ["Simple 1-5", "Detailed rubric", "Google 1-4"])
    
    if st.button("📋 Generate", type="primary", use_container_width=True, key="s"):
        if role:
            prompt = f"Create interview scorecard: {role}, competencies: {comp or 'Technical, Communication, Problem solving, Culture fit'}, format: {fmt}. Include header, scoring, overall recommendation."
            with st.spinner("📋..."):
                resp, _, _ = call_claude(prompt, 2000)
                st.markdown(f'<div class="output-box"><pre>{resp}</pre></div>', unsafe_allow_html=True)

st.markdown('<a href="mailto:sharpsuite@sharphuman.com?subject=Feedback" style="position:fixed;bottom:20px;right:20px;background:#6366f1;color:white;padding:12px 20px;border-radius:30px;text-decoration:none;">💬 Feedback</a>', unsafe_allow_html=True)
