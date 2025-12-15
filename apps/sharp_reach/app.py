"""Sharp Reach - Candidate Engagement & Outreach Platform"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re
import io
import zipfile
from xml.etree import ElementTree

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
GOD_PASSWORD = os.environ.get("GOD_PASSWORD", "G0DHum@n101!!!")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

APP_URLS = {
    "portal": "https://demo.sharphuman.com", "jd": "https://jd.sharphuman.com",
    "screen": "https://screen.sharphuman.com", "interview": "https://hire.sharphuman.com",
    "source": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com",
    "sales": "https://sales.sharphuman.com", "reach": "https://reach.sharphuman.com",
    "assistant": "https://assistant.sharphuman.com", "admin": "https://admin.sharphuman.com"
}

OUTREACH_TEMPLATES = {
    "engagement_strategy": {
        "name": "Engagement Strategy",
        "icon": "📊",
        "desc": "Recommended outreach channel, best time to contact, and highest conversion selling points"
    },
    "video_script": {
        "name": "Why Us Video Script",
        "icon": "🎬",
        "desc": "Quick video message script focusing on culture, team, and why this specific candidate"
    },
    "inmail_sequence": {
        "name": "Source-to-Hire InMail",
        "icon": "💼",
        "desc": "Connection request + follow-up InMail referencing skills or mutual connections"
    },
    "prescreen_script": {
        "name": "Pre-Screen Script",
        "icon": "📞",
        "desc": "Script to confirm CV points and assess cultural fit before formal interview"
    },
    "followup_sequence": {
        "name": "Follow-up Sequence",
        "icon": "📧",
        "desc": "3-email sequence: Initial hook, Value prop, Soft close"
    },
    "cold_outreach": {
        "name": "Cold Outreach",
        "icon": "❄️",
        "desc": "Multi-channel cold outreach (LinkedIn, Email, Phone script)"
    }
}

INDUSTRIES = ["Technology", "Finance", "Healthcare", "Consulting", "Retail", "Manufacturing", "Media", "Legal", "Education", "Government", "Nonprofit", "Other"]
SENIORITY_LEVELS = ["Entry Level", "Mid-Level", "Senior", "Lead/Principal", "Manager", "Director", "VP", "C-Suite"]

# ============================================
# AUTH FUNCTIONS
# ============================================

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "reach",
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
        return {"success": False, "message": data.get("error_description") or "Invalid"}
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
        r = requests.post(f"{SUPABASE_URL}/rest/v1/user_feedback",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": st.session_state.user.get("id") if st.session_state.user else None,
                  "app": app, "feedback_type": feedback_type, "rating": 4, "message": message,
                  "email": get_user_email()}, timeout=10)
        return r.status_code in [200, 201]
    except: return False

def get_jd_history(limit=20):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god": return []
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/jd_history?user_id=eq.{user_id}&order=created_at.desc&limit={limit}",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        return r.json() if r.status_code == 200 else []
    except: return []

def init_session():
    defaults = [
        ('authenticated', False), ('user', None), ('is_god', False), ('session_token', None),
        ('user_plan', 'free'), ('working_on', None), ('generated_content', None),
        ('transcripts_text', '')
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
    if st.session_state.user:
        return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"

def build_app_url(app_name):
    base = APP_URLS.get(app_name, "")
    token = st.session_state.get("session_token", "")
    return f"{base}?auth={token}" if base and token else base

# ============================================
# FILE EXTRACTION
# ============================================

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.name.split('.')[-1].lower()
    content = uploaded_file.read()
    uploaded_file.seek(0)
    
    if file_type == 'txt':
        return content.decode('utf-8', errors='ignore')
    
    elif file_type == 'pdf':
        try:
            import fitz
            pdf = fitz.open(stream=content, filetype="pdf")
            text_parts = []
            for page in pdf:
                text_parts.append(page.get_text())
            pdf.close()
            result = "\n".join(text_parts)
            if result.strip():
                return result
        except: pass
        return "[PDF extraction failed - please paste content]"
    
    elif file_type in ['docx', 'doc']:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            if paragraphs:
                return '\n\n'.join(paragraphs)
        except: pass
        
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                if 'word/document.xml' in z.namelist():
                    xml_content = z.read('word/document.xml')
                    tree = ElementTree.fromstring(xml_content)
                    texts = [elem.text for elem in tree.iter() if elem.text and elem.text.strip()]
                    if texts:
                        return ' '.join(texts)
        except: pass
        return "[DOCX extraction failed - please paste content]"
    
    elif file_type in ['vtt', 'srt']:
        text = content.decode('utf-8', errors='ignore')
        text = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', text)
        text = re.sub(r'WEBVTT.*?\n', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        return '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
    
    return content.decode('utf-8', errors='ignore')

# ============================================
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=4000, action="generate"):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens,
                  "messages": [{"role": "user", "content": prompt}]}, timeout=180)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            if st.session_state.user:
                log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "reach", action, (len(prompt)+len(text))//4)
            return text, (len(prompt)+len(text))//4
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {e}", 0

# ============================================
# CONTENT GENERATION
# ============================================

def generate_engagement_strategy(candidate_info, job_info, company_info, transcripts=""):
    prompt = f"""You are an expert talent acquisition strategist. Create a comprehensive engagement strategy for reaching this candidate.

