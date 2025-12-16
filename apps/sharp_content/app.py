"""Sharp Content - Recruiting Content Generator (STRIPPED - Pure Streamlit)"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from shared_ui import apply_global_styles, render_top_banner, render_sidebar, render_app_header, COLORS
    from shared_config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY, ANTHROPIC_API_KEY, GOD_PASSWORD, APP_URLS
    USING_SHARED = True
except ImportError:
    USING_SHARED = False
    SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
    GOD_PASSWORD = os.environ.get("GOD_PASSWORD", "G0DHum@n101!!!")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    APP_URLS = {"portal": "https://demo.sharphuman.com", "jd": "https://jd.sharphuman.com", "screen": "https://screen.sharphuman.com", "interview": "https://interview.sharphuman.com", "outreach": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com", "sales": "https://sales.sharphuman.com"}
    COLORS = {"primary": "#ff4b4b"}
    def apply_global_styles(): pass
    def render_top_banner(**kwargs):
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.link_button("Services", "https://sharphuman.com#services")
        with c2: st.link_button("Blog", "https://sharphuman.com/blog")
        with c3: st.link_button("Book Demo", "https://calendly.com/sharphuman/30min")
        with c4: st.link_button("sharphuman.com", "https://sharphuman.com")
        st.divider()
    def render_app_header(title, subtitle=""): st.title(title); st.caption(subtitle) if subtitle else None; st.divider()
    def render_sidebar(current_app, user_email="", user_plan="free", session_token=""):
        with st.sidebar:
            st.title("Sharp Suite"); st.write(f"**{user_email}**"); st.caption(f"{user_plan.upper()} Plan"); st.divider()
            for key, label in [("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"), ("interview", "🎯 Interview"), ("outreach", "🚀 Outreach"), ("content", "✍️ Content"), ("sales", "💰 Sales")]:
                if key == current_app: st.success(f"**{label}** ◀")
                else: st.link_button(label, f"{APP_URLS.get(key, '')}?token={session_token}" if session_token else APP_URLS.get(key, ""), use_container_width=True)
            st.divider()
            if st.button("🚪 Logout", use_container_width=True):
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try: requests.post(f"{SUPABASE_URL}/rest/v1/sessions", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json"}, json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "content", "is_active": True, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()}, timeout=10)
    except: pass
    return token

def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"): return {"success": True, "user": data.get("user", {}), "session_token": create_session(data.get("user", {}).get("id"), email)}
        return {"success": False, "message": data.get("error_description") or "Invalid"}
    except Exception as e: return {"success": False, "message": str(e)}

def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        return {"success": True, "message": "Check email!"} if r.status_code == 200 and r.json().get("user") else {"success": False, "message": "Failed"}
    except Exception as e: return {"success": False, "message": str(e)}

def validate_session_token(token):
    if not token: return None
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        if r.status_code == 200 and r.json():
            session = r.json()[0]
            if datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00")).replace(tzinfo=None) > datetime.utcnow():
                ur = requests.get(f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
                if ur.status_code == 200 and ur.json(): return {"user_id": session["user_id"], "email": ur.json()[0].get("email"), "plan": ur.json()[0].get("plan", "free"), "token": token}
    except: pass
    return None

def log_usage(user_id, session_id, app, action, tokens_used=0):
    try: requests.post(f"{SUPABASE_URL}/rest/v1/usage_logs", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json"}, json={"user_id": user_id, "session_id": session_id, "app": app, "action": action, "tokens_used": tokens_used}, timeout=5)
    except: pass

def init_session():
    for k, v in [('authenticated', False), ('user', None), ('session_token', ''), ('is_god', False), ('user_plan', 'free'), ('working_on', None)]:
        if k not in st.session_state: st.session_state[k] = v

def check_url_auth():
    if st.session_state.authenticated: return
    token = st.query_params.get("token") or st.query_params.get("auth")
    if token:
        user_info = validate_session_token(token)
        if user_info: st.session_state.authenticated = True; st.session_state.user = {"email": user_info["email"], "id": user_info["user_id"]}; st.session_state.session_token = token; st.session_state.user_plan = user_info.get("plan", "free")

def get_user_email(): return st.session_state.user.get("email", "User") if st.session_state.user else ("GOD" if st.session_state.is_god else "User")

def call_claude(prompt, max_tokens=2000):
    if not ANTHROPIC_API_KEY: return "Error: API key not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            if st.session_state.user: log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "content", "generate", (len(prompt)+len(text))//4)
            return text, (len(prompt)+len(text))//4
        return f"Error: {r.status_code}", 0
    except Exception as e: return f"Error: {str(e)}", 0

# MAIN APP
st.set_page_config(page_title="Sharp Content", page_icon="✍️", layout="wide")
init_session()
check_url_auth()
apply_global_styles()

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("✍️ Sharp Content")
        st.caption("AI-Powered Recruiting Content")
        st.divider()
        t1, t2 = st.tabs(["Log In", "Sign Up"])
        with t1:
            email = st.text_input("Email", key="l_email"); pwd = st.text_input("Password", type="password", key="l_pwd")
            if st.button("Log In", use_container_width=True, type="primary"):
                if pwd == GOD_PASSWORD: st.session_state.authenticated = True; st.session_state.is_god = True; st.session_state.user = {"email": "GOD", "id": "god"}; st.session_state.session_token = secrets.token_urlsafe(32); st.rerun()
                elif email and pwd:
                    r = supabase_sign_in(email, pwd)
                    if r["success"]: st.session_state.authenticated = True; st.session_state.user = r["user"]; st.session_state.session_token = r.get("session_token"); st.rerun()
                    else: st.error(r["message"])
        with t2:
            s_email = st.text_input("Email", key="s_email"); s_pwd = st.text_input("Password", type="password", key="s_pwd"); s_conf = st.text_input("Confirm", type="password", key="s_conf")
            if st.button("Create Account", use_container_width=True, type="primary"):
                if s_pwd != s_conf: st.error("Passwords don't match")
                elif len(s_pwd) < 6: st.warning("6+ characters")
                elif s_email and s_pwd: r = supabase_sign_up(s_email, s_pwd); st.success(r["message"]) if r["success"] else st.error(r["message"])
    st.stop()

render_top_banner()
render_sidebar(current_app="content", user_email=get_user_email(), user_plan=st.session_state.get('user_plan', 'free'), session_token=st.session_state.get('session_token', ''))
render_app_header("Sharp Content", "AI-Powered Recruiting Content Generator")

CONTENT_TYPES = ["LinkedIn Post", "Job Ad", "Career Page Copy", "Recruitment Email", "Employee Spotlight", "Company Culture Post", "Industry Thought Leadership"]

st.subheader("📝 Create Content")

c1, c2 = st.columns(2)
with c1:
    content_type = st.selectbox("Content Type", CONTENT_TYPES)
    company = st.text_input("Company Name", placeholder="Acme Corp")
    industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Other"])
with c2:
    tone = st.selectbox("Tone", ["Professional", "Casual", "Enthusiastic", "Thought-provoking", "Inspirational"])
    target = st.selectbox("Target Audience", ["Candidates", "Passive Talent", "Industry Peers", "General Public"])
    length = st.selectbox("Length", ["Short (< 100 words)", "Medium (100-250 words)", "Long (250+ words)"])

topic = st.text_area("Topic / Key Points", placeholder="What should this content be about? Any specific messages or themes?", height=100)

if st.button("✨ Generate Content", type="primary", use_container_width=True):
    if topic:
        with st.spinner("Creating content..."):
            prompt = f"""Generate {content_type} content:

Company: {company or "A growing company"}
Industry: {industry}
Tone: {tone}
Target Audience: {target}
Length: {length}
Topic/Key Points: {topic}

Create compelling, authentic content that would perform well on the target platform. Include relevant hashtags if it's social media content."""
            result, tokens = call_claude(prompt)
            st.divider()
            st.subheader("📄 Generated Content")
            st.text_area("Your Content", result, height=300)
            
            c1, c2 = st.columns(2)
            with c1: st.download_button("📥 Download", result, f"{content_type.replace(' ', '_').lower()}.txt", "text/plain")
            with c2: st.metric("Tokens Used", tokens)

st.divider()

with st.expander("💡 Content Ideas"):
    st.write("Need inspiration? Try these popular topics:")
    ideas = [
        "🎯 Day in the life of a [role] at our company",
        "🚀 Why we're hiring for [role] - team growth story",
        "💡 Industry trends affecting [field] hiring",
        "🏆 Employee success story / career progression",
        "🌟 What makes our culture unique",
        "📈 Company milestone / growth announcement",
    ]
    for idea in ideas:
        st.write(f"• {idea}")
