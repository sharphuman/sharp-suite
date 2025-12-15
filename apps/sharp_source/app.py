"""Sharp Source - AI-Powered Candidate Sourcing & Outreach"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

APP_URLS = {
    "portal": "https://demo.sharphuman.com", "jd": "https://jd.sharphuman.com",
    "screen": "https://screen.sharphuman.com", "interview": "https://hire.sharphuman.com",
    "source": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com",
    "sales": "https://sales.sharphuman.com", "reach": "https://reach.sharphuman.com",
    "assistant": "https://assistant.sharphuman.com", "admin": "https://admin.sharphuman.com",
}

# Email sequence templates library
EMAIL_TEMPLATES = {
    "3_touch_passive": {
        "name": "3-Touch Passive Candidate",
        "description": "Gentle sequence for employed candidates not actively looking",
        "touches": 3,
        "spacing": "Day 1, Day 4, Day 10",
        "tone": "casual_friendly"
    },
    "2_touch_active": {
        "name": "2-Touch Active Seeker",
        "description": "Direct sequence for candidates actively job hunting",
        "touches": 2,
        "spacing": "Day 1, Day 3",
        "tone": "professional"
    },
    "4_touch_executive": {
        "name": "4-Touch Executive Outreach",
        "description": "High-touch sequence for senior/executive roles",
        "touches": 4,
        "spacing": "Day 1, Day 5, Day 12, Day 20",
        "tone": "executive"
    },
    "urgent_backfill": {
        "name": "Urgent Backfill",
        "description": "Fast 2-touch for immediate hiring needs",
        "touches": 2,
        "spacing": "Day 1, Day 2",
        "tone": "urgent"
    },
    "referral_warm": {
        "name": "Warm Referral Introduction",
        "description": "When you have a mutual connection to reference",
        "touches": 2,
        "spacing": "Day 1, Day 5",
        "tone": "warm_referral"
    }
}

# Platform-specific syntax
PLATFORM_SYNTAX = {
    "linkedin_recruiter": {
        "name": "LinkedIn Recruiter",
        "and": "AND",
        "or": "OR",
        "not": "NOT",
        "exact": '"phrase"',
        "tips": "Use current:yes for employed, years:5+ for experience"
    },
    "linkedin_basic": {
        "name": "LinkedIn Basic",
        "and": "AND",
        "or": "OR", 
        "not": "-",
        "exact": '"phrase"',
        "tips": "Limited to ~1000 results, no advanced filters"
    },
    "indeed": {
        "name": "Indeed",
        "and": "and",
        "or": "or",
        "not": "-",
        "exact": '"phrase"',
        "tips": "Add location:remote for remote roles"
    },
    "github": {
        "name": "GitHub",
        "and": " ",
        "or": "OR",
        "not": "-",
        "exact": '"phrase"',
        "tips": "Search repos, users, or code separately"
    },
    "stackoverflow": {
        "name": "Stack Overflow",
        "and": " ",
        "or": "or",
        "not": "-",
        "exact": '"phrase"',
        "tips": "Filter by tags and reputation"
    }
}

# ============================================
# AUTH FUNCTIONS
# ============================================

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "source",
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

def submit_feedback(app, feedback_type, message):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/user_feedback",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": st.session_state.user.get("id") if st.session_state.user else None,
                  "app": app, "feedback_type": feedback_type, "rating": 4, "message": message, 
                  "email": get_user_email()}, timeout=5)
        return True
    except: return False

def init_session():
    defaults = [
        ('authenticated', False), ('user', None), ('is_god', False), ('session_token', None),
        ('user_plan', 'free'), ('working_on', None), ('boolean_result', None),
        ('email_sequence', None), ('screening_rationale', None),
    ]
    for k, v in defaults:
        if k not in st.session_state:
            st.session_state[k] = v

def check_url_auth():
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
    return st.session_state.user.get("email", "User") if st.session_state.user else ("GOD" if st.session_state.is_god else "User")

def build_app_url(app_name):
    base = APP_URLS.get(app_name, "")
    token = st.session_state.get("session_token", "")
    return f"{base}?auth={token}" if base and token else base

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_jd_history(limit=20):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god": return []
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/jd_history?user_id=eq.{user_id}&order=created_at.desc&limit={limit}",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        return r.json() if r.status_code == 200 else []
    except: return []

def get_screen_history(limit=20):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god": return []
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/screen_history?user_id=eq.{user_id}&order=created_at.desc&limit={limit}",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        return r.json() if r.status_code == 200 else []
    except: return []

# ============================================
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=3000, action="source"):
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
                log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "source", action, tokens)
            return text, tokens
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0

# ============================================
# SOURCING FUNCTIONS
# ============================================

def generate_boolean_string(job_title, skills, experience, location, platform, nice_to_have=""):
    syntax = PLATFORM_SYNTAX.get(platform, PLATFORM_SYNTAX["linkedin_recruiter"])
    
    prompt = f"""Generate an optimized Boolean search string for {syntax['name']}.