## CANDIDATE PROFILE
{candidate_info}

## TARGET ROLE
{job_info}

## COMPANY/OPPORTUNITY
{company_info}

{f"## PREVIOUS SALES/RECRUITING CALL INSIGHTS{chr(10)}{transcripts[:5000]}" if transcripts else ""}

---

Create a detailed engagement strategy including:

## 1. RECOMMENDED OUTREACH CHANNEL
Best primary channel (LinkedIn, Email, Phone, Text) with reasoning based on their title/industry

## 2. OPTIMAL CONTACT TIMING
Best days/times to reach out based on their role and industry patterns

## 3. PRIMARY SELLING POINTS
Rank what will resonate most with this specific candidate:
1. Compensation
2. Mission/Impact
3. Growth Opportunity
4. Culture/Team
5. Tech Stack/Tools
6. Flexibility/Remote

## 4. PERSONALIZATION HOOKS
Specific talking points based on their background

## 5. OBJECTION ANTICIPATION
Likely concerns and how to address them

## 6. MULTI-TOUCH STRATEGY
Recommended sequence of touches across channels with timing"""

    return call_claude(prompt, 3000, "engagement_strategy")

def generate_video_script(candidate_info, job_info, company_info, your_name=""):
    prompt = f"""Create a personalized 60-90 second video script for reaching out to this candidate.

## CANDIDATE
{candidate_info}

## ROLE
{job_info}

## COMPANY
{company_info}

## SENDER
{your_name if your_name else "The recruiter"}

---

Write a warm, authentic video script:

## INTRO (10-15 seconds)
[Tone: Warm, Energetic]
- Open with personal hook (reference something specific about them)
- Quick self-intro

## BODY (40-50 seconds)
[Tone: Genuine, Enthusiastic]
- Why YOU specifically are reaching out to THEM
- 2-3 compelling reasons why this opportunity is special
- Quick mention of team/culture

## CLOSE (15-20 seconds)
[Tone: Friendly, No Pressure]
- Soft, low-pressure CTA
- Make it easy to respond

Include [PAUSE] markers and delivery tips throughout."""

    return call_claude(prompt, 2000, "video_script")

def generate_inmail_sequence(candidate_info, job_info, company_info, mutual_connections="", screening_insights=""):
    prompt = f"""Create a LinkedIn InMail sequence for sourcing this candidate.

## CANDIDATE
{candidate_info}

## ROLE
{job_info}

## COMPANY
{company_info}

{f"## MUTUAL CONNECTIONS/SHARED BACKGROUND{chr(10)}{mutual_connections}" if mutual_connections else ""}
{f"## SCREENING/CV INSIGHTS{chr(10)}{screening_insights}" if screening_insights else ""}

---

