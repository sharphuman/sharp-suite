"""
Sharp Portal - Main Dashboard
STANDALONE VERSION
"""
import streamlit as st

GOD_PASSWORD = "G0DHum@n101!!!"
DEMO_PASSWORD = "D3M0Human101!!!"

def check_auth():
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False; st.session_state.access_level = None
    return st.session_state.authenticated

def login_form():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:60px 0 40px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="color:white;">Sharp Suite</h1><p style="color:#9ca3af;">AI-Powered Recruiting Tools</p></div>""", unsafe_allow_html=True)
        password = st.text_input("Enter Access Password", type="password", key="pwd")
        if st.button("🚀 Access Sharp Suite", type="primary", use_container_width=True):
            if password == GOD_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "god"; st.rerun()
            elif password == DEMO_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "demo"; st.rerun()
            else: st.error("Invalid password")
        st.markdown('<p style="text-align:center;color:#6b7280;margin-top:24px;">Need access? <a href="mailto:sharpsuite@sharphuman.com" style="color:#6366f1;">sharpsuite@sharphuman.com</a></p>', unsafe_allow_html=True)

def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    * { font-family: 'Nunito', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%); }
    h1, h2, h3 { color: #ffffff !important; }
    [data-testid="stSidebar"] { background: #0a0a0f; }
    .app-card { background: linear-gradient(135deg, #12121a, #1a1a2e); border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 24px; height: 180px; transition: all 0.3s; text-decoration: none !important; display: block; }
    .app-card:hover { transform: translateY(-4px); border-color: #6366f1; box-shadow: 0 12px 40px rgba(99,102,241,0.2); }
    .app-icon { font-size: 2.2rem; margin-bottom: 10px; }
    .app-title { font-size: 1.1rem; font-weight: 700; color: white !important; margin-bottom: 6px; }
    .app-desc { font-size: 0.85rem; color: #9ca3af !important; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Sharp Suite", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

if not check_auth(): login_form(); st.stop()

apply_styles()

with st.sidebar:
    st.markdown(f"**{st.session_state.access_level.upper()}** access")
    if st.button("🚪 Logout"): st.session_state.authenticated = False; st.rerun()

st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;color:white;">Sharp Suite</h1><p style="color:#6b7280;margin:0;">{st.session_state.access_level.upper()} ACCESS</p></div></div>""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""<div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border:1px solid rgba(99,102,241,0.2);border-radius:16px;padding:32px;margin-bottom:32px;text-align:center;"><h2 style="margin:0 0 12px;color:white;">Welcome to Sharp Suite 🚀</h2><p style="color:#9ca3af;margin:0;">Your AI-powered recruiting toolkit. Select an app below.</p></div>""", unsafe_allow_html=True)

APPS = [
    ("📝", "Sharp JD", "AI job descriptions", "https://jd.sharphuman.com"),
    ("🔍", "Sharp Screen", "CV screening & ranking", "https://screen.sharphuman.com"),
    ("🎯", "Sharp Interview", "Questions & analysis", "https://hire.sharphuman.com"),
    ("🎣", "Sharp Source", "Boolean & outreach", "https://outreach.sharphuman.com"),
    ("✍️", "Sharp Content", "Content engine", "https://content.sharphuman.com"),
    ("💰", "Sharp Sales", "Sales analysis", "https://sales.sharphuman.com"),
    ("🚀", "Sharp Reach", "BD & leads", "https://reach.sharphuman.com"),
    ("🤖", "Sharp Assistant", "AI partner", "https://assistant.sharphuman.com"),
]

st.markdown("### 🛠️ Your Apps")

cols = st.columns(4)
for i, (icon, name, desc, url) in enumerate(APPS):
    with cols[i % 4]:
        st.markdown(f'<a href="{url}" target="_blank" class="app-card"><div class="app-icon">{icon}</div><div class="app-title">{name}</div><div class="app-desc">{desc}</div></a>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.access_level == "god":
    st.markdown("---")
    st.markdown("### ⚙️ Admin")
    st.markdown('<a href="https://admin.sharphuman.com" target="_blank" class="app-card" style="max-width:300px;border-color:rgba(239,68,68,0.3);"><div class="app-icon">⚙️</div><div class="app-title">Sharp Admin</div><div class="app-desc">Users, broadcasts, analytics</div></a>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center;padding:20px;color:#6b7280;">© 2024 Sharp Human • <a href="https://sharphuman.com" style="color:#6366f1;">sharphuman.com</a></div>', unsafe_allow_html=True)
