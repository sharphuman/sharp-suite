"""Sharp Screen - CV Screening (STRIPPED - Pure Streamlit)"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re
import io
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# ============================================
# IMPORTS
# ============================================
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
    COLORS = {"primary": "#ff4b4b", "success": "#21c354", "warning": "#faca2b", "error": "#ff4b4b"}
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

# ============================================
# AUTH
# ============================================
def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try: requests.post(f"{SUPABASE_URL}/rest/v1/sessions", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "screen", "is_active": True, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()}, timeout=10)
    except: pass
    return token

def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            user = data.get("user", {})
            return {"success": True, "user": user, "session_token": create_session(user.get("id"), email)}
        return {"success": False, "message": data.get("error_description") or "Invalid"}
    except Exception as e: return {"success": False, "message": str(e)}

def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        return {"success": True, "message": "Check email!"} if r.status_code == 200 and r.json().get("user") else {"success": False, "message": r.json().get("error_description") or "Failed"}
    except Exception as e: return {"success": False, "message": str(e)}

def validate_session_token(token):
    if not token: return None
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        if r.status_code == 200 and r.json():
            session = r.json()[0]
            if datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00")).replace(tzinfo=None) > datetime.utcnow():
                ur = requests.get(f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
                if ur.status_code == 200 and ur.json():
                    p = ur.json()[0]
                    return {"user_id": session["user_id"], "email": p.get("email"), "plan": p.get("plan", "free"), "token": token}
    except: pass
    return None

def log_usage(user_id, session_id, app, action, tokens_used=0):
    try: requests.post(f"{SUPABASE_URL}/rest/v1/usage_logs", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": user_id, "session_id": session_id, "app": app, "action": action, "tokens_used": tokens_used}, timeout=5)
    except: pass

def init_session():
    for k, v in [('authenticated', False), ('user', None), ('session_token', ''), ('is_god', False), ('user_plan', 'free'), ('working_on', None), ('screening_results', None)]:
        if k not in st.session_state: st.session_state[k] = v

def check_url_auth():
    if st.session_state.authenticated: return
    token = st.query_params.get("token") or st.query_params.get("auth")
    if token:
        user_info = validate_session_token(token)
        if user_info:
            st.session_state.authenticated = True
            st.session_state.user = {"email": user_info["email"], "id": user_info["user_id"]}
            st.session_state.session_token = token
            st.session_state.user_plan = user_info.get("plan", "free")

def get_user_email():
    if st.session_state.user: return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"

# ============================================
# CLAUDE API
# ============================================
def call_claude(prompt, max_tokens=4000):
    if not ANTHROPIC_API_KEY: return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            if st.session_state.user: log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "screen", "screen", (len(prompt)+len(text))//4)
            return text, (len(prompt)+len(text))//4
        return f"Error: {r.status_code}", 0
    except Exception as e: return f"Error: {str(e)}", 0

def extract_text(uploaded_file):
    name = uploaded_file.name.lower()
    content = uploaded_file.read()
    uploaded_file.seek(0)
    if name.endswith('.txt'): return content.decode('utf-8', errors='ignore')
    if name.endswith('.pdf'):
        try:
            import fitz
            pdf = fitz.open(stream=content, filetype="pdf")
            return "\n".join([page.get_text() for page in pdf])
        except: return "[PDF extraction failed]"
    if name.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join([p.text for p in doc.paragraphs])
        except: return "[DOCX extraction failed]"
    return content.decode('utf-8', errors='ignore')

# ============================================
# MAIN APP
# ============================================
st.set_page_config(page_title="Sharp Screen", page_icon="🔍", layout="wide")
init_session()
check_url_auth()
apply_global_styles()

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🔍 Sharp Screen")
        st.caption("AI-Powered CV Screening")
        st.divider()
        t1, t2 = st.tabs(["Log In", "Sign Up"])
        with t1:
            email = st.text_input("Email", key="l_email")
            pwd = st.text_input("Password", type="password", key="l_pwd")
            if st.button("Log In", use_container_width=True, type="primary"):
                if pwd == GOD_PASSWORD:
                    st.session_state.authenticated = True; st.session_state.is_god = True
                    st.session_state.user = {"email": "GOD", "id": "god"}
                    st.session_state.session_token = secrets.token_urlsafe(32); st.rerun()
                elif email and pwd:
                    r = supabase_sign_in(email, pwd)
                    if r["success"]: st.session_state.authenticated = True; st.session_state.user = r["user"]; st.session_state.session_token = r.get("session_token"); st.rerun()
                    else: st.error(r["message"])
        with t2:
            s_email = st.text_input("Email", key="s_email"); s_pwd = st.text_input("Password", type="password", key="s_pwd"); s_conf = st.text_input("Confirm", type="password", key="s_conf")
            if st.button("Create Account", use_container_width=True, type="primary"):
                if s_pwd != s_conf: st.error("Passwords don't match")
                elif len(s_pwd) < 6: st.warning("6+ characters")
                elif s_email and s_pwd:
                    r = supabase_sign_up(s_email, s_pwd)
                    st.success(r["message"]) if r["success"] else st.error(r["message"])
    st.stop()

render_top_banner()
render_sidebar(current_app="screen", user_email=get_user_email(), user_plan=st.session_state.get('user_plan', 'free'), session_token=st.session_state.get('session_token', ''))
render_app_header("Sharp Screen", "AI-Powered CV Screening")

if st.session_state.working_on: st.info(f"⏳ {st.session_state.working_on}")

tab1, tab2, tab3 = st.tabs(["🔍 Screen & Rank", "👤 Blind Resume", "💰 Salary Estimator"])

with tab1:
    st.subheader("📋 Job Description")
    jd_source = st.radio("Source:", ["📝 Paste", "📚 History", "📄 Upload"], horizontal=True)
    if jd_source == "📄 Upload":
        jd_file = st.file_uploader("Upload JD", type=['txt', 'pdf', 'docx'])
        jd_text = extract_text(jd_file) if jd_file else ""
    else:
        jd_text = st.text_area("Paste Job Description", height=150, placeholder="Paste the full job description...")
    
    st.divider()
    st.subheader("📄 Candidate CVs")
    cv_source = st.radio("Source:", ["📝 Paste", "📤 Upload", "🔗 JSON/ATS"], horizontal=True, key="cv_src")
    
    if cv_source == "📤 Upload":
        cv_files = st.file_uploader("Upload CVs", type=['txt', 'pdf', 'docx'], accept_multiple_files=True)
        cvs_text = "\n---\n".join([extract_text(f) for f in cv_files]) if cv_files else ""
        if cv_files: st.success(f"✅ Loaded {len(cv_files)} CVs")
    else:
        cvs_text = st.text_area("Paste CVs (separate with ---)", height=200, placeholder="Paste CV 1 here...\n---\nPaste CV 2 here...")
    
    c1, c2, c3 = st.columns(3)
    with c1: bias_free = st.checkbox("🎭 Bias-Free Mode", value=True)
    with c2: ai_detect = st.checkbox("🤖 AI Detection", value=True)
    with c3: salary_est = st.checkbox("💰 Salary Estimate", value=True)
    
    if st.button("🔍 Screen Candidates", type="primary", use_container_width=True):
        if not jd_text: st.warning("Enter a job description")
        elif not cvs_text: st.warning("Add some CVs")
        else:
            st.session_state.working_on = "Screening candidates..."
            prompt = f"""Screen these candidates against the JD. Return JSON with: screening_summary, candidates (ranked by match_score), batch_insights.

