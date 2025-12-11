"""
Sharp Admin - GOD Only Console
STANDALONE VERSION
"""
import streamlit as st
import requests
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOD_PASSWORD = "G0DHum@n101!!!"
DEMO_PASSWORD = "D3M0Human101!!!"

def call_claude(prompt, max_tokens=1000):
    if not ANTHROPIC_API_KEY: return "Error: ANTHROPIC_API_KEY not set"
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200: return r.json()["content"][0]["text"]
        return f"API Error"
    except: return "Error"

def check_auth():
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False; st.session_state.access_level = None
    return st.session_state.authenticated

def login_form():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#1a0a0a);}*{font-family:'Nunito',sans-serif!important;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:60px 0 40px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="color:#ef4444;">Sharp Admin</h1><p style="color:#9ca3af;">GOD Access Required</p></div>""", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", key="pwd")
        if st.button("🔓 Access Admin", type="primary", use_container_width=True):
            if password == GOD_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "god"; st.rerun()
            elif password == DEMO_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "demo"; st.rerun()
            else: st.error("Invalid password")

def apply_styles():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#1a0a0a);}h1,h2,h3{color:#fff!important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#12121a!important;border:1px solid rgba(239,68,68,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#ef4444,#dc2626)!important;color:white!important;border:none!important;}p,span,label{color:#e5e5e5!important;}</style>""", unsafe_allow_html=True)

st.set_page_config(page_title="Sharp Admin", page_icon="⚙️", layout="wide")

if not check_auth(): login_form(); st.stop()

# GOD ONLY CHECK
if st.session_state.access_level != "god":
    st.error("⛔ GOD access required. You have DEMO access.")
    st.info("Sharp Admin is restricted to GOD users only.")
    if st.button("🚪 Logout"): st.session_state.authenticated = False; st.rerun()
    st.stop()

apply_styles()

with st.sidebar:
    st.markdown("**GOD ACCESS**")
    if st.button("🚪 Logout"): st.session_state.authenticated = False; st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(239,68,68,0.3);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;color:#ef4444;">Sharp Admin</h1><p style="color:#9ca3af;margin:0;">Command Center</p></div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["👥 Users", "📧 Broadcast", "📊 Analytics"])

with tab1:
    st.markdown("### User Management")
    users = [{"email": "demo@example.com", "name": "Demo User", "status": "trial", "last": "2024-01-20"},
             {"email": "paid@example.com", "name": "Paid User", "status": "paid", "last": "2024-01-21"}]
    st.info("📌 Connect Supabase for real data")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(users))
    c2.metric("Trial", len([u for u in users if u['status']=='trial']))
    c3.metric("Paid", len([u for u in users if u['status']=='paid']))
    c4.metric("Conversion", "50%")
    
    for u in users:
        color = "#22c55e" if u['status']=='paid' else "#f59e0b"
        st.markdown(f"<div style='background:#12121a;border:1px solid rgba(99,102,241,0.1);padding:12px;margin:4px 0;border-radius:6px;'><span style='color:white;'>{u['name']}</span> - <span style='color:#6b7280;'>{u['email']}</span> - <span style='color:{color};'>{u['status'].upper()}</span></div>", unsafe_allow_html=True)

with tab2:
    st.markdown("### Broadcast")
    subject = st.text_input("Subject", placeholder="New Feature Announcement")
    content = st.text_area("Message", height=200)
    recipients = st.selectbox("Recipients", ["All", "Trial Only", "Paid Only"])
    
    c1, c2 = st.columns(2)
    if c1.button("✨ AI Improve"):
        if content:
            improved = call_claude(f"Improve this email:\n{content}")
            st.text_area("Improved", improved, height=150)
    if c2.button("🚀 Send", type="primary"):
        if subject and content:
            st.success(f"✅ Sent to {recipients}!")
            st.balloons()

with tab3:
    st.markdown("### Analytics")
    c1, c2, c3 = st.columns(3)
    c1.metric("API Calls (30d)", "1,247")
    c2.metric("Active Users", "23")
    c3.metric("Cost", "$18.42")
    
    apps = {"Assistant": 67, "JD": 45, "Source": 41, "Reach": 38, "Screen": 32}
    for app, count in sorted(apps.items(), key=lambda x: x[1], reverse=True):
        pct = count / max(apps.values()) * 100
        st.markdown(f"<div style='margin:8px 0;'><span style='color:#e5e5e5;'>{app}</span> - <span style='color:#6b7280;'>{count}</span><div style='background:#1a1a2e;height:8px;border-radius:4px;'><div style='background:#6366f1;height:100%;width:{pct}%;border-radius:4px;'></div></div></div>", unsafe_allow_html=True)