## ROLE REQUIREMENTS:
- Job Title: {job_title}
- Required Skills: {skills}
- Nice-to-Have: {nice_to_have or 'None specified'}
- Experience Level: {experience}
- Location: {location}

## PLATFORM SYNTAX:
- AND operator: {syntax['and']}
- OR operator: {syntax['or']}
- NOT operator: {syntax['not']}
- Exact phrase: {syntax['exact']}
- Tips: {syntax['tips']}

## OUTPUT FORMAT:
```
PRIMARY SEARCH STRING:
[The main Boolean string optimized for this platform]

ALTERNATIVE (BROADER):
[A less restrictive version to expand results]

ALTERNATIVE (NARROWER):
[A more specific version for senior/exact matches]

TITLE VARIATIONS:
[List of job title synonyms to try]

SKILL SYNONYMS:
[Alternative terms for key skills]

PLATFORM-SPECIFIC TIPS:
[2-3 tips for better results on this platform]
```

Generate practical, copy-paste ready Boolean strings."""

    return call_claude(prompt, max_tokens=2000, action="boolean_search")

def generate_email_sequence(template_key, recruiter_info, candidate_info, job_info, cta_link="", include_rationale=False):
    template = EMAIL_TEMPLATES.get(template_key, EMAIL_TEMPLATES["3_touch_passive"])
    
    rationale_section = ""
    if include_rationale and candidate_info.get('screening_notes'):
        rationale_section = f"""
## SCREENING RATIONALE TO REFERENCE:
{candidate_info.get('screening_notes', '')}
- Mention specific skills/experience that made them stand out
- Reference why they're a good fit for this specific role
"""
    
    prompt = f"""Generate a {template['touches']}-email sequence for candidate outreach.

## TEMPLATE TYPE: {template['name']}
- Description: {template['description']}
- Timing: {template['spacing']}
- Tone: {template['tone']}

## RECRUITER INFO:
- Name: {recruiter_info.get('name', 'Recruiter')}
- Title: {recruiter_info.get('title', 'Talent Acquisition')}
- Company: {recruiter_info.get('company', 'Company')}
- Email: {recruiter_info.get('email', '')}
- Phone: {recruiter_info.get('phone', '')}

## CANDIDATE INFO:
- Name: {candidate_info.get('name', 'Candidate')}
- Current Role: {candidate_info.get('current_role', 'Professional')}
- LinkedIn: {candidate_info.get('linkedin', '')}
- Key Skills: {candidate_info.get('skills', '')}

## JOB DETAILS:
- Title: {job_info.get('title', 'Position')}
- Company: {job_info.get('company', 'Company')}
- Location: {job_info.get('location', 'Location')}
- Key Selling Points: {job_info.get('selling_points', '')}
- Salary Range: {job_info.get('salary', 'Competitive')}

## CTA:
- Calendar Link: {cta_link or '[CALENDAR_LINK]'}
{rationale_section}

## OUTPUT FORMAT:
For each email in the sequence, provide:

---
**EMAIL {'{n}'} - {'{timing}'}**

**Subject Line:** [Compelling subject, <50 chars]

**Body:**
[Email body with personalization tokens like {'{candidate_name}'}, {'{job_title}'}]

**CTA:** [Clear call to action]

**Character Count:** [LinkedIn has 300 char limit for InMails]
---

Make emails:
- Personalized and specific (not generic)
- Concise (respect their time)
- Value-focused (what's in it for them)
- With clear CTAs
- Appropriate for the {template['tone']} tone"""

    return call_claude(prompt, max_tokens=3000, action="email_sequence")

def generate_linkedin_message(candidate_name, job_title, hook, cta_link=""):
    prompt = f"""Write a LinkedIn connection request message (300 char MAX).

Candidate: {candidate_name}
Role: {job_title}  
Hook/Angle: {hook}
CTA Link: {cta_link or 'Ask to chat'}

Requirements:
- MUST be under 300 characters
- No generic "I came across your profile"
- Specific, personalized opening
- Clear but soft CTA
- Professional but human

Output the message only, no explanation."""

    return call_claude(prompt, max_tokens=500, action="linkedin_msg")

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp Source", page_icon="🎣", layout="wide")
init_session()
check_url_auth()

# Styles
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

*, *::before, *::after { font-family: 'Nunito', sans-serif !important; box-sizing: border-box; }

.stApp, [data-testid="stAppViewContainer"] { background: #0a0a0f !important; }
[data-testid="stHeader"] { background: transparent !important; }

section[data-testid="stSidebar"] { background: #0d0d14 !important; border-right: 1px solid rgba(99,102,241,0.2); }
section[data-testid="stSidebar"] > div { background: #0d0d14 !important; }
section[data-testid="stSidebar"] * { color: #e5e5e5 !important; }

section[data-testid="stSidebar"] > div > div:first-child > div:first-child { display: none !important; }

h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
p, span, label, div, li { color: #e5e5e5; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div,
[data-baseweb="select"] > div { background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: #ffffff !important; border-radius: 8px !important; }

[data-baseweb="tag"] { background: rgba(99,102,241,0.3) !important; color: white !important; }

.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stDownloadButton > button { background: #1a1a2e !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 8px; border-bottom: 1px solid rgba(99,102,241,0.2); }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #9ca3af !important; border: none !important; border-bottom: 2px solid transparent; padding: 12px 20px !important; }
.stTabs [aria-selected="true"] { background: transparent !important; color: #fff !important; border-bottom: 2px solid #6366f1 !important; }

.stRadio > div { flex-direction: row !important; gap: 12px; flex-wrap: wrap; }
.stRadio > div > label { background: #12121a !important; padding: 10px 16px !important; border-radius: 8px !important; border: 1px solid rgba(99,102,241,0.2) !important; }

[data-testid="stMetricValue"] { color: #fff !important; }
[data-testid="stMetricLabel"] { color: #9ca3af !important; }

.stSuccess { background: rgba(16,185,129,0.1) !important; border: 1px solid #10b981 !important; }
.stError { background: rgba(239,68,68,0.1) !important; border: 1px solid #ef4444 !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid #f59e0b !important; }
.stInfo { background: rgba(99,102,241,0.1) !important; border: 1px solid #6366f1 !important; }

.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.output-box { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; margin: 16px 0; white-space: pre-wrap; color: #e5e5e5; }
.template-card { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 16px; margin: 8px 0; cursor: pointer; transition: all 0.2s; }
.template-card:hover { border-color: #6366f1; background: rgba(99,102,241,0.1); }
.template-card.selected { border-color: #6366f1; background: rgba(99,102,241,0.15); }
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; z-index: 999; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }

div[data-testid="stPopover"] button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important; border-radius: 25px !important;
    padding: 10px 20px !important; font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}
</style>""", unsafe_allow_html=True)

