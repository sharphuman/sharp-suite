"""Sharp Portal - Main Dashboard with Cross-App Auth"""
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
        render_sidebar,
        inject_ga4,
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
    COLORS = {"bg_dark": "#1a1a1a", "pink": "#db2777", "text_primary": "#ffffff", "text_muted": "#9ca3af", "border": "rgba(255,255,255,0.1)"}

# App info with rich descriptions
APPS = [
    {
        "key": "jd",
        "icon": "📝",
        "title": "JD Writer",
        "tagline": "Job descriptions that attract top talent",
        "description": """Turn a quick brief into a polished, bias-free job description in under 60 seconds. 
        Just tell us the role, seniority, and a few must-haves. Our AI crafts compelling copy that attracts 
        the right candidates while keeping your compliance team happy."""
    },
    {
        "key": "screen",
        "icon": "🔍",
        "title": "CV Screener",
        "tagline": "From hundreds of CVs to a shortlist you trust",
        "description": """Upload a stack of CVs and let AI do the heavy lifting. We score and rank every 
        candidate against your job requirements, flag potential concerns, and highlight the hidden gems 
        you might have missed."""
    },
    {
        "key": "interview",
        "icon": "🎯",
        "title": "Interview",
        "tagline": "Prep, evaluate, and coach with confidence",
        "description": """Walk into every interview feeling prepared. Generate role-specific questions, 
        evaluate candidates consistently with structured scorecards, and get AI-powered summaries after 
        each conversation."""
    },
    {
        "key": "outreach",
        "icon": "🚀",
        "title": "Outreach",
        "tagline": "Find candidates and start real conversations",
        "description": """Your complete sourcing and engagement toolkit. Build Boolean search strings 
        that actually work, craft personalized InMails that get replies, and create multi-touch sequences 
        that nurture passive candidates over time."""
    },
    {
        "key": "content",
        "icon": "✍️",
        "title": "Content",
        "tagline": "Build your employer brand without the writer's block",
        "description": """Generate LinkedIn posts, career page copy, job ads, recruitment marketing emails, 
        and thought leadership content. All in your company's voice, all without staring at a blank screen."""
    },
    {
        "key": "sales",
        "icon": "💰",
        "title": "Sales",
        "tagline": "Sharpen your BD and client skills",
        "description": """Analyze your sales calls with AI coaching. Get feedback on your pitch, objection 
        handling, and closing techniques. Works for both general sales and recruiting business development."""
    },
]


# ============================================
# AUTH FUNCTIONS
# ============================================

def supabase_sign_in(email, password):
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password},
            timeout=10
        )
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            user = data.get("user", {})
            return {"success": True, "user": user, "session_token": create_session(user.get("id"), email)}
        return {"success": False, "message": data.get("error_description") or "Invalid credentials"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def supabase_sign_up(email, password):
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password},
            timeout=10
        )
        data = r.json()
        if r.status_code == 200 and data.get("user"):
            return {"success": True, "message": "Check your email to confirm your account!"}
        return {"success": False, "message": data.get("error_description") or "Signup failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def supabase_magic_link(email):
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/magiclink",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email},
            timeout=10
        )
        if r.status_code == 200:
            return {"success": True, "message": "Magic link sent! Check your email."}
        return {"success": False, "message": "Failed to send magic link"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/sessions",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "user_id": user_id,
                "token": token,
                "ip_address": "unknown",
                "device_hash": "portal",
                "is_active": True,
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
            },
            timeout=10
        )
    except:
        pass
    return token


def validate_session_token(token):
    if not token:
        return None
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"},
            timeout=10
        )
        if r.status_code == 200 and r.json():
            session = r.json()[0]
            expires = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
            if expires.replace(tzinfo=None) > datetime.utcnow():
                user_r = requests.get(
                    f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}",
                    headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"},
                    timeout=10
                )
                if user_r.status_code == 200 and user_r.json():
                    profile = user_r.json()[0]
                    return {
                        "user_id": session["user_id"],
                        "email": profile.get("email"),
                        "plan": profile.get("plan", "free"),
                        "token": token
                    }
    except:
        pass
    return None


# ============================================
# SESSION MANAGEMENT
# ============================================

def init_session():
    defaults = [
        ('authenticated', False), ('user', None), ('session_token', ''),
        ('is_god', False), ('user_plan', 'free')
    ]
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
    if token:
        return f"{base_url}?token={token}"
    return base_url


# ============================================
# UI COMPONENTS
# ============================================

