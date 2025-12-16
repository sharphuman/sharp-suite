"""Sharp Portal - Main Dashboard (STRIPPED - Pure Streamlit)"""
import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import secrets
import sys

# Add parent directory for shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# ============================================
# SHARED MODULE IMPORTS
# ============================================
try:
    from shared_config import (
        SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY,
        GOD_PASSWORD, APP_URLS
    )
    from shared_ui import (
        apply_global_styles,
        render_top_banner,
        render_app_header,
        render_sidebar,
        COLORS
    )
    USING_SHARED = True
except ImportError:
    USING_SHARED = False
    SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
    GOD_PASSWORD = os.environ.get("GOD_PASSWORD", "G0DHum@n101!!!")
    APP_URLS = {
        "portal": "https://demo.sharphuman.com",
        "jd": "https://jd.sharphuman.com",
        "screen": "https://screen.sharphuman.com",
        "interview": "https://interview.sharphuman.com",
        "outreach": "https://outreach.sharphuman.com",
        "content": "https://content.sharphuman.com",
        "sales": "https://sales.sharphuman.com",
        "admin": "https://admin.sharphuman.com",
    }
    COLORS = {"primary": "#ff4b4b", "success": "#21c354", "warning": "#faca2b", "error": "#ff4b4b"}
    
    # Fallback UI functions
    def apply_global_styles():
        pass
    
    def render_top_banner(**kwargs):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.link_button("🔧 Services", "https://sharphuman.com#services")
        with col2:
            st.link_button("📝 Blog", "https://sharphuman.com/blog")
        with col3:
            st.link_button("📅 Book Demo", "https://calendly.com/sharphuman/30min")
        with col4:
            st.link_button("🌐 sharphuman.com", "https://sharphuman.com")
        st.divider()
    
    def render_app_header(title, subtitle=""):
        st.title(title)
        if subtitle:
            st.caption(subtitle)
        st.divider()
    
    def render_sidebar(current_app, user_email="", user_plan="free", session_token=""):
        with st.sidebar:
            st.title("Sharp Suite")
            st.write(f"**{user_email}**")
            st.caption(f"{user_plan.upper()} Plan")
            st.divider()
            apps = [("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"), 
                    ("interview", "🎯 Interview"), ("outreach", "🚀 Outreach"), 
                    ("content", "✍️ Content"), ("sales", "💰 Sales")]
            for key, label in apps:
                if key == current_app:
                    st.success(f"**{label}** ◀")
                else:
                    url = f"{APP_URLS.get(key, '')}?token={session_token}" if session_token else APP_URLS.get(key, "")
                    st.link_button(label, url, use_container_width=True)
            st.divider()
            if st.button("🚪 Logout", use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()


# App info
APPS = [
    {"key": "jd", "icon": "📝", "title": "JD Writer", "tagline": "Job descriptions that attract top talent",
     "description": "Turn a quick brief into a polished, bias-free job description in under 60 seconds."},
    {"key": "screen", "icon": "🔍", "title": "CV Screener", "tagline": "From hundreds of CVs to a shortlist you trust",
     "description": "Upload CVs and let AI score and rank candidates against your requirements."},
    {"key": "interview", "icon": "🎯", "title": "Interview", "tagline": "Prep, evaluate, and coach with confidence",
     "description": "Generate questions, evaluate candidates with scorecards, and get AI summaries."},
    {"key": "outreach", "icon": "🚀", "title": "Outreach", "tagline": "Find candidates and start real conversations",
     "description": "Build Boolean searches, craft personalized InMails, and create sequences."},
    {"key": "content", "icon": "✍️", "title": "Content", "tagline": "Build your employer brand without writer's block",
     "description": "Generate LinkedIn posts, career page copy, job ads, and marketing content."},
    {"key": "sales", "icon": "💰", "title": "Sales", "tagline": "Sharpen your BD and client skills",
     "description": "Analyze sales calls with AI coaching on pitch, objection handling, and closing."},
]


# ============================================
# AUTH FUNCTIONS
# ============================================

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", 
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "portal",
                  "is_active": True, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()},
            timeout=10)
    except:
        pass
    return token