# Auth
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;">
            <h1 style="margin:0;">Sharp Source</h1>
            <p style="color:#9ca3af;">Boolean Search • Email Sequences • Outreach</p>
        </div>""", unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["Log In", "Sign Up"])
        with t1:
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
        with t2:
            s_email = st.text_input("Email", key="s_email")
            s_pwd = st.text_input("Password", type="password", key="s_pwd")
            s_conf = st.text_input("Confirm", type="password", key="s_conf")
            if st.button("Create Account", use_container_width=True):
                if s_pwd != s_conf: st.error("Passwords don't match")
                elif len(s_pwd) < 6: st.warning("6+ characters")
                elif s_email and s_pwd:
                    r = supabase_sign_up(s_email, s_pwd)
                    st.success(r["message"]) if r["success"] else st.error(r["message"])
    st.stop()

# ============================================
# AUTHENTICATED UI
# ============================================

if st.session_state.working_on:
    st.markdown(f'<div class="status-badge">{st.session_state.working_on}</div>', unsafe_allow_html=True)

# Sidebar with ICONS
with st.sidebar:
    st.markdown(f"""<div class="user-card">
        <p style="color:#9ca3af;margin:0;font-size:12px;">Logged in as</p>
        <p style="color:#fff;margin:4px 0;font-weight:600;">{get_user_email()}</p>
        <p style="color:#6366f1;margin:0;font-size:12px;text-transform:uppercase;">{st.session_state.get('user_plan','free')} plan</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("**Apps**")
    
    apps = [
        ("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"),
        ("interview", "🎯 Interview"), ("source", "🎣 Sourcing"), ("content", "✍️ Content"),
        ("sales", "💰 Sales"), ("reach", "🚀 Reach"), ("assistant", "🤖 Assistant"),
    ]
    
    for key, label in apps:
        if key == "source":
            st.markdown(f"<div style='background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:10px 16px;border-radius:8px;text-align:center;margin:4px 0;color:white;font-weight:600;'>{label} ◀</div>", unsafe_allow_html=True)
        else:
            st.link_button(label, build_app_url(key), use_container_width=True)
    
    if st.session_state.get("is_god"):
        st.markdown("---")
        st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:30px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:50px;">
    <div><h1 style="margin:0;font-size:28px;">Sharp Source</h1><p style="color:#9ca3af;margin:0;">Boolean Search • Email Sequences • Outreach</p></div>