## 1. CONNECTION REQUEST NOTE
(Max 300 characters - must be compelling!)

## 2. FOLLOW-UP INMAIL #1 
(Send if no response in 3 days - different angle, add value)

## 3. FOLLOW-UP INMAIL #2
(Send if no response in 7 days - final attempt with different hook)

Each message should:
- Be personalized to their specific background
- Reference specific skills/experience
- Have a clear but soft CTA
- Feel human, not templated

Include character/word counts for each."""

    return call_claude(prompt, 2500, "inmail_sequence")

def generate_prescreen_script(candidate_info, job_info, cv_highlights=""):
    prompt = f"""Create a pre-screening call script tailored to this candidate.

## CANDIDATE
{candidate_info}

## ROLE REQUIREMENTS
{job_info}

{f"## CV/BACKGROUND HIGHLIGHTS TO VERIFY{chr(10)}{cv_highlights}" if cv_highlights else ""}

---

Create a 15-20 minute pre-screen script:

## OPENING (2 min)
- Warm intro
- Set expectations for the call
- Confirm their interest/availability

## BACKGROUND VERIFICATION (5 min)
- Questions to verify specific CV claims
- Dig into key experiences mentioned
[Mark MUST-ASK questions with ⭐]

## ROLE FIT ASSESSMENT (5 min)
- Technical/skill alignment questions
- Experience relevance questions
[Mark MUST-ASK questions with ⭐]

## CULTURAL FIT (3 min)
- Work style questions
- Values alignment questions

## LOGISTICS (3 min)
- Compensation expectations
- Notice period/availability
- Location/remote preferences

## CLOSE (2 min)
- Answer their questions
- Explain next steps
- Timeline setting"""

    return call_claude(prompt, 3000, "prescreen_script")

def generate_followup_sequence(candidate_info, job_info, company_info, urgency_level="medium"):
    prompt = f"""Create a 3-email follow-up sequence for a high-priority passive candidate.

## CANDIDATE
{candidate_info}

## ROLE
{job_info}

## COMPANY
{company_info}

## URGENCY LEVEL: {urgency_level.upper()}

---

## EMAIL 1: THE HOOK (Day 0)

**Subject Line Options:**
1. 
2. 
3. 

**Body:** (Under 150 words)
- Personalized opening
- Intriguing value prop
- Soft CTA

---

## EMAIL 2: THE VALUE DEEP-DIVE (Day 3-4)

**Subject Line Options:**
1. 
2. 
3. 

**Body:** (Under 150 words)
- Focus on culture/team/impact
- Social proof or specific wins
- Address likely objections
- Slightly stronger CTA

---

## EMAIL 3: THE SOFT CLOSE (Day 7-10)

**Subject Line Options:**
1. 
2. 
3. 

**Body:** (Under 150 words)
- Create gentle urgency
- Offer alternative (coffee chat, call, etc.)
- Make it easy to say yes
- Leave door open

---

All emails should be mobile-friendly with short paragraphs."""

    return call_claude(prompt, 3000, "followup_sequence")

def generate_cold_outreach(candidate_info, job_info, company_info, channels):
    channel_instructions = []
    if "linkedin" in channels:
        channel_instructions.append("""## LINKEDIN
- Connection request note (Max 300 characters)
- InMail if not connected (Max 300 words)""")
    if "email" in channels:
        channel_instructions.append("""## EMAIL
- Subject line options (3)
- Email body (Under 150 words)""")
    if "phone" in channels:
        channel_instructions.append("""## PHONE
- Voicemail script (30 seconds)
- Live call opening script""")
    if "text" in channels:
        channel_instructions.append("""## TEXT/SMS
- Initial text (Max 160 characters)""")
    
    prompt = f"""Create multi-channel cold outreach for this candidate.

## CANDIDATE
{candidate_info}

## ROLE
{job_info}

## COMPANY
{company_info}

---

Create coordinated outreach for each channel:

{chr(10).join(channel_instructions)}

---

