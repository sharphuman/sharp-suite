"""Sharp Portal - Main Dashboard with Cross-App Auth"""
import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import secrets

# ============================================
# CONFIGURATION
# ============================================

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# App URLs for navigation
APP_URLS = {
    "portal": "https://demo.sharphuman.com",
    "jd": "https://jd.sharphuman.com",
    "screen": "https://screen.sharphuman.com",
    "interview": "https://hire.sharphuman.com",
    "source": "https://outreach.sharphuman.com",
    "content": "https://content.sharphuman.com",
    "sales": "https://sales.sharphuman.com",
    "reach": "https://reach.sharphuman.com",
    "assistant": "https://assistant.sharphuman.com",
    "admin": "https://admin.sharphuman.com",
}

# App info for tiles
APPS = [
    ("jd", "📝", "JD Writer", "Create compelling job descriptions in seconds"),
    ("screen", "🔍", "CV Screener", "Automatically rank candidates against requirements"),
    ("interview", "🎯", "Interview Prep", "Generate role-specific questions & scorecards"),
    ("source", "🎣", "Sourcing", "Boolean strings & outreach sequences"),
    ("content", "✍️", "Content", "Blogs, social posts, employer branding"),
    ("sales", "💰", "Sales Analysis", "Analyze calls & extract insights"),
    ("reach", "🚀", "BD Outreach", "Multi-channel business development"),
    ("assistant", "🤖", "AI Assistant", "Your intelligent recruiting partner"),
]

# ============================================
# AUTH FUNCTIONS
# ============================================

def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", 
                          headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, 
                          json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            user = data.get("user", {})
            # Create session token for cross-app auth
            session_token = create_session(user.get("id"), email)
            return {"success": True, "user": user, "session_token": session_token}
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
            return {"success": True, "message": "Check email!"}
        return {"success": False, "message": data.get("error_description") or "Failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def supabase_magic_link(email):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink", 
                          headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, 
                          json={"email": email}, timeout=10)
        return {"success": r.status_code == 200, "message": "Magic link sent!" if r.status_code == 200 else "Failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def create_session(user_id, email):
    """Create a session in Supabase and return the token."""
    token = secrets.token_urlsafe(32)
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/sessions",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
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
        if r.status_code in [200, 201]:
            return token
    except:
        pass
    return token  # Return token anyway for GOD mode

def validate_session_token(token):
    """Validate a session token from URL and return user info."""
    if not token:
        return None
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_ANON_KEY}"},
            timeout=10
        )
        if r.status_code == 200:
            sessions = r.json()
            if sessions:
                session = sessions[0]
                # Check expiry
                expires = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
                if expires.replace(tzinfo=None) > datetime.utcnow():
                    # Get user profile
                    user_r = requests.get(
                        f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}",
                        headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_ANON_KEY}"},
                        timeout=10
                    )
                    if user_r.status_code == 200 and user_r.json():
                        profile = user_r.json()[0]
                        return {
                            "user_id": session["user_id"],
                            "email": profile.get("email"),
                            "plan": profile.get("plan", "free"),
                            "session_id": session["id"],
                            "token": token
                        }
    except:
        pass
    return None

def log_usage(user_id, session_id, app, action, tokens_used=0):
    """Log usage to Supabase."""
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/usage_logs",
            headers={
                "apikey": SUPABASE_ANON_KEY, 
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "user_id": user_id,
                "session_id": session_id,
                "app": app,
                "action": action,
                "tokens_used": tokens_used
            },
            timeout=5
        )
    except:
        pass

# ============================================
# SESSION MANAGEMENT
# ============================================

def init_session():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_god' not in st.session_state:
        st.session_state.is_god = False
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None
    if 'user_plan' not in st.session_state:
        st.session_state.user_plan = "free"

def check_url_auth():
    """Check for auth token in URL params."""
    token = st.query_params.get("auth")
    if token and not st.session_state.authenticated:
        user_info = validate_session_token(token)
        if user_info:
            st.session_state.authenticated = True
            st.session_state.user = {"email": user_info["email"], "id": user_info["user_id"]}
            st.session_state.session_token = token
            st.session_state.user_plan = user_info.get("plan", "free")
            st.session_state.is_god = user_info.get("plan") == "god"
            return True
    return False

def get_user_email():
    if st.session_state.user:
        return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"

def build_app_url(app_name):
    """Build URL with auth token for cross-app navigation."""
    base_url = APP_URLS.get(app_name, "")
    token = st.session_state.get("session_token", "")
    if base_url and token:
        return f"{base_url}?auth={token}"
    return base_url

# ============================================
# UI COMPONENTS
# ============================================