</div>""", unsafe_allow_html=True)

# Tabs
tab_boolean, tab_email, tab_linkedin = st.tabs(["🔍 Boolean Search", "📧 Email Sequences", "💼 LinkedIn Outreach"])

# ============================================
# BOOLEAN SEARCH TAB
# ============================================
with tab_boolean:
    st.markdown("### 🔍 Generate Boolean Search String")
    
    # Load from JD option
    col_load, col_space = st.columns([1, 2])
    with col_load:
        load_src = st.selectbox("📥 Load Requirements", ["Manual Entry", "From Sharp JD", "From Sharp Screen"], key="bool_load")
    
    jd_data = None
    if load_src == "From Sharp JD":
        history = get_jd_history(15)
        if history:
            opts = {f"{j['job_title']} ({j['created_at'][:10]})": j for j in history}
            sel = st.selectbox("Select JD:", list(opts.keys()))
            if sel:
                jd_data = opts[sel]
                st.success(f"✅ Loaded: {jd_data.get('job_title')}")
        else:
            st.info("No JDs found. Create one in Sharp JD first.")
    elif load_src == "From Sharp Screen":
        history = get_screen_history(15)
        if history:
            opts = {f"Screening ({h['created_at'][:10]}) - {h.get('candidates_count', '?')} candidates": h for h in history}
            sel = st.selectbox("Select Screening:", list(opts.keys()))
            if sel:
                jd_data = {"generated_jd": opts[sel].get("job_description", "")}
                st.success("✅ Loaded from screening history")
        else:
            st.info("No screening history found.")
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        job_title = st.text_input("🎯 Job Title *", 
            value=jd_data.get('job_title', '') if jd_data else "",
            placeholder="e.g., Senior Software Engineer, Product Manager")
        
        skills = st.text_area("💻 Required Skills *", height=100,
            placeholder="Enter 3-5 key skills or technologies the candidate must possess, separated by commas.\n\nExample: Python, AWS, Kubernetes, CI/CD, PostgreSQL")
        
        nice_to_have = st.text_area("✨ Nice-to-Have Skills", height=80,
            placeholder="Optional skills that would be a plus, separated by commas.\n\nExample: Terraform, GraphQL, Machine Learning")
    
    with c2:
        experience = st.selectbox("📅 Experience Level", 
            ["Any", "Entry Level (0-2 years)", "Mid Level (3-5 years)", "Senior (5-8 years)", "Staff/Principal (8+ years)", "Executive"])
        
        location = st.text_input("📍 Location", 
            placeholder="e.g., San Francisco Bay Area, Remote US, London UK")
        
        platform = st.selectbox("🔧 Platform Optimization", 
            list(PLATFORM_SYNTAX.keys()),
            format_func=lambda x: PLATFORM_SYNTAX[x]["name"])
        
        # Platform tips
        st.info(f"💡 **Tip:** {PLATFORM_SYNTAX[platform]['tips']}")
    
    if st.button("🔍 Generate Boolean String", type="primary", use_container_width=True):
        if not job_title or not skills:
            st.warning("Please enter job title and required skills")
        else:
            st.session_state.working_on = "Generating Boolean string..."
            result, _ = generate_boolean_string(job_title, skills, experience, location, platform, nice_to_have)
            st.session_state.working_on = None
            if not result.startswith("Error"):
                st.session_state.boolean_result = result
                st.rerun()
            else:
                st.error(result)
    
    if st.session_state.get('boolean_result'):
        st.markdown("---")
        st.markdown("### 📋 Generated Boolean Strings")
        st.markdown(f'<div class="output-box">{st.session_state.boolean_result}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download", st.session_state.boolean_result, 
                f"boolean_{job_title.lower().replace(' ', '_')}.txt", use_container_width=True)
        with c2:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.boolean_result = None
                st.rerun()

# ============================================
# EMAIL SEQUENCES TAB
# ============================================
with tab_email:
    st.markdown("### 📧 Generate Email Sequence")
    
    # Template Library
    st.markdown("#### 📚 Select Template")
    
    template_cols = st.columns(3)
    selected_template = st.session_state.get('selected_template', '3_touch_passive')
    
    for i, (key, template) in enumerate(EMAIL_TEMPLATES.items()):
        with template_cols[i % 3]:
            is_selected = selected_template == key
            border_color = "#6366f1" if is_selected else "rgba(99,102,241,0.2)"
            bg = "rgba(99,102,241,0.15)" if is_selected else "#12121a"
            
            st.markdown(f"""
            <div style="background:{bg};border:2px solid {border_color};border-radius:12px;padding:16px;margin:8px 0;min-height:140px;">
                <p style="color:#fff;font-weight:bold;margin:0 0 8px;">{template['name']}</p>
                <p style="color:#9ca3af;font-size:12px;margin:0 0 8px;">{template['description']}</p>
                <p style="color:#6366f1;font-size:11px;margin:0;">📧 {template['touches']} emails • ⏱️ {template['spacing']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"{'✓ Selected' if is_selected else 'Select'}", key=f"tmpl_{key}", use_container_width=True):
                st.session_state.selected_template = key
                st.rerun()
    
    st.markdown("---")
    
    # Recruiter Info
    st.markdown("#### 👤 Recruiter Information")
    r_cols = st.columns(3)
    with r_cols[0]:
        recruiter_name = st.text_input("Your Name *", placeholder="e.g., Sarah Johnson")
        recruiter_email = st.text_input("Email", placeholder="sarah@company.com")
    with r_cols[1]:
        recruiter_title = st.text_input("Title", placeholder="e.g., Senior Technical Recruiter")
        recruiter_phone = st.text_input("Phone", placeholder="+1 (555) 123-4567")
    with r_cols[2]:
        recruiter_company = st.text_input("Company *", placeholder="e.g., Acme Corp")
        cta_link = st.text_input("📅 Calendar Link (CTA)", placeholder="https://calendly.com/your-link")
    
    st.markdown("---")
    
    # Candidate Info
    st.markdown("#### 🎯 Candidate Information")
    
    cand_cols = st.columns(2)
    with cand_cols[0]:
        candidate_name = st.text_input("Candidate Name *", 
            placeholder="e.g., John Smith (or paste multiple names, one per line)")
        candidate_role = st.text_input("Current Role", placeholder="e.g., Software Engineer at Google")
    with cand_cols[1]:
        candidate_linkedin = st.text_input("LinkedIn URL", 
            placeholder="https://linkedin.com/in/johnsmith")
        candidate_skills = st.text_input("Key Skills/Experience", 
            placeholder="e.g., 5 years Python, AWS certified, Led team of 8")
    
    # Include rationale toggle
    include_rationale = st.checkbox("📊 Include Screening Rationale", 
        help="Reference specific reasons why this candidate was selected from Sharp Screen")
    
    screening_notes = ""
    if include_rationale:
        screening_notes = st.text_area("Screening Notes", height=80,
            placeholder="Why is this candidate a good fit? (e.g., 'Matched 8/10 required skills, has AWS certification we need, salary expectations align')")
    
    st.markdown("---")
    
    # Job Info
    st.markdown("#### 💼 Job Details")
    
    # Load from JD
    job_load = st.radio("Load Job Info:", ["Manual", "From Sharp JD"], horizontal=True, key="job_load")
    
    if job_load == "From Sharp JD":
        history = get_jd_history(10)
        if history:
            opts = {f"{j['job_title']}": j for j in history}
            sel = st.selectbox("Select:", list(opts.keys()), key="job_sel")
            if sel:
                jd = opts[sel]
                job_title_email = jd.get('job_title', '')
                job_company_email = jd.get('company', '')
                st.success(f"✅ Loaded: {job_title_email}")
        else:
            job_title_email = ""
            job_company_email = ""
    else:
        job_title_email = ""
        job_company_email = ""
    
    job_cols = st.columns(3)
    with job_cols[0]:
        job_title_final = st.text_input("Job Title *", value=job_title_email, placeholder="e.g., Senior Backend Engineer")
    with job_cols[1]:
        job_company_final = st.text_input("Company", value=job_company_email, placeholder="e.g., Acme Corp")
    with job_cols[2]:
        job_location = st.text_input("Location", placeholder="e.g., Remote US, NYC Hybrid")
    
    selling_cols = st.columns(2)
    with selling_cols[0]:
        job_selling = st.text_area("🌟 Key Selling Points", height=80,
            placeholder="What makes this role attractive?\n• Cutting-edge tech stack\n• Strong growth trajectory\n• Excellent benefits")
    with selling_cols[1]:
        job_salary = st.text_input("💰 Salary/Comp Range", placeholder="e.g., $180-220K + equity")
    
    if st.button("📧 Generate Email Sequence", type="primary", use_container_width=True):
        if not recruiter_name or not recruiter_company or not candidate_name or not job_title_final:
            st.warning("Please fill in required fields (marked with *)")
        else:
            st.session_state.working_on = "Generating emails..."
            
            recruiter_info = {
                "name": recruiter_name, "title": recruiter_title, "company": recruiter_company,
                "email": recruiter_email, "phone": recruiter_phone
            }
            candidate_info = {
                "name": candidate_name, "current_role": candidate_role,
                "linkedin": candidate_linkedin, "skills": candidate_skills,
                "screening_notes": screening_notes if include_rationale else ""
            }
            job_info = {
                "title": job_title_final, "company": job_company_final or recruiter_company,
                "location": job_location, "selling_points": job_selling, "salary": job_salary
            }
            
            result, _ = generate_email_sequence(
                st.session_state.get('selected_template', '3_touch_passive'),
                recruiter_info, candidate_info, job_info, cta_link, include_rationale
            )
            st.session_state.working_on = None
            
            if not result.startswith("Error"):
                st.session_state.email_sequence = result
                st.rerun()
            else:
                st.error(result)
    
    if st.session_state.get('email_sequence'):
        st.markdown("---")
        st.markdown("### 📬 Generated Email Sequence")
        st.markdown(st.session_state.email_sequence)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download Sequence", st.session_state.email_sequence,
                f"email_sequence_{candidate_name.split()[0].lower() if candidate_name else 'candidate'}.md", use_container_width=True)
        with c2:
            if st.button("🔄 Clear Sequence", use_container_width=True):
                st.session_state.email_sequence = None
                st.rerun()

