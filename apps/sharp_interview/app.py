"""Sharp Interview - Questions, Analysis & Scorecards with Cross-App Auth"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re
import io

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

# ============================================
# AUTH FUNCTIONS
# ============================================

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "interview",
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
    """Submit feedback to database"""
    try:
        user_id = st.session_state.user.get("id") if st.session_state.user else None
        email = st.session_state.user.get("email", "") if st.session_state.user else ""
        
        payload = {
            "user_id": user_id,
            "app": app,
            "feedback_type": feedback_type,
            "rating": 4,
            "message": message,
            "email": email
        }
        
        r = requests.post(f"{SUPABASE_URL}/rest/v1/user_feedback",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json=payload, timeout=10)
        return r.status_code in [200, 201]
    except Exception as e:
        print(f"Feedback error: {e}")
        return False

def init_session():
    defaults = [
        ('authenticated', False), ('user', None), ('is_god', False), ('session_token', None),
        ('user_plan', 'free'), ('generated_questions', None), ('analysis_result', None),
        ('scorecard_result', None), ('working_on', None), ('jd_text', ''), ('cv_text', ''),
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

# ============================================
# FILE PROCESSING
# ============================================

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()
    content = uploaded_file.read()
    uploaded_file.seek(0)
    
    if file_type == 'txt':
        return content.decode('utf-8', errors='ignore')
    elif file_type in ['vtt', 'srt']:
        # Parse transcript formats
        text = content.decode('utf-8', errors='ignore')
        # Remove timestamps and formatting
        text = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', text)
        text = re.sub(r'WEBVTT\n', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    elif file_type == 'pdf':
        try:
            import fitz
            pdf = fitz.open(stream=content, filetype="pdf")
            return "".join([page.get_text() for page in pdf])
        except:
            return content.decode('utf-8', errors='ignore')
    elif file_type in ['docx', 'doc']:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return '\n'.join([p.text for p in doc.paragraphs])
        except:
            return "[DOCX requires python-docx]"
    return content.decode('utf-8', errors='ignore')

# ============================================
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=4000, action="interview"):
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
                log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "interview", action, tokens)
            return text, tokens
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0

# ============================================
# INTERVIEW FUNCTIONS
# ============================================

def generate_questions(job_title, requirements, stage, duration, focus_areas, cv_text="", exclude_illegal=True):
    cv_section = f"""
## CANDIDATE CV (Generate 3+ CV-specific questions based on this):
{cv_text}
""" if cv_text else ""
    
    illegal_note = """
## IMPORTANT - LEGAL COMPLIANCE:
Do NOT include questions about: age, marital status, family planning, religion, nationality/citizenship, disabilities, pregnancy, political affiliation, genetic information, or arrest records.
Focus ONLY on job-relevant qualifications and experience.
""" if exclude_illegal else ""
    
    prompt = f"""Generate interview questions for this role:

## JOB DETAILS:
- Title: {job_title}
- Stage: {stage}
- Duration: {duration} minutes
- Focus Areas: {', '.join(focus_areas) if focus_areas else 'General'}

## REQUIREMENTS:
{requirements}
{cv_section}
{illegal_note}

## OUTPUT FORMAT:
For each question, provide:
1. The question
2. What it assesses (skill/competency)
3. What a good answer looks like
4. Follow-up probe question

