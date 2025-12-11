"""
Sharp Portal - Main Dashboard
With Supabase Auth (Email/Password + Magic Link + GOD)
"""
import streamlit as st
import requests

# ============== CONFIG ==============
SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"

# ============== AUTH FUNCTIONS ==============
def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("user"):
            return {"success": True, "message": "Check your email to confirm your account!"}
        return {"success": False, "message": data.get("error_description") or data.get("msg") or "Sign up failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            return {"success": True, "user": data.get("user"), "access_token": data.get("access_token")}
        return {"success": False, "message": data.get("error_description") or "Invalid credentials"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def supabase_magic_link(email):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email}, timeout=10)
        if r.status_code == 200:
            return {"success": True, "message": "Magic link sent! Check your email."}
        return {"success": False, "message": "Failed to send magic link"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def init_session():
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False
    if 'user' not in st.session_state: st.session_state.user = None
    if 'is_god' not in st.session_state: st.session_state.is_god = False

def get_user_email():
    if st.session_state.user: return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.is_god = False

# ============== AUTH PAGE ==============
def render_auth_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%); }
    * { font-family: 'Nunito', sans-serif !important; }
    .stTextInput > div > div > input { background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; border-radius: 8px !important; }
    .stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; background: #12121a; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { background: transparent !important; color: #9ca3af !important; border-radius: 6px !important; }
    .stTabs [aria-selected="true"] { background: rgba(99,102,241,0.3) !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding:40px 0 30px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:70px; margin-bottom:16px;">
            <h1 style="color:white; margin:0 0 8px; font-size:1.8rem;">Sharp Suite</h1>
            <p style="color:#9ca3af; margin:0;">AI-Powered Recruiting Tools</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        
        with tab1:
            login_email = st.text_input("Email", placeholder="you@company.com", key="le")
            login_password = st.text_input("Password", type="password", key="lp")
            
            if st.button("Log In", use_container_width=True, key="bl"):
                if login_email and login_password:
                    if login_password == GOD_PASSWORD:
                        st.session_state.authenticated = True
                        st.session_state.is_god = True
                        st.session_state.user = {"email": "GOD"}
                        st.rerun()
                    else:
                        result = supabase_sign_in(login_email, login_password)
                        if result["success"]:
                            st.session_state.authenticated = True
                            st.session_state.user = result["user"]
                            st.rerun()
                        else:
                            st.error(result["message"])
            
            st.markdown("<p style='text-align:center; color:#6b7280; margin:16px 0;'>— or —</p>", unsafe_allow_html=True)
            magic_email = st.text_input("Email for magic link", placeholder="you@company.com", key="me", label_visibility="collapsed")
            if st.button("✨ Send Magic Link", use_container_width=True, key="bm"):
                if magic_email:
                    result = supabase_magic_link(magic_email)
                    if result["success"]: st.success(result["message"])
                    else: st.error(result["message"])
        
        with tab2:
            signup_email = st.text_input("Email", placeholder="you@company.com", key="se")
            signup_password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="sp")
            signup_confirm = st.text_input("Confirm Password", type="password", key="sc")
            
            if st.button("Create Account", use_container_width=True, key="bs"):
                if signup_password != signup_confirm:
                    st.error("Passwords don't match")
                elif len(signup_password) < 6:
                    st.warning("Password must be 6+ characters")
                elif signup_email and signup_password:
                    result = supabase_sign_up(signup_email, signup_password)
                    if result["success"]: st.success(result["message"])
                    else: st.error(result["message"])
        
        st.markdown("<p style='text-align:center; color:#6b7280; margin-top:20px; font-size:0.8rem;'>Need help? <a href='mailto:sharpsuite@sharphuman.com' style='color:#6366f1;'>sharpsuite@sharphuman.com</a></p>", unsafe_allow_html=True)

