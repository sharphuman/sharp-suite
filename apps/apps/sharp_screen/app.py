"""Sharp Screen - CV Screening with Supabase Auth"""
import streamlit as st
import requests
import os

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"): return {"success": True, "user": data.get("user")}
        return {"success": False, "message": data.get("error_description") or "Invalid credentials"}
    except Exception as e: return {"success": False, "message": str(e)}

def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("user"): return {"success": True, "message": "Check email to confirm!"}
        return {"success": False, "message": data.get("error_description") or "Failed"}
    except Exception as e: return {"success": False, "message": str(e)}

def supabase_magic_link(email):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email}, timeout=10)
        return {"success": r.status_code == 200, "message": "Magic link sent!" if r.status_code == 200 else "Failed"}
    except Exception as e: return {"success": False, "message": str(e)}

def init_session():
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False
    if 'user' not in st.session_state: st.session_state.user = None
    if 'is_god' not in st.session_state: st.session_state.is_god = False

def get_user_email():
    if st.session_state.user: return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"

def call_claude(prompt, max_tokens=3000):
    if not ANTHROPIC_API_KEY: return "Error: ANTHROPIC_API_KEY not set"
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200: return r.json()["content"][0]["text"]
        return f"Error: {r.status_code}"
    except Exception as e: return f"Error: {str(e)}"

def render_auth():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}.stTextInput>div>div>input{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}.stTabs [data-baseweb="tab-list"]{background:#12121a;}.stTabs [aria-selected="true"]{background:rgba(99,102,241,0.3)!important;color:white!important;}</style>""", unsafe_allow_html=True)
    col1,col2,col3 = st.columns([1,1.3,1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:40px 0;"><img src="https://sharphuman.com/logo1-3.png" style="width:70px;margin-bottom:16px;"><h1 style="color:white;">Sharp Screen</h1><p style="color:#9ca3af;">CV Screening & Analysis</p></div>""", unsafe_allow_html=True)
        tab1,tab2 = st.tabs(["🔐 Log In","✨ Sign Up"])
        with tab1:
            e,p = st.text_input("Email",key="le"), st.text_input("Password",type="password",key="lp")
            if st.button("Log In",use_container_width=True):
                if p == GOD_PASSWORD: st.session_state.authenticated=True;st.session_state.is_god=True;st.session_state.user={"email":"GOD"};st.rerun()
                elif e and p:
                    r=supabase_sign_in(e,p)
                    if r["success"]: st.session_state.authenticated=True;st.session_state.user=r["user"];st.rerun()
                    else: st.error(r["message"])
            st.markdown("<p style='text-align:center;color:#6b7280;'>— or —</p>",unsafe_allow_html=True)
            me=st.text_input("Magic link",key="me",label_visibility="collapsed",placeholder="Email")
            if st.button("✨ Magic Link",use_container_width=True,key="ml"):
                if me: r=supabase_magic_link(me);st.success(r["message"]) if r["success"] else st.error(r["message"])
        with tab2:
            se,sp,sc = st.text_input("Email",key="se"),st.text_input("Password",type="password",key="sp"),st.text_input("Confirm",type="password",key="sc")
            if st.button("Create Account",use_container_width=True):
                if sp!=sc: st.error("Passwords don't match")
                elif len(sp)<6: st.warning("6+ chars")
                elif se and sp: r=supabase_sign_up(se,sp);st.success(r["message"]) if r["success"] else st.error(r["message"])

st.set_page_config(page_title="Sharp Screen",page_icon="🔍",layout="wide")
init_session()
if not st.session_state.authenticated: render_auth();st.stop()

st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}h1,h2,h3{color:white!important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}.output-box{background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:24px;margin:16px 0;}p,span,label{color:#e5e5e5!important;}</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<div style='padding:12px;background:rgba(99,102,241,0.1);border-radius:8px;'><p style='color:#9ca3af;margin:0;font-size:0.75rem;'>Logged in</p><p style='color:white;margin:0;'>{get_user_email()}</p></div>",unsafe_allow_html=True)
    if st.button("🚪 Logout",use_container_width=True): st.session_state.authenticated=False;st.session_state.user=None;st.session_state.is_god=False;st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;">Sharp Screen</h1><p style="color:#9ca3af;margin:0;">CV Screening • Anonymization • GitHub</p></div></div>""", unsafe_allow_html=True)

tab1,tab2,tab3 = st.tabs(["🔍 Screen","👤 Blind Resume","💻 GitHub"])

with tab1:
    c1,c2 = st.columns(2)
    jd = c1.text_area("📋 Job Description",height=200)
    cvs = c2.text_area("📄 CVs (--- separated)",height=200)
    bias = st.checkbox("Bias-free",value=True)
    if st.button("⚡ Screen",type="primary",use_container_width=True):
        if jd and cvs:
            prompt = f"Analyze candidates vs JD.\nJD:{jd}\nCVs:{cvs}\n{'Ignore names/gender.' if bias else ''}\nRank, score, strengths, concerns."
            with st.spinner("🔍..."): st.markdown(f'<div class="output-box">{call_claude(prompt)}</div>',unsafe_allow_html=True)

with tab2:
    resume = st.text_area("Resume",height=250)
    if st.button("👤 Anonymize",type="primary",use_container_width=True):
        if resume:
            with st.spinner("👤..."): st.markdown(f'<div class="output-box">{call_claude(f"Anonymize: remove name,email,phone,age. Keep skills,experience.\n{resume}")}</div>',unsafe_allow_html=True)

with tab3:
    gh = st.text_input("GitHub URL")
    if st.button("💻 Analyze",type="primary",use_container_width=True):
        if gh:
            with st.spinner("💻..."): st.markdown(f'<div class="output-box">{call_claude(f"Analyze GitHub {gh} for recruiting: level, activity, stack, red flags.")}</div>',unsafe_allow_html=True)