JOB DESCRIPTION:
{jd_text}

CANDIDATES:
{cvs_text}

For each candidate include: rank, identifier, match_score (0-100), skills_breakdown, experience_years, strengths, concerns, recommended_action.
Return valid JSON only."""
            with st.spinner("Analyzing..."):
                result, tokens = call_claude(prompt, 6000)
                st.session_state.working_on = None
                st.session_state.screening_results = result
                st.rerun()
    
    if st.session_state.screening_results:
        st.divider()
        st.subheader("📊 Screening Results")
        try:
            data = json.loads(re.search(r'```json\s*(.*?)\s*```', st.session_state.screening_results, re.DOTALL).group(1) if '```json' in st.session_state.screening_results else st.session_state.screening_results)
            summary = data.get('screening_summary', {})
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total", summary.get('total_candidates', '?'))
            with c2: st.metric("Recommended", summary.get('recommended_for_interview', '?'))
            with c3: st.metric("Maybe", summary.get('maybe', '?'))
            with c4: st.metric("Pass", summary.get('not_recommended', '?'))
            
            for c in data.get('candidates', []):
                with st.expander(f"#{c.get('rank')} - {c.get('identifier')} ({c.get('match_score')}%)"):
                    st.write(f"**Score:** {c.get('match_score')}%")
                    st.write(f"**Experience:** {c.get('experience_years', '?')} years")
                    if c.get('strengths'): st.success("**Strengths:** " + ", ".join(c.get('strengths', [])))
                    if c.get('concerns'): st.warning("**Concerns:** " + ", ".join(c.get('concerns', [])))
                    st.write(f"**Action:** {c.get('recommended_action', 'N/A')}")
        except Exception as e:
            st.text_area("Raw Results", st.session_state.screening_results, height=300)

with tab2:
    st.subheader("👤 Blind Resume Generator")
    st.write("Remove identifying information from CVs for unbiased review.")
    cv_to_blind = st.text_area("Paste CV to anonymize", height=200)
    if st.button("🎭 Generate Blind Resume", type="primary"):
        if cv_to_blind:
            with st.spinner("Anonymizing..."):
                result, _ = call_claude(f"Remove all identifying info (name, email, phone, address, LinkedIn, company names) from this CV. Keep skills and experience. Return the anonymized version:\n\n{cv_to_blind}")
                st.text_area("Blind Resume", result, height=300)

with tab3:
    st.subheader("💰 Salary Estimator")
    st.write("Estimate market salary based on CV and location.")
    cv_for_salary = st.text_area("Paste CV", height=150, key="sal_cv")
    location = st.text_input("Location", placeholder="e.g. New York, NY")
    if st.button("💰 Estimate Salary", type="primary"):
        if cv_for_salary:
            with st.spinner("Estimating..."):
                result, _ = call_claude(f"Based on this CV and location ({location or 'US average'}), estimate salary range. Include: low/mid/high estimates, factors considered, market comparison.\n\nCV:\n{cv_for_salary}")
                st.write(result)