def render_auth():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    *, *::before, *::after { font-family: 'Nunito', sans-serif !important; }
    
    .stApp { 
        background: #1a1a1a;
        background-image: url('https://sharphuman.com/sharphuman_blue.png');
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        background-blend-mode: lighten;
    }
    
    [data-testid="stHeader"] { background: transparent !important; }
    h1, h2, h3, h4 { color: white !important; }
    p, span, label { color: #e5e5e5 !important; }
    .stTextInput > div > div > input { background: rgba(42, 42, 42, 0.8) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: white !important; border-radius: 8px !important; }
    .stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
    </style>""", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""
        <div style="text-align:center;padding:60px 0 30px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:100px;margin-bottom:20px;">
            <h1 style="margin:0;font-size:2.8rem;">Sharp Suite</h1>
            <p style="color:#9ca3af;font-size:1.2rem;">Your AI Recruiting Toolkit</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])
        
        with tab1:
            email = st.text_input("Email", key="l_email")
            pwd = st.text_input("Password", type="password", key="l_pwd")
            
            if st.button("Log In", use_container_width=True):
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
            
            st.markdown("---")
            st.markdown("**Or use magic link:**")
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
            
            if st.button("Create Account", use_container_width=True):
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


def render_dashboard():
    token = st.session_state.get("session_token", "")
    
    # Apply styles - REDUCED tile sizes by ~25%
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    *, *::before, *::after { font-family: 'Nunito', sans-serif !important; }
    
    .stApp { 
        background: #1a1a1a;
        background-image: url('https://sharphuman.com/sharphuman_blue.png');
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        background-blend-mode: lighten;
    }
    
    [data-testid="stHeader"] { background: transparent !important; }
    section[data-testid="stSidebar"] { background: rgba(26, 26, 26, 0.95) !important; border-right: 1px solid rgba(219, 39, 119, 0.3); backdrop-filter: blur(10px); }
    section[data-testid="stSidebar"] > div { background: transparent !important; }
    section[data-testid="stSidebar"] * { color: #e5e5e5 !important; }
    
    h1, h2, h3, h4 { color: white !important; }
    p, span, label { color: #e5e5e5 !important; }
    
    .app-tile {
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 16px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .app-tile:hover {
        border-color: rgba(59, 130, 246, 0.8);
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
    }
    
    .app-icon { font-size: 1.6rem; margin-bottom: 8px; }
    .app-title { font-size: 1.1rem; font-weight: 700; color: white !important; margin: 0 0 4px 0; }
    .app-tagline { font-size: 0.85rem; color: #60a5fa !important; margin: 0 0 10px 0; font-weight: 500; }
    .app-desc { font-size: 0.8rem; color: #b8b8b8 !important; line-height: 1.5; margin: 0 0 12px 0; }
    
    .app-button {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white !important;
        padding: 8px 18px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    .app-button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(99,102,241,0.4);
        color: white !important;
        text-decoration: none;
    }
    
    .welcome-section {
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .stLinkButton > a {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    </style>""", unsafe_allow_html=True)
    
    # Use shared_ui top banner if available
    if USING_SHARED:
        render_top_banner()
    
    # Header
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;padding:16px 0;border-bottom:1px solid rgba(59,130,246,0.3);margin-bottom:20px;">
        <img src="https://sharphuman.com/logo1-3.png" style="width:45px;">
        <div>
            <h1 style="margin:0;font-size:1.5rem;">Sharp Suite</h1>
            <p style="color:#9ca3af;margin:0;font-size:0.9rem;">Your AI Recruiting Toolkit</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome section
    user_name = get_user_email().split('@')[0].title() if '@' in get_user_email() else get_user_email()
    st.markdown(f"""
    <div class="welcome-section">
        <h2 style="margin:0 0 10px;font-size:1.3rem;">👋 Welcome back, {user_name}!</h2>
        <p style="margin:0;font-size:0.9rem;line-height:1.5;">
            Sharp Suite is your AI-powered recruiting command center. Whether you're writing job descriptions, 
            screening candidates, prepping for interviews, or crafting outreach that actually gets replies, 
            we've got the tools to help you work smarter. Pick an app below to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # App tiles - 3 columns
    for row_start in range(0, len(APPS), 3):
        cols = st.columns(3)
        for i, col in enumerate(cols):
            app_idx = row_start + i
            if app_idx < len(APPS):
                app = APPS[app_idx]
                url = build_app_url(app["key"])
                with col:
                    st.markdown(f"""
                    <div class="app-tile">
                        <div class="app-icon">{app["icon"]}</div>
                        <h3 class="app-title">{app["title"]}</h3>
                        <p class="app-tagline">{app["tagline"]}</p>
                        <p class="app-desc">{app["description"]}</p>
                        <a href="{url}" class="app-button">Open {app["title"]} →</a>
                    </div>
                    """, unsafe_allow_html=True)


# ============================================
# MAIN
# ============================================

st.set_page_config(page_title="Sharp Suite", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

# GA4
if USING_SHARED:
    inject_ga4()

init_session()
check_url_auth()

if not st.session_state.authenticated:
    render_auth()
else:
    # Use shared_ui sidebar
    if USING_SHARED:
        render_sidebar(
            current_app="portal",
            user_email=get_user_email(),
            user_plan=st.session_state.get("user_plan", "free"),
            session_token=st.session_state.get("session_token", "")
        )
    else:
        # Fallback sidebar
        with st.sidebar:
            st.markdown(f"**Logged in as:** {get_user_email()}")
            st.markdown(f"**Plan:** {st.session_state.get('user_plan', 'free')}")
            st.markdown("---")
            st.markdown("**Apps**")
            for app in APPS:
                st.link_button(f"{app['icon']} {app['title']}", build_app_url(app["key"]), use_container_width=True)
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
    
    render_dashboard()