# ============== MAIN APP ==============
st.set_page_config(page_title="Sharp Suite", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")
init_session()

if not st.session_state.authenticated:
    render_auth_page()
    st.stop()

# ============== DASHBOARD ==============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%); }
h1, h2, h3 { color: #ffffff !important; }
.app-card { background: linear-gradient(135deg, #12121a, #1a1a2e); border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 24px; height: 160px; transition: all 0.3s; text-decoration: none !important; display: block; }
.app-card:hover { transform: translateY(-4px); border-color: #6366f1; box-shadow: 0 12px 40px rgba(99,102,241,0.2); }
.app-icon { font-size: 2rem; margin-bottom: 8px; }
.app-title { font-size: 1rem; font-weight: 700; color: white !important; margin-bottom: 4px; }
.app-desc { font-size: 0.8rem; color: #9ca3af !important; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="padding:12px; background:rgba(99,102,241,0.1); border-radius:8px; margin-bottom:16px;">
        <p style="color:#9ca3af; margin:0; font-size:0.75rem;">Logged in as</p>
        <p style="color:white; margin:0; font-weight:600;">{get_user_email()}</p>
        {"<span style='color:#f59e0b; font-size:0.7rem;'>👑 GOD MODE</span>" if st.session_state.is_god else ""}
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

# Header
st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between; padding:20px 0;">
    <div style="display:flex; align-items:center; gap:12px;">
        <img src="https://sharphuman.com/logo1-3.png" style="width:45px;">
        <div>
            <h1 style="margin:0; font-size:1.6rem; color:white;">Sharp Suite</h1>
            <p style="color:#6b7280; margin:0; font-size:0.8rem;">Welcome, {get_user_email()}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Welcome banner
st.markdown("""
<div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1)); border:1px solid rgba(99,102,241,0.2); border-radius:16px; padding:28px; margin-bottom:28px; text-align:center;">
    <h2 style="margin:0 0 8px; color:white; font-size:1.4rem;">Welcome to Sharp Suite 🚀</h2>
    <p style="color:#9ca3af; margin:0;">Your AI-powered recruiting toolkit</p>
</div>
""", unsafe_allow_html=True)

# Apps grid
APPS = [
    ("📝", "Sharp JD", "AI job descriptions", "https://jd.sharphuman.com"),
    ("🔍", "Sharp Screen", "CV screening", "https://screen.sharphuman.com"),
    ("🎯", "Sharp Interview", "Questions & analysis", "https://hire.sharphuman.com"),
    ("🎣", "Sharp Source", "Boolean & outreach", "https://outreach.sharphuman.com"),
    ("✍️", "Sharp Content", "Content engine", "https://content.sharphuman.com"),
    ("💰", "Sharp Sales", "Sales analysis", "https://sales.sharphuman.com"),
    ("🚀", "Sharp Reach", "BD & leads", "https://reach.sharphuman.com"),
    ("🤖", "Sharp Assistant", "AI chat partner", "https://assistant.sharphuman.com"),
]

st.markdown("### 🛠️ Your Apps")
cols = st.columns(4)
for i, (icon, name, desc, url) in enumerate(APPS):
    with cols[i % 4]:
        st.markdown(f'<a href="{url}" target="_blank" class="app-card"><div class="app-icon">{icon}</div><div class="app-title">{name}</div><div class="app-desc">{desc}</div></a>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

# Admin section for GOD
if st.session_state.is_god:
    st.markdown("---")
    st.markdown("### ⚙️ Admin")
    st.markdown('<a href="https://admin.sharphuman.com" target="_blank" class="app-card" style="max-width:280px; border-color:rgba(239,68,68,0.3);"><div class="app-icon">⚙️</div><div class="app-title">Sharp Admin</div><div class="app-desc">Users & analytics</div></a>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p style="text-align:center; color:#6b7280; font-size:0.8rem;">© 2024 Sharp Human • <a href="https://sharphuman.com" style="color:#6366f1;">sharphuman.com</a></p>', unsafe_allow_html=True)