# ============================================
# LINKEDIN OUTREACH TAB
# ============================================
with tab_linkedin:
    st.markdown("### 💼 LinkedIn Connection Request")
    st.markdown("Generate personalized connection messages (300 character limit)")
    
    c1, c2 = st.columns(2)
    
    with c1:
        li_name = st.text_input("Candidate Name", placeholder="e.g., John Smith", key="li_name")
        li_role = st.text_input("Target Role", placeholder="e.g., Senior Software Engineer", key="li_role")
    
    with c2:
        li_hook = st.selectbox("Outreach Angle", [
            "Their recent post/article",
            "Mutual connection",
            "Shared background (school, company)",
            "Their open source work",
            "Speaking at conference",
            "Industry expertise",
            "Custom hook"
        ], key="li_hook")
        
        if li_hook == "Custom hook":
            li_hook_custom = st.text_input("Custom Hook", placeholder="What's your angle?", key="li_custom")
        else:
            li_hook_custom = li_hook
    
    li_cta = st.text_input("CTA Link (optional)", placeholder="https://calendly.com/...", key="li_cta")
    
    if st.button("💼 Generate LinkedIn Message", type="primary", use_container_width=True):
        if not li_name or not li_role:
            st.warning("Enter candidate name and role")
        else:
            st.session_state.working_on = "Writing message..."
            result, _ = generate_linkedin_message(li_name, li_role, li_hook_custom, li_cta)
            st.session_state.working_on = None
            
            if not result.startswith("Error"):
                char_count = len(result)
                color = "#10b981" if char_count <= 300 else "#ef4444"
                
                st.markdown(f"""
                <div style="background:#12121a;border:1px solid rgba(99,102,241,0.3);border-radius:12px;padding:20px;margin:16px 0;">
                    <p style="color:#9ca3af;font-size:12px;margin:0 0 8px;">MESSAGE ({char_count}/300 characters)</p>
                    <p style="color:#fff;font-size:16px;margin:0;line-height:1.6;">{result}</p>
                    <p style="color:{color};font-size:12px;margin:16px 0 0;text-align:right;">
                        {'✅ Within limit' if char_count <= 300 else '⚠️ Over limit - needs trimming'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.button("📋 Copy to Clipboard", key="copy_li")
            else:
                st.error(result)

# ============================================
# FLOATING FEEDBACK
# ============================================
st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)

_, _, _, fb_col = st.columns([4, 1, 1, 1])
with fb_col:
    with st.popover("💬 Feedback"):
        st.markdown("**Send Feedback**")
        fb_type = st.segmented_control("Type", ["🐛 Bug", "✨ Feature", "💬 General"], 
                                        default="💬 General", label_visibility="collapsed")
        fb_msg = st.text_area("Message", height=100, placeholder="What's on your mind?",
                              label_visibility="collapsed", key="fb_msg")
        if st.button("Send Feedback", type="primary", use_container_width=True, key="fb_send"):
            if fb_msg:
                t = fb_type.split()[1].lower() if fb_type else "general"
                success = submit_feedback("source", t, fb_msg)
                if success:
                    st.success("Thanks! 🙏")
                else:
                    st.error("Failed to send")