## RECOMMENDED TIMING SEQUENCE
Provide a day-by-day multi-channel approach for optimal response rate."""

    return call_claude(prompt, 3000, "cold_outreach")

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp Reach", page_icon="🚀", layout="wide")
init_session()
check_url_auth()

# Styles
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
*, *::before, *::after { font-family: 'Nunito', sans-serif !important; }
.stApp, [data-testid="stAppViewContainer"] { background: #0a0a0f !important; }
[data-testid="stHeader"] { background: transparent !important; }
section[data-testid="stSidebar"] { background: #0d0d14 !important; border-right: 1px solid rgba(99,102,241,0.2); }
section[data-testid="stSidebar"] > div { background: #0d0d14 !important; }
section[data-testid="stSidebar"] * { color: #e5e5e5 !important; }
section[data-testid="stSidebar"] > div > div:first-child > div:first-child { display: none !important; }
h1,h2,h3,h4,h5,h6 { color: #fff !important; }
p,span,label,div,li { color: #e5e5e5; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div, [data-baseweb="select"] > div {
    background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: #fff !important; border-radius: 8px !important;
}
[data-baseweb="tag"] { background: rgba(99,102,241,0.3) !important; color: white !important; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stDownloadButton > button { background: #1a1a2e !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; }
[data-testid="stFileUploader"] { background: #12121a !important; border: 1px dashed rgba(99,102,241,0.3) !important; border-radius: 8px !important; }
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 8px; border-bottom: 1px solid rgba(99,102,241,0.2); }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #9ca3af !important; }
.stTabs [aria-selected="true"] { color: #fff !important; border-bottom: 2px solid #6366f1 !important; }
.stRadio > div { flex-direction: row !important; gap: 8px; flex-wrap: wrap; }
.stRadio > div > label { background: #12121a !important; padding: 10px 16px !important; border-radius: 8px !important; border: 1px solid rgba(99,102,241,0.2) !important; }
.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.input-card { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; margin: 12px 0; }
.output-box { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 24px; margin: 16px 0; white-space: pre-wrap; }
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; z-index: 999; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
div[data-testid="stPopover"] button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 25px !important; }
</style>""", unsafe_allow_html=True)

# Auth
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;">
            <h1 style="margin:0;">Sharp Reach</h1>
            <p style="color:#9ca3af;">Candidate Engagement Platform</p>
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
                if s_pwd != s_conf:
                    st.error("Passwords don't match")
                elif len(s_pwd) < 6:
                    st.warning("6+ characters")
                elif s_email and s_pwd:
                    r = supabase_sign_up(s_email, s_pwd)
                    st.success(r["message"]) if r["success"] else st.error(r["message"])
    st.stop()