def render_auth():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f, #0f0f1a); }
    * { font-family: 'Nunito', sans-serif !important; }
    .stTextInput>div>div>input { 
        background: #12121a !important; 
        border: 1px solid rgba(99,102,241,0.3) !important; 
        color: white !important; 
    }
    .stButton>button { 
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; 
        color: white !important; 
        border: none !important; 
    }
    .stTabs [data-baseweb="tab-list"] { background: #12121a; }
    .stTabs [aria-selected="true"] { background: rgba(99,102,241,0.3) !important; color: white !important; }
    </style>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:40px 0;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:16px;">
            <h1 style="color:white;">Sharp Suite</h1>
            <p style="color:#9ca3af;">AI-Powered Recruiting Tools</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        
        with tab1:
            e = st.text_input("Email", key="le")
            p = st.text_input("Password", type="password", key="lp")
            
            if st.button("Log In", use_container_width=True):
                if p == GOD_PASSWORD:
                    # GOD mode - create session token
                    token = secrets.token_urlsafe(32)
                    st.session_state.authenticated = True
                    st.session_state.is_god = True
                    st.session_state.user = {"email": "GOD", "id": "god"}
                    st.session_state.user_plan = "god"
                    st.session_state.session_token = token
                    # Log usage
                    log_usage("god", None, "portal", "login_god")
                    st.rerun()
                elif e and p:
                    r = supabase_sign_in(e, p)
                    if r["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = r["user"]
                        st.session_state.session_token = r.get("session_token")
                        # Log usage
                        log_usage(r["user"].get("id"), None, "portal", "login")
                        st.rerun()
                    else:
                        st.error(r["message"])
            
            st.markdown("<p style='text-align:center;color:#6b7280;'>— or —</p>", unsafe_allow_html=True)
            
            me = st.text_input("Email for magic link", key="me", label_visibility="collapsed", placeholder="Email for magic link")
            if st.button("✨ Send Magic Link", use_container_width=True, key="ml"):
                if me:
                    r = supabase_magic_link(me)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
        
        with tab2:
            se = st.text_input("Email", key="se")
            sp = st.text_input("Password", type="password", key="sp")
            sc = st.text_input("Confirm Password", type="password", key="sc")
            
            if st.button("Create Account", use_container_width=True):
                if sp != sc:
                    st.error("Passwords don't match")
                elif len(sp) < 6:
                    st.warning("Password must be at least 6 characters")
                elif se and sp:
                    r = supabase_sign_up(se, sp)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])

def render_sidebar():
    """Render sidebar with navigation."""
    with st.sidebar:
        # User info
        st.markdown(f"""
        <div style='padding:12px;background:rgba(99,102,241,0.1);border-radius:8px;margin-bottom:16px;'>
            <p style='color:#9ca3af;margin:0;font-size:0.75rem;'>Logged in as</p>
            <p style='color:white;margin:0;font-weight:600;'>{get_user_email()}</p>
            <p style='color:#6366f1;margin:0;font-size:0.75rem;text-transform:uppercase;'>{st.session_state.get('user_plan', 'free')} plan</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🧭 Quick Links")
        
        # Current app indicator
        st.button("🏠 Portal ◀", disabled=True, use_container_width=True)
        
        st.markdown("---")
        
        if st.session_state.get("is_god") or st.session_state.get("user_plan") == "god":
            st.link_button("⚙️ Admin Dashboard", build_app_url("admin"), use_container_width=True)
            st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.session_token = None
            st.session_state.is_god = False
            st.rerun()

def render_dashboard():
    """Render main dashboard with app tiles."""
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    * { font-family: 'Nunito', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #0a0a0f, #0f0f1a); }
    h1, h2, h3, h4 { color: white !important; }
    p, span, label { color: #e5e5e5 !important; }
    
    .app-tile {
        background: linear-gradient(135deg, #12121a, #1a1a2e);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    .app-tile:hover {
        border-color: rgba(99,102,241,0.8);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(99,102,241,0.2);
    }
    .app-icon { font-size: 2.5rem; margin-bottom: 12px; }
    .app-title { font-size: 1.2rem; font-weight: 700; color: white; margin-bottom: 8px; }
    .app-desc { font-size: 0.85rem; color: #9ca3af; }
    
    .stLinkButton > a {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
    }
    </style>""", unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:32px;">
        <img src="https://sharphuman.com/logo1-3.png" style="width:50px;">
        <div>
            <h1 style="margin:0;">Sharp Suite</h1>
            <p style="color:#9ca3af;margin:0;">Your AI Recruiting Toolkit</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # App tiles - 4 columns
    cols = st.columns(4)
    
    for i, (app_key, icon, title, desc) in enumerate(APPS):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="app-tile">
                <div class="app-icon">{icon}</div>
                <div class="app-title">{title}</div>
                <div class="app-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            st.link_button(f"Open {title}", build_app_url(app_key), use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# MAIN
# ============================================

st.set_page_config(page_title="Sharp Suite", page_icon="🚀", layout="wide")
init_session()

# Check for URL auth token first
check_url_auth()

if not st.session_state.authenticated:
    render_auth()
else:
    render_sidebar()
    render_dashboard()
