"""Sharp JD - Job Description Writer with Shared Auth"""
import streamlit as st
import os

# Import shared auth module (in production, this would be a package)
# For now, we inline the essential functions

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

import requests
import hashlib
from datetime import datetime, timedelta
import json

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
            return {"success": True, "user": data.get("user"), "access_token": data.get("access_token")}
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
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=2000):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set"
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", 
                          headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, 
                          json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, 
                          timeout=120)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            # Log usage
            if st.session_state.user:
                tokens_used = (len(prompt) + len(text)) // 4
                log_usage(
                    st.session_state.user.get("id"),
                    st.session_state.get("session_token"),
                    "jd",
                    "generate_jd",
                    tokens_used
                )
            return text
        return f"Error: {r.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# ============================================
# UI
# ============================================

def render_auth():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}.stTextInput>div>div>input{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}.stTabs [data-baseweb="tab-list"]{background:#12121a;}.stTabs [aria-selected="true"]{background:rgba(99,102,241,0.3)!important;color:white!important;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:40px 0;"><img src="https://sharphuman.com/logo1-3.png" style="width:70px;margin-bottom:16px;"><h1 style="color:white;">Sharp JD</h1><p style="color:#9ca3af;">Job Description Writer</p></div>""", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        with tab1:
            e, p = st.text_input("Email", key="le"), st.text_input("Password", type="password", key="lp")
            if st.button("Log In", use_container_width=True):
                if p == GOD_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_god = True
                    st.session_state.user = {"email": "GOD", "id": "god"}
                    st.session_state.user_plan = "god"
                    st.session_state.session_token = "god_mode"
                    st.rerun()
                elif e and p:
                    r = supabase_sign_in(e, p)
                    if r["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = r["user"]
                        st.rerun()
                    else:
                        st.error(r["message"])
            st.markdown("<p style='text-align:center;color:#6b7280;'>— or —</p>", unsafe_allow_html=True)
            me = st.text_input("Magic link", key="me", label_visibility="collapsed", placeholder="Email")
            if st.button("✨ Magic Link", use_container_width=True, key="ml"):
                if me:
                    r = supabase_magic_link(me)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
        with tab2:
            se, sp, sc = st.text_input("Email", key="se"), st.text_input("Password", type="password", key="sp"), st.text_input("Confirm", type="password", key="sc")
            if st.button("Create Account", use_container_width=True):
                if sp != sc:
                    st.error("Passwords don't match")
                elif len(sp) < 6:
                    st.warning("6+ chars")
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
        
        st.markdown("#### 🧭 Apps")
        
        apps = [
            ("portal", "🏠 Portal"),
            ("jd", "📝 JD Writer"),
            ("screen", "🔍 CV Screener"),
            ("interview", "🎯 Interview"),
            ("source", "🎣 Sourcing"),
            ("content", "✍️ Content"),
            ("sales", "💰 Sales"),
            ("reach", "🚀 Reach"),
            ("assistant", "🤖 Assistant"),
        ]
        
        for app_key, label in apps:
            if app_key == "jd":
                st.button(f"{label} ◀", disabled=True, use_container_width=True)
            else:
                url = build_app_url(app_key)
                st.link_button(label, url, use_container_width=True)
        
        if st.session_state.get("is_god") or st.session_state.get("user_plan") == "god":
            st.markdown("---")
            st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.session_token = None
            st.session_state.is_god = False
            st.rerun()

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp JD", page_icon="📝", layout="wide")
init_session()

# Check for URL auth token first
check_url_auth()

if not st.session_state.authenticated:
    render_auth()
    st.stop()

# Main app styles
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}h1,h2,h3{color:white!important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stSelectbox>div>div>div{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}.output-box{background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:24px;margin:16px 0;}p,span,label{color:#e5e5e5!important;}</style>""", unsafe_allow_html=True)

# Sidebar navigation
render_sidebar()

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;">Sharp JD</h1><p style="color:#9ca3af;margin:0;">AI-Powered Job Descriptions</p></div></div>""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    title = st.text_input("Job Title", placeholder="e.g. Senior Software Engineer")
    company = st.text_input("Company", placeholder="e.g. Acme Corp")
    details = st.text_area("Key Requirements & Details", height=150, placeholder="• 5+ years Python experience\n• Remote friendly\n• Competitive salary...")

with col2:
    tone = st.selectbox("Tone", ["Professional", "Casual", "Startup Vibe", "Corporate"])
    length = st.selectbox("Length", ["Standard", "Detailed", "Brief"])
    include_salary = st.checkbox("Include salary placeholder")
    include_benefits = st.checkbox("Include benefits section", value=True)

if st.button("📝 Generate Job Description", type="primary", use_container_width=True):
    if title:
        prompt = f"""Write a {tone.lower()} job description for a {title} position at {company or 'a growing company'}.

Requirements and details:
{details or 'Standard requirements for this role'}

Length: {length}
{"Include a salary range placeholder section." if include_salary else ""}
{"Include a comprehensive benefits section." if include_benefits else ""}

Format with clear sections: About Us, The Role, Responsibilities, Requirements, Nice to Have, {"Salary Range, " if include_salary else ""}{"Benefits, " if include_benefits else ""}How to Apply."""

        with st.spinner("✨ Generating..."):
            result = call_claude(prompt)
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
            
            # Copy button
            st.download_button(
                "📋 Download as Text",
                result,
                file_name=f"job_description_{title.lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )
    else:
        st.warning("Please enter a job title")