Generate {duration // 5} questions appropriate for a {duration}-minute {stage} interview.
{"Include at least 3 questions that reference specific items from the candidate's CV." if cv_text else ""}

Format as markdown with clear sections."""

    return call_claude(prompt, max_tokens=3000, action="generate_questions")

def analyze_transcript(transcript, jd_text, cv_text=""):
    prompt = f"""Analyze this interview transcript against the job requirements:

## JOB DESCRIPTION:
{jd_text}

{"## CANDIDATE CV:" + chr(10) + cv_text if cv_text else ""}

## INTERVIEW TRANSCRIPT:
{transcript}

## PROVIDE ANALYSIS:

### 1. KEY THEMES
What main topics were discussed? How well did they align with job requirements?

### 2. STRENGTHS DEMONSTRATED
What competencies did the candidate demonstrate well? Provide specific quotes.

### 3. CONCERNS / RED FLAGS
What areas need follow-up? Any inconsistencies or gaps?

### 4. TALK TIME RATIO
Estimate interviewer vs candidate talk time. Was the candidate engaged?

### 5. COMMUNICATION ASSESSMENT
Rate clarity, structure, and professionalism of responses.

### 6. TECHNICAL DEPTH
Did answers demonstrate required expertise level?

### 7. CULTURAL FIT INDICATORS
Any signals about work style, values, or team fit?

### 8. RECOMMENDED FOLLOW-UP QUESTIONS
Based on gaps in the interview, what should be asked next?

Be specific and cite quotes from the transcript where relevant."""

    return call_claude(prompt, max_tokens=4000, action="analyze_transcript")

def generate_scorecard(transcript, jd_text, cv_text, focus_areas):
    prompt = f"""Generate an objective interview scorecard based on this transcript.

## JOB DESCRIPTION:
{jd_text}

## CANDIDATE CV:
{cv_text}

## FOCUS AREAS TO SCORE:
{', '.join(focus_areas) if focus_areas else 'Technical Skills, Communication, Problem Solving, Cultural Fit, Leadership'}

## INTERVIEW TRANSCRIPT:
{transcript}

## GENERATE SCORECARD:

For EACH focus area, provide:

### [FOCUS AREA NAME]
**Score: X/5** ⭐⭐⭐⭐⭐ (show filled stars)

**Evidence:**
> "[Direct quote from transcript supporting this score]"

**Assessment:** [2-3 sentence explanation of score]

---

After all focus areas:

## OVERALL ASSESSMENT

**Total Score:** X/25 (or X/[total possible])

**AI Recommendation:** [Strong Hire | Hire | On the Fence | Lean No | No Hire]

**Confidence Level:** [High | Medium | Low]

**Reasoning:** [2-3 sentences explaining recommendation]

**Suggested Next Steps:**
- [Action 1]
- [Action 2]

**Risk Factors:**
- [Any concerns to address]

Be objective. Base scores ONLY on evidence from the transcript."""

    return call_claude(prompt, max_tokens=4000, action="generate_scorecard")

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp Interview", page_icon="🎯", layout="wide")
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

/* Hide orphaned text */
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

.stCheckbox > label { color: #e5e5e5 !important; }

[data-testid="stFileUploader"] { background: #12121a !important; border: 1px dashed rgba(99,102,241,0.3) !important; border-radius: 8px !important; padding: 20px !important; }

[data-baseweb="popover"], [data-baseweb="menu"] { background: #12121a !important; }
[role="option"] { color: #e5e5e5 !important; }
[role="option"]:hover { background: rgba(99,102,241,0.2) !important; }

.stSlider > div > div { background: rgba(99,102,241,0.3) !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] { background: #6366f1 !important; }

[data-testid="stMetricValue"] { color: #fff !important; }
[data-testid="stMetricLabel"] { color: #9ca3af !important; }

.stSuccess { background: rgba(16,185,129,0.1) !important; border: 1px solid #10b981 !important; }
.stError { background: rgba(239,68,68,0.1) !important; border: 1px solid #ef4444 !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid #f59e0b !important; }
.stInfo { background: rgba(99,102,241,0.1) !important; border: 1px solid #6366f1 !important; }

.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.output-box { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; margin: 16px 0; white-space: pre-wrap; color: #e5e5e5; }
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; z-index: 999; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
</style>""", unsafe_allow_html=True)

# Auth
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;">
            <h1 style="margin:0;">Sharp Interview</h1>
            <p style="color:#9ca3af;">Questions • Analysis • Scorecards</p>
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
        if key == "interview":
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
    <div><h1 style="margin:0;font-size:28px;">Sharp Interview</h1><p style="color:#9ca3af;margin:0;">Questions • Analysis • Scorecards</p></div>