def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            user = data.get("user", {})
            return {"success": True, "user": user, "session_token": create_session(user.get("id"), email)}
        return {"success": False, "message": data.get("error_description") or "Invalid credentials"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("user"):
            return {"success": True, "message": "Check your email to confirm!"}
        return {"success": False, "message": data.get("error_description") or "Sign up failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def supabase_magic_link(email):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email}, timeout=10)
        if r.status_code == 200:
            return {"success": True, "message": "Check your email for the magic link!"}
        return {"success": False, "message": "Failed to send magic link"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def validate_session_token(token):
    if not token:
        return None
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        if r.status_code == 200 and r.json():
            session = r.json()[0]
            expires = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
            if expires.replace(tzinfo=None) > datetime.utcnow():
                user_r = requests.get(f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}",
                    headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
                if user_r.status_code == 200 and user_r.json():
                    profile = user_r.json()[0]
                    return {"user_id": session["user_id"], "email": profile.get("email"), 
                            "plan": profile.get("plan", "free"), "token": token}
    except:
        pass
    return None


# ============================================
# SESSION MANAGEMENT
# ============================================

def init_session():
    defaults = [('authenticated', False), ('user', None), ('session_token', ''),
                ('is_god', False), ('user_plan', 'free')]
    for k, v in defaults:
        if k not in st.session_state:
            st.session_state[k] = v


def check_url_auth():
    if st.session_state.authenticated:
        return
    token = st.query_params.get("token") or st.query_params.get("auth")
    if token:
        user_info = validate_session_token(token)
        if user_info:
            st.session_state.authenticated = True
            st.session_state.user = {"email": user_info["email"], "id": user_info["user_id"]}
            st.session_state.session_token = token
            st.session_state.user_plan = user_info.get("plan", "free")
            st.session_state.is_god = user_info.get("plan") == "god"


def get_user_email():
    if st.session_state.user:
        return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"


def build_app_url(app_key):
    base_url = APP_URLS.get(app_key, f"https://{app_key}.sharphuman.com")
    token = st.session_state.get("session_token", "")
    return f"{base_url}?token={token}" if token else base_url


# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp Suite", page_icon="🚀", layout="wide")
init_session()
check_url_auth()

# Apply styles
apply_global_styles()

# Auth screen
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚀 Sharp Suite")
        st.caption("Your AI Recruiting Toolkit")
        st.divider()
        
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])
        
        with tab1:
            email = st.text_input("Email", key="l_email")
            pwd = st.text_input("Password", type="password", key="l_pwd")
            
            if st.button("Log In", use_container_width=True, type="primary"):
                if pwd == GOD_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_god = True
                    st.session_state.user = {"email": "GOD", "id": "god"}
                    st.session_state.session_token = secrets.token_urlsafe(32)
                    st.rerun()
                elif email and pwd:
                    r = supabase_sign_in(email, pwd)
                    if r["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = r["user"]
                        st.session_state.session_token = r.get("session_token")
                        st.rerun()
                    else:
                        st.error(r["message"])
            
            st.divider()
            st.write("**Or use magic link:**")
            magic_email = st.text_input("Email for magic link", key="m_email", label_visibility="collapsed", placeholder="Enter your email")
            if st.button("✨ Send Magic Link", use_container_width=True):
                if magic_email:
                    r = supabase_magic_link(magic_email)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
        
        with tab2:
            s_email = st.text_input("Email", key="s_email")
            s_pwd = st.text_input("Password", type="password", key="s_pwd")
            s_conf = st.text_input("Confirm Password", type="password", key="s_conf")
            
            if st.button("Create Account", use_container_width=True, type="primary"):
                if s_pwd != s_conf:
                    st.error("Passwords don't match")
                elif len(s_pwd) < 6:
                    st.warning("Password must be at least 6 characters")
                elif s_email and s_pwd:
                    r = supabase_sign_up(s_email, s_pwd)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
    st.stop()

# Authenticated - show dashboard
render_top_banner()
render_sidebar(
    current_app="portal",
    user_email=get_user_email(),
    user_plan=st.session_state.get('user_plan', 'free'),
    session_token=st.session_state.get('session_token', '')
)

# Header
render_app_header("Sharp Suite", "Your AI Recruiting Toolkit")

# Welcome message
user_name = get_user_email().split('@')[0].title() if '@' in get_user_email() else get_user_email()
st.success(f"👋 Welcome back, {user_name}!")
st.write("Sharp Suite is your AI-powered recruiting command center. Pick an app below to get started.")

st.divider()

# App tiles in grid
for i in range(0, len(APPS), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j < len(APPS):
            app = APPS[i + j]
            with col:
                with st.container(border=True):
                    st.subheader(f"{app['icon']} {app['title']}")
                    st.caption(app['tagline'])
                    st.write(app['description'])
                    st.link_button(f"Open {app['title']} →", build_app_url(app['key']), use_container_width=True)