# Status badge
if st.session_state.working_on:
    st.markdown(f'<div class="status-badge">{st.session_state.working_on}</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"""<div class="user-card">
        <p style="color:#9ca3af;margin:0;font-size:12px;">Logged in as</p>
        <p style="color:#fff;margin:4px 0;font-weight:600;">{get_user_email()}</p>
        <p style="color:#6366f1;margin:0;font-size:12px;text-transform:uppercase;">{st.session_state.get('user_plan','free')} plan</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("**Apps**")
    apps = [("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"),
            ("interview", "🎯 Interview"), ("source", "🎣 Sourcing"), ("content", "✍️ Content"),
            ("sales", "💰 Sales"), ("reach", "🚀 Reach"), ("assistant", "🤖 Assistant")]
    for key, label in apps:
        if key == "reach":
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
    <div>
        <h1 style="margin:0;font-size:28px;">Sharp Reach</h1>
        <p style="color:#9ca3af;margin:0;">AI-Powered Candidate Engagement</p>
    </div>
</div>""", unsafe_allow_html=True)

# Main Content
col_input, col_output = st.columns([1, 1])

with col_input:
    st.markdown("### 👤 Candidate Profile")
    
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        candidate_name = st.text_input("Candidate Name", placeholder="Sarah Chen")
        current_title = st.text_input("Current Title", placeholder="Senior Software Engineer")
        current_company = st.text_input("Current Company", placeholder="Google")
    with c2:
        industry = st.selectbox("Industry", INDUSTRIES)
        seniority = st.selectbox("Seniority Level", SENIORITY_LEVELS, index=2)
        years_exp = st.slider("Years of Experience", 0, 30, 5)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎯 Target Role")
    
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    jd_source = st.radio("Job Description:", ["📝 Enter Details", "📜 Import from JD History"], horizontal=True)
    
    target_title = ""
    target_skills = ""
    
    if jd_source == "📜 Import from JD History":
        history = get_jd_history(20)
        if history:
            opts = {f"{j['job_title']} ({j['created_at'][:10]})": j for j in history}
            selected_jd = st.selectbox("Select JD:", list(opts.keys()))
            if selected_jd:
                jd_data = opts[selected_jd]
                target_title = jd_data.get('job_title', '')
                target_skills = jd_data.get('requirements', '') or jd_data.get('generated_jd', '')[:500]
                st.success(f"Loaded: {jd_data.get('job_title')}")
        else:
            st.info("No saved JDs found")
            target_title = st.text_input("Target Job Title", placeholder="Staff Software Engineer")
            target_skills = st.text_area("Key Skills/Requirements", height=80, placeholder="5+ years Kubernetes, AWS, Go...")
    else:
        target_title = st.text_input("Target Job Title", placeholder="Staff Software Engineer")
        target_skills = st.text_area("Key Skills/Requirements", height=80, placeholder="5+ years Kubernetes, AWS, Go...")
    
    compensation = st.text_input("Compensation Highlights", placeholder="$180-220k, 100% remote, unlimited PTO, equity...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏢 Company/Opportunity")
    
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    company_name = st.text_input("Your Company", placeholder="Acme Corp")
    company_pitch = st.text_area("Company Value Prop / Culture", height=80, placeholder="Series B startup, mission-driven team, fast growth...")
    your_name = st.text_input("Your Name (Recruiter)", placeholder="Alex Johnson")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Previous transcripts
    with st.expander("📞 Previous Call Transcripts (Optional)"):
        st.caption("Upload previous recruiting/sales calls to inform the outreach strategy")
        trans_method = st.radio("Input:", ["📝 Paste", "📁 Upload Files"], horizontal=True, key="trans_method")
        
        transcripts_text = ""
        if trans_method == "📝 Paste":
            transcripts_text = st.text_area("Paste transcripts:", height=150, placeholder="Paste any previous call notes or transcripts here...")
        else:
            trans_files = st.file_uploader("Upload transcripts", type=['txt', 'pdf', 'docx', 'vtt', 'srt'], accept_multiple_files=True)
            if trans_files:
                all_texts = []
                for f in trans_files:
                    text = extract_text_from_file(f)
                    if text and not text.startswith("["):
                        all_texts.append(f"--- {f.name} ---\n{text}")
                        st.success(f"✅ {f.name}")
                    else:
                        st.warning(f"⚠️ {f.name}: {text}")
                transcripts_text = "\n\n".join(all_texts)
                if transcripts_text:
                    st.info(f"Loaded {len(all_texts)} transcript(s)")

with col_output:
    st.markdown("### 📝 Generate Outreach")
    
    # Template selection with cards
    st.markdown("**Select Template:**")
    template_cols = st.columns(3)
    template_keys = list(OUTREACH_TEMPLATES.keys())
    
    if 'selected_template' not in st.session_state:
        st.session_state.selected_template = template_keys[0]
    
    for i, key in enumerate(template_keys):
        with template_cols[i % 3]:
            tpl = OUTREACH_TEMPLATES[key]
            is_selected = st.session_state.selected_template == key
            btn_style = "primary" if is_selected else "secondary"
            if st.button(f"{tpl['icon']} {tpl['name']}", key=f"tpl_{key}", use_container_width=True, type=btn_style):
                st.session_state.selected_template = key
                st.session_state.generated_content = None
                st.rerun()
    
    template_type = st.session_state.selected_template
    st.caption(f"*{OUTREACH_TEMPLATES[template_type]['desc']}*")
    
    st.markdown("---")
    
    # Additional options based on template
    mutual_connections = ""
    screening_insights = ""
    cv_highlights = ""
    urgency_level = "medium"
    channels = ["linkedin", "email"]
    
    if template_type == "inmail_sequence":
        mutual_connections = st.text_input("Mutual Connections/Shared Background", placeholder="Both worked at Stripe, same university...")
        screening_insights = st.text_area("Screening/CV Insights", height=60, placeholder="Strong Python skills, led team of 5...")
    elif template_type == "prescreen_script":
        cv_highlights = st.text_area("CV Points to Verify", height=80, placeholder="Claims 'led migration to K8s' - probe on specifics...")
    elif template_type == "followup_sequence":
        urgency_level = st.select_slider("Urgency Level", options=["low", "medium", "high"], value="medium")
    elif template_type == "cold_outreach":
        channels = st.multiselect("Channels", ["linkedin", "email", "phone", "text"], default=["linkedin", "email"])
    
    # Generate button
    if st.button("🚀 Generate Outreach", type="primary", use_container_width=True):
        # Build info strings
        candidate_info = f"""Name: {candidate_name or 'Unknown'}
Current Title: {current_title or 'Unknown'}
Current Company: {current_company or 'Unknown'}
Industry: {industry}
Seniority: {seniority}
Years of Experience: {years_exp}"""
        
        job_info = f"""Target Title: {target_title or 'Not specified'}
Key Skills/Requirements: {target_skills or 'Not specified'}
Compensation: {compensation or 'Not specified'}"""
        
        company_info = f"""Company: {company_name or 'Not specified'}
Value Prop/Culture: {company_pitch or 'Not specified'}
Recruiter: {your_name or 'Not specified'}"""
        
        st.session_state.working_on = f"Generating {OUTREACH_TEMPLATES[template_type]['name']}..."
        
        # Generate based on template type
        if template_type == "engagement_strategy":
            result, _ = generate_engagement_strategy(candidate_info, job_info, company_info, transcripts_text)
        elif template_type == "video_script":
            result, _ = generate_video_script(candidate_info, job_info, company_info, your_name)
        elif template_type == "inmail_sequence":
            result, _ = generate_inmail_sequence(candidate_info, job_info, company_info, mutual_connections, screening_insights)
        elif template_type == "prescreen_script":
            result, _ = generate_prescreen_script(candidate_info, job_info, cv_highlights)
        elif template_type == "followup_sequence":
            result, _ = generate_followup_sequence(candidate_info, job_info, company_info, urgency_level)
        elif template_type == "cold_outreach":
            result, _ = generate_cold_outreach(candidate_info, job_info, company_info, channels)
        else:
            result = "Template not implemented"
        
        st.session_state.working_on = None
        st.session_state.generated_content = result
        st.rerun()
    
    # Display results
    if st.session_state.generated_content:
        st.markdown("### 📄 Generated Content")
        
        result = st.session_state.generated_content
        
        if not str(result).startswith("Error"):
            st.markdown(result)
            
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("📥 Download TXT", result, f"outreach_{template_type}.txt", use_container_width=True)
            with col2:
                st.download_button("📥 Download MD", result, f"outreach_{template_type}.md", use_container_width=True)
            with col3:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.generated_content = None
                    st.rerun()
        else:
            st.error(result)

# Feedback
st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)
_, _, _, fb = st.columns([4, 1, 1, 1])
with fb:
    with st.popover("💬 Feedback"):
        st.markdown("**Send Feedback**")
        ft = st.segmented_control("Type", ["🐛 Bug", "✨ Feature", "💬 General"], default="💬 General", label_visibility="collapsed")
        fm = st.text_area("Message", height=100, placeholder="Your feedback...", label_visibility="collapsed", key="fb_msg")
        if st.button("Send", type="primary", use_container_width=True, key="fb_send"):
            if fm:
                fb_type = ft.split()[1].lower() if ft else "general"
                if submit_feedback("reach", fb_type, fm):
                    st.success("Thanks! 🙏")
                else:
                    st.error("Failed")