</div>""", unsafe_allow_html=True)

# Tabs
tab_questions, tab_analyze, tab_scorecard = st.tabs(["❓ Generate Questions", "📊 Analyze Interview", "📋 Scorecard"])

with tab_questions:
    st.markdown("### 🎯 Generate Interview Questions")
    
    c1, c2 = st.columns(2)
    
    with c1:
        job_title = st.text_input("Job Title *", placeholder="e.g. Senior Software Engineer")
        
        # JD Source
        jd_src = st.radio("JD Source:", ["📝 Type/Paste", "📜 From History", "📄 Upload"], horizontal=True, key="q_jd_src")
        
        if jd_src == "📜 From History":
            history = get_jd_history(15)
            if history:
                opts = {f"{j['job_title']} ({j['created_at'][:10]})": j for j in history}
                sel = st.selectbox("Select JD:", list(opts.keys()))
                if sel:
                    st.session_state.jd_text = opts[sel].get('generated_jd', '')
                    st.success(f"✅ Loaded: {opts[sel].get('job_title')}")
            else:
                st.info("No saved JDs. Create one in Sharp JD first.")
        elif jd_src == "📄 Upload":
            f = st.file_uploader("Upload JD", type=['pdf', 'docx', 'txt'], key="q_jd_file")
            if f:
                st.session_state.jd_text = extract_text_from_file(f)
                st.success(f"✅ Loaded {f.name}")
        
        requirements = st.text_area("Job Requirements:", value=st.session_state.get('jd_text', ''), height=150,
            placeholder="Key requirements, responsibilities, and qualifications...")
    
    with c2:
        stage = st.selectbox("Interview Stage", ["Phone Screen", "Technical Round", "Hiring Manager", "Final Round", "Culture Fit", "Panel Interview"])
        duration = st.slider("Duration (minutes)", 15, 90, 45, 5)
        
        focus_areas = st.multiselect("Focus Areas", 
            ["Technical Skills", "Problem Solving", "Communication", "Leadership", "Cultural Fit", 
             "Project Experience", "System Design", "Behavioral", "Situational"],
            default=["Technical Skills", "Communication"])
        
        exclude_illegal = st.checkbox("🛡️ Exclude Illegal Questions", value=True, 
            help="Prevents questions about age, religion, family status, etc.")
    
    # Optional CV for bespoke questions
    st.markdown("---")
    st.markdown("### 👤 Optional: Add Candidate CV for Bespoke Questions")
    cv_src = st.radio("CV Source:", ["❌ Skip", "📝 Paste", "📄 Upload"], horizontal=True, key="q_cv_src")
    
    cv_text = ""
    if cv_src == "📝 Paste":
        cv_text = st.text_area("Paste candidate CV:", height=150)
    elif cv_src == "📄 Upload":
        cv_file = st.file_uploader("Upload CV", type=['pdf', 'docx', 'txt'], key="q_cv_file")
        if cv_file:
            cv_text = extract_text_from_file(cv_file)
            st.success(f"✅ Loaded {cv_file.name}")
    
    if st.button("🎯 Generate Questions", type="primary", use_container_width=True):
        if not job_title:
            st.warning("Enter a job title")
        elif not requirements:
            st.warning("Enter job requirements")
        else:
            st.session_state.working_on = "Generating questions..."
            with st.spinner("Creating questions..."):
                result, _ = generate_questions(job_title, requirements, stage, duration, focus_areas, cv_text, exclude_illegal)
                st.session_state.working_on = None
                if not result.startswith("Error"):
                    st.session_state.generated_questions = result
                    st.rerun()
                else:
                    st.error(result)
    
    if st.session_state.get('generated_questions'):
        st.markdown("---")
        st.markdown("### 📝 Generated Questions")
        st.markdown(st.session_state.generated_questions)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download Questions", st.session_state.generated_questions, 
                f"interview_questions_{job_title.lower().replace(' ', '_')}.md", "text/markdown", use_container_width=True)
        with c2:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.generated_questions = None
                st.rerun()

with tab_analyze:
    st.markdown("### 📊 Analyze Interview Transcript")
    st.markdown("Upload or paste an interview transcript for AI analysis.")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**📄 Job Description**")
        a_jd_src = st.radio("JD:", ["📝 Paste", "📜 History", "📄 Upload"], horizontal=True, key="a_jd_src")
        
        if a_jd_src == "📜 History":
            history = get_jd_history(15)
            if history:
                opts = {f"{j['job_title']}": j.get('generated_jd', '') for j in history}
                sel = st.selectbox("Select:", list(opts.keys()), key="a_jd_sel")
                a_jd_text = opts.get(sel, "")
            else:
                a_jd_text = st.text_area("JD:", height=120, key="a_jd_text_input")
        elif a_jd_src == "📄 Upload":
            f = st.file_uploader("Upload JD", type=['pdf', 'docx', 'txt'], key="a_jd_file")
            a_jd_text = extract_text_from_file(f) if f else ""
        else:
            a_jd_text = st.text_area("Job Description:", height=120, placeholder="Paste JD here...")
    
    with c2:
        st.markdown("**👤 Candidate CV (Optional)**")
        a_cv_src = st.radio("CV:", ["❌ Skip", "📝 Paste", "📄 Upload"], horizontal=True, key="a_cv_src")
        
        if a_cv_src == "📝 Paste":
            a_cv_text = st.text_area("CV:", height=120, key="a_cv_paste")
        elif a_cv_src == "📄 Upload":
            f = st.file_uploader("Upload CV", type=['pdf', 'docx', 'txt'], key="a_cv_file")
            a_cv_text = extract_text_from_file(f) if f else ""
        else:
            a_cv_text = ""
    
    st.markdown("---")
    st.markdown("**🎤 Interview Transcript**")
    t_src = st.radio("Transcript:", ["📝 Paste", "📄 Upload (TXT/VTT/SRT)"], horizontal=True, key="t_src")
    
    if t_src == "📄 Upload (TXT/VTT/SRT)":
        t_file = st.file_uploader("Upload Transcript", type=['txt', 'vtt', 'srt'], key="t_file")
        transcript = extract_text_from_file(t_file) if t_file else ""
        if transcript:
            st.success(f"✅ Loaded {len(transcript)} characters")
    else:
        transcript = st.text_area("Paste transcript:", height=200, 
            placeholder="Interviewer: Tell me about yourself...\nCandidate: ...")
    
    if st.button("📊 Analyze Transcript", type="primary", use_container_width=True):
        if not transcript:
            st.warning("Provide a transcript")
        elif not a_jd_text:
            st.warning("Provide a job description")
        else:
            st.session_state.working_on = "Analyzing..."
            with st.spinner("Analyzing transcript..."):
                result, _ = analyze_transcript(transcript, a_jd_text, a_cv_text)
                st.session_state.working_on = None
                if not result.startswith("Error"):
                    st.session_state.analysis_result = result
                    st.rerun()
                else:
                    st.error(result)
    
    if st.session_state.get('analysis_result'):
        st.markdown("---")
        st.markdown("### 📈 Analysis Results")
        st.markdown(st.session_state.analysis_result)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download Analysis", st.session_state.analysis_result, 
                "interview_analysis.md", "text/markdown", use_container_width=True)
        with c2:
            if st.button("🔄 Clear Analysis", use_container_width=True):
                st.session_state.analysis_result = None
                st.rerun()

with tab_scorecard:
    st.markdown("### 📋 Generate Interview Scorecard")
    st.markdown("Create an objective scorecard based on transcript, JD, and CV.")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**📄 Job Description**")
        s_jd_src = st.radio("JD:", ["📝 Paste", "📜 History"], horizontal=True, key="s_jd_src")
        
        if s_jd_src == "📜 History":
            history = get_jd_history(15)
            if history:
                opts = {f"{j['job_title']}": j.get('generated_jd', '') for j in history}
                sel = st.selectbox("Select:", list(opts.keys()), key="s_jd_sel")
                s_jd_text = opts.get(sel, "")
            else:
                s_jd_text = st.text_area("JD:", height=100, key="s_jd_text")
        else:
            s_jd_text = st.text_area("Job Description:", height=100, key="s_jd_paste")
        
        st.markdown("**👤 Candidate CV**")
        s_cv_text = st.text_area("CV:", height=100, placeholder="Paste candidate CV...")
    
    with c2:
        st.markdown("**🎤 Interview Transcript**")
        s_transcript = st.text_area("Transcript:", height=150, placeholder="Full interview transcript...")
        
        st.markdown("**🎯 Focus Areas to Score**")
        s_focus = st.multiselect("Select areas:", 
            ["Technical Skills", "Problem Solving", "Communication", "Leadership", "Cultural Fit", 
             "Domain Knowledge", "Initiative", "Teamwork"],
            default=["Technical Skills", "Communication", "Problem Solving", "Cultural Fit"],
            key="s_focus")
    
    if st.button("📋 Generate Scorecard", type="primary", use_container_width=True):
        if not s_transcript:
            st.warning("Provide a transcript")
        elif not s_jd_text:
            st.warning("Provide a job description")
        elif not s_cv_text:
            st.warning("Provide candidate CV")
        else:
            st.session_state.working_on = "Generating scorecard..."
            with st.spinner("Creating scorecard..."):
                result, _ = generate_scorecard(s_transcript, s_jd_text, s_cv_text, s_focus)
                st.session_state.working_on = None
                if not result.startswith("Error"):
                    st.session_state.scorecard_result = result
                    st.rerun()
                else:
                    st.error(result)
    
    if st.session_state.get('scorecard_result'):
        st.markdown("---")
        st.markdown("### 📊 Interview Scorecard")
        st.markdown(st.session_state.scorecard_result)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download Scorecard", st.session_state.scorecard_result, 
                "interview_scorecard.md", "text/markdown", use_container_width=True)
        with c2:
            if st.button("🔄 Clear Scorecard", use_container_width=True):
                st.session_state.scorecard_result = None
                st.rerun()

# ============================================
# FLOATING FEEDBACK (Bottom of page)
# ============================================
st.markdown("---")
with st.container():
    fb_col1, fb_col2, fb_col3 = st.columns([2, 1, 1])
    with fb_col3:
        if st.checkbox("💬 Feedback", key="show_fb"):
            fb_type = st.selectbox("Type", ["Bug", "Feature", "General"], key="fb_type")
            fb_msg = st.text_area("Message", height=80, key="fb_msg", placeholder="Your feedback...")
            if st.button("Submit Feedback", key="fb_submit"):
                if fb_msg:
                    success = submit_feedback("interview", fb_type.lower(), fb_msg)
                    if success:
                        st.success("Thanks for your feedback! 🙏")
                    else:
                        st.error("Failed to submit. Please try again.")
                else:
                    st.warning("Please enter a message")
