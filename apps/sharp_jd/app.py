"""Sharp JD - AI Job Description Writer (STRIPPED - Pure Streamlit)"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re
import io
import sys

# Add parent directory for shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# ============================================
# SHARED MODULE IMPORTS
# ============================================
try:
    from shared_ui import (
        apply_global_styles,
        render_top_banner,
        render_sidebar,
        render_app_header,
        COLORS
    )
    from shared_config import (
        SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY,
        ANTHROPIC_API_KEY, GOD_PASSWORD, APP_URLS
    )
    USING_SHARED = True
except ImportError:
    USING_SHARED = False
    SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
    GOD_PASSWORD = os.environ.get("GOD_PASSWORD", "G0DHum@n101!!!")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    APP_URLS = {
        "portal": "https://demo.sharphuman.com", "jd": "https://jd.sharphuman.com",
        "screen": "https://screen.sharphuman.com", "interview": "https://interview.sharphuman.com",
        "outreach": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com",
        "sales": "https://sales.sharphuman.com", "admin": "https://admin.sharphuman.com",
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


# ============================================
# AUTH FUNCTIONS
# ============================================

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "jd",
                  "is_active": True, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()}, timeout=10)
    except: pass
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
        return {"success": True, "message": "Check email!"} if r.status_code == 200 and data.get("user") else {"success": False, "message": data.get("error_description") or "Failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def validate_session_token(token):
    if not token: return None
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        if r.status_code == 200 and r.json():
            session = r.json()[0]
            expires = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
            if expires.replace(tzinfo=None) > datetime.utcnow():
                ur = requests.get(f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}",
                    headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
                if ur.status_code == 200 and ur.json():
                    p = ur.json()[0]
                    return {"user_id": session["user_id"], "email": p.get("email"), "plan": p.get("plan", "free"), "token": token}
    except: pass
    return None


def log_usage(user_id, session_id, app, action, tokens_used=0):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/usage_logs",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "session_id": session_id, "app": app, "action": action, "tokens_used": tokens_used}, timeout=5)
    except: pass


# ============================================
# SESSION MANAGEMENT
# ============================================

def init_session():
    defaults = [('authenticated', False), ('user', None), ('session_token', ''),
                ('is_god', False), ('user_plan', 'free'), ('generated_jd', ''),
                ('jd_metadata', None), ('working_on', None), ('requirements_text', '')]
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


def get_user_email():
    if st.session_state.user:
        return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"


def build_app_url(app_key):
    base_url = APP_URLS.get(app_key, f"https://{app_key}.sharphuman.com")
    token = st.session_state.get("session_token", "")
    return f"{base_url}?token={token}" if token else base_url


# ============================================
# FILE HANDLING
# ============================================

def extract_text_from_file(uploaded_file):
    name = uploaded_file.name.lower()
    content = uploaded_file.read()
    
    if name.endswith('.txt'):
        return content.decode('utf-8', errors='ignore')
    elif name.endswith('.json'):
        try:
            data = json.loads(content)
            return json.dumps(data, indent=2) if isinstance(data, dict) else str(data)
        except:
            return content.decode('utf-8', errors='ignore')
    elif name.endswith('.pdf'):
        try:
            import fitz
            doc = fitz.open(stream=content, filetype="pdf")
            return "\n".join([page.get_text() for page in doc])
        except:
            return "[PDF extraction requires PyMuPDF]"
    elif name.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join([p.text for p in doc.paragraphs])
        except:
            return "[DOCX extraction requires python-docx]"
    return "[Unsupported format]"


# ============================================
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=3000):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            tokens = (len(prompt) + len(text)) // 4
            if st.session_state.user:
                log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "jd", "generate", tokens)
            return text, tokens
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0


def calculate_seo_score(jd_text, metadata):
    score = 50
    jd_lower = jd_text.lower()
    if metadata.get("job_title", "").lower() in jd_lower: score += 10
    for kw in ["responsibilities", "requirements", "qualifications", "benefits"]:
        if kw in jd_lower: score += 3
    words = len(jd_text.split())
    if 300 <= words <= 800: score += 10
    elif 200 <= words <= 1000: score += 5
    if any(v in jd_lower for v in ["manage", "lead", "develop", "create", "build"]): score += 5
    if "equal opportunity" in jd_lower or "diversity" in jd_lower: score += 5
    return min(max(score, 1), 100)


# ============================================
# DATABASE FUNCTIONS
# ============================================

def save_jd_to_history(metadata, generated_jd, seo_score, tokens_used):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god":
        return None, "History not available in GOD mode"
    
    payload = {
        "user_id": user_id,
        "job_title": metadata.get('job_title', 'Untitled'),
        "company": metadata.get('company'),
        "experience_level": metadata.get('experience_level'),
        "remote_type": metadata.get('remote_type'),
        "industry": metadata.get('industry'),
        "tone": metadata.get('tone'),
        "user_type": metadata.get('user_type'),
        "word_count": len(generated_jd.split()),
        "generated_jd": generated_jd,
        "seo_ats_score": seo_score,
        "tokens_used": tokens_used or 0
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/jd_history",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=representation"},
            json=payload, timeout=10)
        if r.status_code in [200, 201]:
            return r.json()[0] if r.json() else {"id": "saved"}, None
        return None, f"Status {r.status_code}"
    except Exception as e:
        return None, str(e)


def get_jd_history(limit=50):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god": 
        return []
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/jd_history?user_id=eq.{user_id}&order=created_at.desc&limit={limit}",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []


# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp JD", page_icon="📝", layout="wide")
init_session()
check_url_auth()

# Apply styles
apply_global_styles()

# Auth screen
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📝 Sharp JD")
        st.caption("AI Job Description Writer")
        st.divider()
        
        t1, t2 = st.tabs(["Log In", "Sign Up"])
        with t1:
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
        with t2:
            s_email = st.text_input("Email", key="s_email")
            s_pwd = st.text_input("Password", type="password", key="s_pwd")
            s_conf = st.text_input("Confirm", type="password", key="s_conf")
            if st.button("Create Account", use_container_width=True, type="primary"):
                if s_pwd != s_conf: st.error("Passwords don't match")
                elif len(s_pwd) < 6: st.warning("6+ characters")
                elif s_email and s_pwd:
                    r = supabase_sign_up(s_email, s_pwd)
                    st.success(r["message"]) if r["success"] else st.error(r["message"])
    st.stop()

# Authenticated UI
render_top_banner()
render_sidebar(
    current_app="jd",
    user_email=get_user_email(),
    user_plan=st.session_state.get('user_plan', 'free'),
    session_token=st.session_state.get('session_token', '')
)

# Header
render_app_header("Sharp JD", "AI-Powered Job Descriptions")

# Working indicator
if st.session_state.working_on:
    st.info(f"⏳ {st.session_state.working_on}")

# Tabs
tab_create, tab_history = st.tabs(["✏️ Create JD", "📜 History"])

with tab_create:
    st.subheader("📋 Job Details")
    
    c1, c2 = st.columns(2)
    with c1:
        job_title = st.text_input("Job Title *", placeholder="e.g. Senior Software Engineer")
        company = st.text_input("Company", placeholder="e.g. Acme Corp")
        experience_level = st.selectbox("Level", ["Entry Level", "Mid Level", "Senior", "Lead", "Manager", "Director", "Executive"])
    
    with c2:
        industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Education", "Media", "Consulting", "Government", "Non-Profit", "Other"])
        remote_type = st.selectbox("Work Type", ["Remote", "Hybrid", "On-site"])
        tone = st.selectbox("Tone", ["Professional", "Casual/Startup", "Formal/Corporate", "Friendly", "Bold/Exciting"])
    
    user_type = st.radio("I am a:", ["🏢 Recruiter (Agency)", "👔 Internal HR / TA"], horizontal=True)
    
    st.subheader("📝 Requirements")
    
    req_source = st.radio("Source:", ["📝 Type/Paste", "📄 Upload File"], horizontal=True)
    
    if req_source == "📄 Upload File":
        req_file = st.file_uploader("Upload requirements", type=['pdf', 'docx', 'txt', 'json'])
        if req_file:
            st.session_state.requirements_text = extract_text_from_file(req_file)
            st.success(f"✅ Loaded from {req_file.name}")
    
    requirements = st.text_area(
        "Key requirements & responsibilities",
        value=st.session_state.get('requirements_text', ''),
        height=150,
        placeholder="• 5+ years experience\n• Python, AWS\n• Leadership skills..."
    )
    st.session_state.requirements_text = requirements
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: inc_salary = st.checkbox("💰 Salary", value=True)
    with c2: inc_benefits = st.checkbox("🎁 Benefits", value=True)
    with c3: inc_diversity = st.checkbox("🌈 Diversity", value=True)
    with c4: word_target = st.select_slider("Words", [300, 400, 500, 600, 700, 800], value=500)
    
    if st.button("📝 Generate Job Description", type="primary", use_container_width=True):
        if not job_title:
            st.warning("Enter a job title")
        else:
            st.session_state.working_on = "Writing JD..."
            
            user_context = "an external recruiter at a staffing agency" if "Recruiter" in user_type else "an internal HR/TA professional"
            
            prompt = f"""Write a compelling job description:

**Context:** I am {user_context} writing this JD.

**Job:** {job_title}
**Company:** {company or "A growing company"}
**Level:** {experience_level}
**Industry:** {industry}
**Work Type:** {remote_type}
**Tone:** {tone}

**Requirements/Base Content:** 
{requirements or "Standard for this role"}

**Include:**
- About Company (2-3 sentences)
- About Role
- Responsibilities (5-7 bullets)
- Requirements (must-have and nice-to-have separated)
{"- Salary range placeholder" if inc_salary else ""}
{"- Benefits section" if inc_benefits else ""}
{"- Diversity/EEO statement" if inc_diversity else ""}
- How to Apply

Target: ~{word_target} words. Make it compelling and clear."""

            with st.spinner("Writing..."):
                result, tokens = call_claude(prompt)
                st.session_state.working_on = None
                
                if not result.startswith("Error"):
                    st.session_state.generated_jd = result
                    st.session_state.jd_metadata = {
                        "job_title": job_title, "company": company, "experience_level": experience_level,
                        "remote_type": remote_type, "industry": industry, "tone": tone,
                        "user_type": user_type, "tokens_used": tokens
                    }
                    st.rerun()
                else:
                    st.error(result)

    # Display generated JD
    if st.session_state.generated_jd:
        st.divider()
        st.subheader("📄 Your Job Description")
        
        meta = st.session_state.jd_metadata or {}
        seo = calculate_seo_score(st.session_state.generated_jd, meta)
        words = len(st.session_state.generated_jd.split())
        
        # Stats
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Words", words)
        with c2:
            st.metric("SEO Score", f"{seo}/100")
        with c3:
            st.metric("Tokens", meta.get('tokens_used', 0))
        
        # JD Content
        st.text_area("Generated JD", st.session_state.generated_jd, height=400)
        
        # Actions
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("📥 Download TXT", st.session_state.generated_jd, 
                             f"{meta.get('job_title', 'JD').replace(' ', '_')}.txt", "text/plain")
        with c2:
            if st.button("💾 Save to History"):
                saved, err = save_jd_to_history(meta, st.session_state.generated_jd, seo, meta.get('tokens_used'))
                if saved:
                    st.success("Saved!")
                else:
                    st.error(err or "Failed to save")
        with c3:
            if st.button("🔄 Generate New"):
                st.session_state.generated_jd = ""
                st.session_state.jd_metadata = None
                st.rerun()

with tab_history:
    st.subheader("📜 Your JD History")
    
    history = get_jd_history()
    
    if not history:
        st.info("No saved JDs yet. Generate and save some!")
    else:
        for jd in history:
            with st.expander(f"📝 {jd.get('job_title', 'Untitled')} - {jd.get('created_at', '')[:10]}"):
                st.write(f"**Company:** {jd.get('company', 'N/A')}")
                st.write(f"**Level:** {jd.get('experience_level', 'N/A')}")
                st.write(f"**Words:** {jd.get('word_count', 'N/A')} | **SEO:** {jd.get('seo_ats_score', 'N/A')}")
                st.text_area("Content", jd.get('generated_jd', ''), height=200, key=f"hist_{jd.get('id')}")
