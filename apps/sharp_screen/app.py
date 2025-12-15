"""Sharp Screen - Advanced CV Screening with Cross-App Auth"""
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
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

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

def create_session(user_id, email):
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
                "device_hash": "screen",
                "is_active": True,
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
            },
            timeout=10
        )
        if r.status_code in [200, 201]:
            return token
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

def validate_session_token(token):
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
                expires = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
                if expires.replace(tzinfo=None) > datetime.utcnow():
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
    defaults = [
        ('authenticated', False),
        ('user', None),
        ('is_god', False),
        ('session_token', None),
        ('user_plan', 'free'),
        ('screening_results', None),
        ('working_on', None),
        ('anonymized_result', None),
        ('show_jd_preview', False),
        ('show_cv_preview', False),
        ('show_feedback', False),
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
    base_url = APP_URLS.get(app_name, "")
    token = st.session_state.get("session_token", "")
    if base_url and token:
        return f"{base_url}?auth={token}"
    return base_url

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_jd_history(limit=50):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god":
        return []
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/jd_history?user_id=eq.{user_id}&order=created_at.desc&limit={limit}",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_ANON_KEY}"},
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def save_screen_history(jd_id, jd_text, candidates_input, result, candidates_count, tokens_used):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god":
        return None
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/screen_history",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json={
                "user_id": user_id,
                "jd_history_id": jd_id,
                "job_description": jd_text[:5000] if jd_text else None,
                "candidates_input": candidates_input[:5000] if candidates_input else None,
                "screening_result": result,
                "candidates_count": candidates_count,
                "tokens_used": tokens_used
            },
            timeout=10
        )
        if r.status_code in [200, 201]:
            return r.json()[0] if r.json() else None
    except:
        pass
    return None

def submit_feedback(app, feedback_type, rating, message):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    email = get_user_email()
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/user_feedback",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "user_id": user_id,
                "app": app,
                "feedback_type": feedback_type,
                "rating": rating,
                "message": message,
                "email": email
            },
            timeout=5
        )
        return True
    except:
        return False

# ============================================
# FILE PROCESSING
# ============================================

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()
    content = uploaded_file.read()
    uploaded_file.seek(0)
    
    if file_type == 'txt':
        return content.decode('utf-8', errors='ignore')
    
    elif file_type == 'pdf':
        try:
            import fitz
            pdf = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in pdf:
                text += page.get_text()
            return text
        except ImportError:
            text = content.decode('utf-8', errors='ignore')
            return re.sub(r'[^\x20-\x7E\n]', ' ', text)
    
    elif file_type in ['docx', 'doc']:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return '\n'.join([para.text for para in doc.paragraphs])
        except ImportError:
            return "[DOCX parsing requires python-docx]"
    
    elif file_type == 'json':
        try:
            data = json.loads(content.decode('utf-8'))
            if isinstance(data, list):
                return '\n---\n'.join([json.dumps(item, indent=2) for item in data])
            return json.dumps(data, indent=2)
        except:
            return content.decode('utf-8', errors='ignore')
    
    return content.decode('utf-8', errors='ignore')

def parse_json_candidates(json_text):
    try:
        data = json.loads(json_text)
        candidates = []
        if isinstance(data, list):
            for item in data:
                candidate = {
                    'name': item.get('name') or item.get('candidateName') or item.get('full_name', 'Unknown'),
                    'email': item.get('email') or item.get('emailAddress', ''),
                    'skills': item.get('skills') or item.get('skillSet', []),
                    'summary': item.get('summary') or item.get('professionalSummary', ''),
                }
                candidates.append(candidate)
        elif isinstance(data, dict):
            if 'candidates' in data:
                return parse_json_candidates(json.dumps(data['candidates']))
            candidates.append(data)
        return candidates
    except:
        return None

# ============================================
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=4000, action="screen"):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", 
                          headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, 
                          json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, 
                          timeout=180)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            tokens_used = (len(prompt) + len(text)) // 4
            if st.session_state.user:
                log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "screen", action, tokens_used)
            return text, tokens_used
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0

# ============================================
# SCREENING FUNCTIONS
# ============================================

def screen_candidates(jd_text, cvs_text, options):
    prompt = f"""You are an expert technical recruiter. Analyze these candidates against the job description.

## JOB DESCRIPTION:
{jd_text}

## CANDIDATES (separated by ---):
{cvs_text}

## OPTIONS:
- Bias-Free Mode: {options.get('bias_free', True)}
- AI Detection: {options.get('ai_detection', True)}
- Salary Estimate: {options.get('salary_estimate', True)}

## OUTPUT (JSON):
```json
{{
    "screening_summary": {{
        "total_candidates": <number>,
        "recommended_for_interview": <number>,
        "maybe": <number>,
        "not_recommended": <number>,
        "time_saved_minutes": <number>
    }},
    "candidates": [
        {{
            "rank": <number>,
            "identifier": "<name or Candidate A/B/C>",
            "match_score": <0-100>,
            "required_skills_match": "<X/Y>",
            "preferred_skills_match": "<X/Y>",
            "experience_years": <number>,
            "why_this_score": "<2-3 sentences>",
            "strengths": ["<str1>", "<str2>"],
            "concerns": ["<concern1>"],
            "ai_written_probability": <0-100>,
            "estimated_salary_range": "<$X-$Y>",
            "recommended_action": "<Phone Screen | Technical Test | Reject>",
            "next_steps": "<specific steps>"
        }}
    ],
    "batch_insights": {{
        "strongest_candidate_summary": "<summary>",
        "common_gaps": ["<gap1>"],
        "hiring_recommendation": "<recommendation>"
    }}
}}
```"""
    return call_claude(prompt, max_tokens=4000, action="screen_batch")

def anonymize_cv(cv_text, options):
    prompt = f"""Anonymize this CV by removing identifying information.

## CV:
{cv_text}

## REQUIREMENTS:
1. Remove names, emails, phones, addresses, LinkedIn URLs
2. {"Convert dates to relative time" if options.get('time_based') else "Keep dates, remove birth dates"}
3. Replace universities with "[Tier 1/2/3 University]"
4. Replace companies with "[Fortune 500 Tech]", "[Startup]", etc.

## OUTPUT (JSON):
```json
{{
    "anonymized_cv": "<anonymized text>",
    "items_removed": {{
        "names": [],
        "emails": [],
        "phones": [],
        "universities": [],
        "companies": []
    }},
    "anonymization_score": <0-100>
}}
```"""
    return call_claude(prompt, max_tokens=3000, action="anonymize")

def estimate_salary(cv_text, jd_text, location):
    prompt = f"""Estimate salary for this candidate.

## JOB: {jd_text[:2000]}
## CV: {cv_text[:3000]}
## LOCATION: {location}

## OUTPUT (JSON):
```json
{{
    "estimated_range": {{"low": <num>, "mid": <num>, "high": <num>}},
    "confidence": "<Low|Medium|High>",
    "factors_increasing": ["<factor>"],
    "factors_decreasing": ["<factor>"],
    "market_context": "<context>",
    "negotiation_advice": "<advice>"
}}
```"""
    return call_claude(prompt, max_tokens=1500, action="salary")

# ============================================
# REPORT GENERATION
# ============================================

def generate_csv_report(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        candidates = data.get('candidates', [])
        lines = ["Rank,Identifier,Score,Required,Preferred,Experience,AI%,Salary,Action,Why"]
        for c in candidates:
            lines.append(f"{c.get('rank','')},{c.get('identifier','')},{c.get('match_score','')},{c.get('required_skills_match','')},{c.get('preferred_skills_match','')},{c.get('experience_years','')},{c.get('ai_written_probability','')},{c.get('estimated_salary_range','')},{c.get('recommended_action','')},\"{c.get('why_this_score','')}\"")
        return '\n'.join(lines)
    except:
        return "Error generating CSV"

def generate_html_report(data, title=""):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        summary = data.get('screening_summary', {})
        candidates = data.get('candidates', [])
        
        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Screening Report</title>
<style>
body{{font-family:Arial,sans-serif;max-width:900px;margin:40px auto;padding:20px;color:#333;}}
.header{{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;padding:30px;border-radius:10px;margin-bottom:30px;}}
.summary{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:30px;}}
.card{{background:#f8f9fa;padding:20px;border-radius:8px;text-align:center;}}
.card .num{{font-size:28px;font-weight:bold;color:#6366f1;}}
.candidate{{border:1px solid #e5e7eb;border-radius:10px;padding:20px;margin-bottom:15px;}}
.score-high{{color:#10b981;}} .score-med{{color:#f59e0b;}} .score-low{{color:#ef4444;}}
</style></head><body>
<div class="header"><h1>CV Screening Report</h1><p>{title} | {datetime.now().strftime('%Y-%m-%d')}</p></div>
<div class="summary">
<div class="card"><div class="num">{summary.get('total_candidates','?')}</div><div>Candidates</div></div>
<div class="card"><div class="num" style="color:#10b981">{summary.get('recommended_for_interview','?')}</div><div>Recommended</div></div>
<div class="card"><div class="num" style="color:#f59e0b">{summary.get('maybe','?')}</div><div>Maybe</div></div>
<div class="card"><div class="num">~{summary.get('time_saved_minutes','?')}m</div><div>Time Saved</div></div>
</div>"""
        
        for c in candidates:
            score = c.get('match_score', 0)
            sc = "score-high" if score >= 70 else "score-med" if score >= 50 else "score-low"
            html += f"""<div class="candidate">
<h3>#{c.get('rank')} {c.get('identifier')} - <span class="{sc}">{score}%</span></h3>
<p><b>Skills:</b> Required {c.get('required_skills_match','?')} | Preferred {c.get('preferred_skills_match','?')}</p>
<p><b>Why:</b> {c.get('why_this_score','')}</p>
<p><b>Strengths:</b> {', '.join(c.get('strengths',[]))}</p>
<p><b>Concerns:</b> {', '.join(c.get('concerns',[]))}</p>
<p><b>Recommendation:</b> {c.get('recommended_action','')}</p>
</div>"""
        
        html += "</body></html>"
        return html
    except:
        return "<html><body>Error</body></html>"

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp Screen", page_icon="🔍", layout="wide")
init_session()
check_url_auth()

# Global styles - matching Sharp Human brand colors
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

/* Reset and base */
*, *::before, *::after { font-family: 'Nunito', sans-serif !important; box-sizing: border-box; }

/* Main app background - dark theme matching website */
.stApp { background: #0a0a0f !important; }
[data-testid="stAppViewContainer"] { background: #0a0a0f !important; }
[data-testid="stHeader"] { background: transparent !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #0d0d14 !important; border-right: 1px solid rgba(99,102,241,0.2); }
[data-testid="stSidebar"] * { color: #e5e5e5 !important; }

/* Text colors */
h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
p, span, label, div { color: #e5e5e5; }

/* Form inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div {
    background: #12121a !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton > button:hover { opacity: 0.9; }

/* Download buttons */
.stDownloadButton > button {
    background: #1a1a2e !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    color: white !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: transparent; gap: 8px; }
.stTabs [data-baseweb="tab"] { 
    background: #12121a; 
    border-radius: 8px 8px 0 0; 
    color: #9ca3af !important;
    border: 1px solid rgba(99,102,241,0.2);
    border-bottom: none;
}
.stTabs [aria-selected="true"] { 
    background: rgba(99,102,241,0.2) !important; 
    color: white !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent; }

/* Radio buttons horizontal */
.stRadio > div { flex-direction: row !important; gap: 16px; flex-wrap: wrap; }
.stRadio label { 
    background: #12121a !important; 
    padding: 8px 16px !important; 
    border-radius: 8px !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
}
.stRadio [data-checked="true"] label {
    background: rgba(99,102,241,0.3) !important;
    border-color: #6366f1 !important;
}

/* File uploader */
[data-testid="stFileUploader"] { background: #12121a; border-radius: 8px; padding: 16px; }
[data-testid="stFileUploader"] label { color: white !important; }

/* Checkbox */
.stCheckbox label { color: #e5e5e5 !important; }

/* Hide problematic expander icons completely */
.streamlit-expanderHeader svg { display: none !important; }
details summary { list-style: none; }
details summary::-webkit-details-marker { display: none; }

/* Success/error messages */
.stSuccess, .stError, .stWarning, .stInfo { border-radius: 8px; }

/* Custom classes */
.status-badge {
    position: fixed;
    top: 70px;
    right: 20px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    padding: 10px 20px;
    border-radius: 25px;
    font-weight: 600;
    z-index: 1000;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.metric-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1));
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.candidate-card {
    background: #12121a;
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 24px;
    margin: 16px 0;
}

.output-box {
    background: #12121a;
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    white-space: pre-wrap;
    color: #e5e5e5;
}

.user-card {
    background: rgba(99,102,241,0.1);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
}
</style>""", unsafe_allow_html=True)

# Auth screen
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px 0;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;">
            <h1 style="margin:0;">Sharp Screen</h1>
            <p style="color:#9ca3af;">AI CV Screening & Analysis</p>
        </div>""", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Log In", use_container_width=True):
                if password == GOD_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_god = True
                    st.session_state.user = {"email": "GOD", "id": "god"}
                    st.session_state.user_plan = "god"
                    st.session_state.session_token = secrets.token_urlsafe(32)
                    st.rerun()
                elif email and password:
                    r = supabase_sign_in(email, password)
                    if r["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = r["user"]
                        st.session_state.session_token = r.get("session_token")
                        st.rerun()
                    else:
                        st.error(r["message"])
            
            st.markdown("---")
            magic_email = st.text_input("Or get a magic link:", placeholder="your@email.com", key="magic")
            if st.button("Send Magic Link", use_container_width=True):
                if magic_email:
                    r = supabase_magic_link(magic_email)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
        
        with tab2:
            new_email = st.text_input("Email", key="signup_email")
            new_pass = st.text_input("Password", type="password", key="signup_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm")
            if st.button("Create Account", use_container_width=True):
                if new_pass != confirm_pass:
                    st.error("Passwords don't match")
                elif len(new_pass) < 6:
                    st.warning("Password must be 6+ characters")
                elif new_email and new_pass:
                    r = supabase_sign_up(new_email, new_pass)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
    st.stop()

# ============================================
# AUTHENTICATED APP
# ============================================

# Working status badge
if st.session_state.working_on:
    st.markdown(f'<div class="status-badge">✨ {st.session_state.working_on}</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"""<div class="user-card">
        <p style="color:#9ca3af;margin:0;font-size:12px;">Logged in as</p>
        <p style="color:white;margin:4px 0;font-weight:600;">{get_user_email()}</p>
        <p style="color:#6366f1;margin:0;font-size:12px;text-transform:uppercase;">{st.session_state.get('user_plan', 'free')} plan</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("**Apps**")
    apps = [
        ("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"),
        ("interview", "🎯 Interview"), ("source", "🎣 Sourcing"), ("content", "✍️ Content"),
        ("sales", "💰 Sales"), ("reach", "🚀 Reach"), ("assistant", "🤖 Assistant"),
    ]
    for app_key, label in apps:
        if app_key == "screen":
            st.button(f"{label} ◀", disabled=True, use_container_width=True)
        else:
            st.link_button(label, build_app_url(app_key), use_container_width=True)
    
    if st.session_state.get("is_god"):
        st.markdown("---")
        st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
    
    st.markdown("---")
    
    # Feedback - simple toggle instead of expander
    if st.button("💬 Send Feedback", use_container_width=True):
        st.session_state.show_feedback = not st.session_state.get('show_feedback', False)
    
    if st.session_state.get('show_feedback'):
        fb_type = st.selectbox("Type", ["General", "Bug", "Feature"], key="fb_type")
        fb_msg = st.text_area("Message", height=80, key="fb_msg")
        if st.button("Submit", key="fb_submit"):
            if fb_msg:
                submit_feedback("screen", fb_type.lower(), 4, fb_msg)
                st.success("Thanks! 🙏")
                st.session_state.show_feedback = False
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main header
st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:30px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:50px;">
    <div>
        <h1 style="margin:0;font-size:28px;">Sharp Screen</h1>
        <p style="color:#9ca3af;margin:0;">AI-Powered CV Screening & Analysis</p>
    </div>
</div>""", unsafe_allow_html=True)

# Main tabs
tab_screen, tab_blind, tab_github, tab_salary = st.tabs(["🔍 Screen & Rank", "👤 Blind Resume", "💻 GitHub", "💰 Salary"])

with tab_screen:
    st.markdown("### 📋 Job Description")
    
    jd_source = st.radio("JD Source:", ["📝 Paste JD", "📜 From History", "📄 Upload File"], horizontal=True, key="jd_src")
    
    jd_text = ""
    selected_jd_id = None
    
    if jd_source == "📜 From History":
        jd_history = get_jd_history(20)
        if jd_history:
            options = {f"{j['job_title']} ({j['created_at'][:10]})": j for j in jd_history}
            selected = st.selectbox("Select JD:", list(options.keys()))
            if selected:
                jd_data = options[selected]
                jd_text = jd_data.get('generated_jd', '')
                selected_jd_id = jd_data.get('id')
                st.success(f"✅ Loaded: {jd_data.get('job_title')}")
                if st.checkbox("Preview JD"):
                    st.text_area("JD:", jd_text[:1500], height=150, disabled=True)
        else:
            st.info("No saved JDs. Use Sharp JD to create some.")
            jd_text = st.text_area("Or paste here:", height=120)
    
    elif jd_source == "📄 Upload File":
        jd_file = st.file_uploader("Upload JD (PDF, DOCX, TXT)", type=['pdf', 'docx', 'doc', 'txt'])
        if jd_file:
            jd_text = extract_text_from_file(jd_file)
            st.success(f"✅ Extracted from {jd_file.name}")
            if st.checkbox("Preview"):
                st.text_area("Extracted:", jd_text[:1500], height=150, disabled=True)
    else:
        jd_text = st.text_area("Paste Job Description:", height=150, placeholder="Paste the job description here...")
    
    st.markdown("---")
    st.markdown("### 📄 Candidate CVs")
    
    cv_source = st.radio("CV Source:", ["📝 Paste", "📁 Upload Files", "🔗 JSON/ATS"], horizontal=True, key="cv_src")
    
    cvs_text = ""
    
    if cv_source == "📁 Upload Files":
        cv_files = st.file_uploader("Upload CVs (multiple)", type=['pdf', 'docx', 'doc', 'txt'], accept_multiple_files=True)
        if cv_files:
            st.success(f"📎 {len(cv_files)} files")
            extracted = []
            for f in cv_files:
                extracted.append(f"=== {f.name} ===\n{extract_text_from_file(f)}")
            cvs_text = "\n\n---\n\n".join(extracted)
            if st.checkbox("Preview CVs"):
                st.text_area("Extracted:", cvs_text[:2000], height=150, disabled=True)
    
    elif cv_source == "🔗 JSON/ATS":
        json_input = st.text_area("Paste JSON:", height=120, placeholder='[{"name": "...", "skills": [...]}]')
        if json_input:
            candidates = parse_json_candidates(json_input)
            if candidates:
                st.success(f"✅ {len(candidates)} candidates")
                cvs_text = "\n\n---\n\n".join([json.dumps(c, indent=2) for c in candidates])
            else:
                st.error("Invalid JSON")
    else:
        cvs_text = st.text_area("Paste CVs (separate with ---):", height=180, placeholder="CV 1...\n\n---\n\nCV 2...")
    
    st.markdown("---")
    st.markdown("### ⚙️ Options")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        bias_free = st.checkbox("🔒 Bias-Free", value=True)
    with c2:
        ai_detect = st.checkbox("🤖 AI Detection", value=True)
    with c3:
        salary_est = st.checkbox("💰 Salary Est.", value=True)
    with c4:
        save_hist = st.checkbox("💾 Save", value=True)
    
    if st.button("🔍 Screen Candidates", type="primary", use_container_width=True):
        if not jd_text:
            st.warning("Please provide a job description")
        elif not cvs_text:
            st.warning("Please provide CVs")
        else:
            st.session_state.working_on = "Analyzing candidates..."
            
            with st.spinner("🔍 Screening candidates..."):
                result, tokens = screen_candidates(jd_text, cvs_text, {
                    'bias_free': bias_free, 'ai_detection': ai_detect, 'salary_estimate': salary_est
                })
                
                st.session_state.working_on = None
                
                if not result.startswith("Error"):
                    st.session_state.screening_results = result
                    if save_hist:
                        save_screen_history(selected_jd_id, jd_text, cvs_text, result, cvs_text.count('---')+1, tokens)
                    st.rerun()
                else:
                    st.error(result)
    
    # Results
    if st.session_state.screening_results:
        st.markdown("---")
        st.markdown("### 📊 Results")
        
        try:
            match = re.search(r'```json\s*(.*?)\s*```', st.session_state.screening_results, re.DOTALL)
            data = json.loads(match.group(1) if match else st.session_state.screening_results)
            
            summary = data.get('screening_summary', {})
            candidates = data.get('candidates', [])
            insights = data.get('batch_insights', {})
            
            # Metrics
            cols = st.columns(4)
            metrics = [
                ("Candidates", summary.get('total_candidates', '?'), "white"),
                ("Recommended", summary.get('recommended_for_interview', '?'), "#10b981"),
                ("Maybe", summary.get('maybe', '?'), "#f59e0b"),
                ("Time Saved", f"~{summary.get('time_saved_minutes', '?')}m", "#6366f1")
            ]
            for col, (label, value, color) in zip(cols, metrics):
                with col:
                    st.markdown(f"""<div class="metric-card">
                        <p style="color:#9ca3af;margin:0;font-size:12px;">{label}</p>
                        <p style="color:{color};font-size:28px;font-weight:bold;margin:0;">{value}</p>
                    </div>""", unsafe_allow_html=True)
            
            st.markdown("")
            
            # Candidates
            for c in candidates:
                score = c.get('match_score', 0)
                color = "#10b981" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
                
                st.markdown(f"""<div class="candidate-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="background:#6366f1;color:white;padding:4px 12px;border-radius:20px;font-size:13px;">#{c.get('rank')}</span>
                            <span style="font-size:18px;font-weight:bold;margin-left:12px;">{c.get('identifier')}</span>
                        </div>
                        <span style="font-size:28px;font-weight:bold;color:{color};">{score}%</span>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:16px 0;">
                        <div>Required: {c.get('required_skills_match', '?')}</div>
                        <div>Preferred: {c.get('preferred_skills_match', '?')}</div>
                        <div>Experience: {c.get('experience_years', '?')} yrs</div>
                        <div>Salary: {c.get('estimated_salary_range', '?')}</div>
                    </div>
                    <p><b>Why:</b> {c.get('why_this_score', '')}</p>
                    <p style="color:#10b981;"><b>+</b> {', '.join(c.get('strengths', []))}</p>
                    <p style="color:#f59e0b;"><b>-</b> {', '.join(c.get('concerns', []))}</p>
                    <div style="background:rgba(99,102,241,0.1);padding:12px;border-radius:8px;margin-top:12px;">
                        <b>➤ {c.get('recommended_action', '')}</b><br>
                        <span style="color:#9ca3af;">{c.get('next_steps', '')}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
            
            # Insights
            if insights:
                st.markdown("### 💡 Insights")
                st.info(f"**Top:** {insights.get('strongest_candidate_summary', '')}")
                if insights.get('common_gaps'):
                    st.warning(f"**Gaps:** {', '.join(insights.get('common_gaps', []))}")
                st.success(f"**Recommendation:** {insights.get('hiring_recommendation', '')}")
            
            # Export
            st.markdown("### 📥 Export")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.download_button("📊 CSV", generate_csv_report(data), "report.csv", "text/csv", use_container_width=True)
            with c2:
                st.download_button("📄 HTML", generate_html_report(data), "report.html", "text/html", use_container_width=True)
            with c3:
                st.download_button("🔗 JSON", json.dumps(data, indent=2), "report.json", "application/json", use_container_width=True)
            with c4:
                if st.button("🔄 New", use_container_width=True):
                    st.session_state.screening_results = None
                    st.rerun()
        
        except Exception as e:
            st.markdown(f'<div class="output-box">{st.session_state.screening_results}</div>', unsafe_allow_html=True)

with tab_blind:
    st.markdown("### 👤 Blind Resume Anonymization")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        anon_src = st.radio("Source:", ["📝 Paste", "📄 Upload"], horizontal=True, key="anon_src")
        if anon_src == "📄 Upload":
            anon_file = st.file_uploader("Upload CV", type=['pdf', 'docx', 'txt'], key="anon_file")
            resume_text = extract_text_from_file(anon_file) if anon_file else ""
        else:
            resume_text = st.text_area("Paste resume:", height=250)
    
    with c2:
        st.markdown("**Options**")
        time_based = st.checkbox("⏱️ Time-based dates")
        st.markdown("**Removes:** Names, emails, phones, addresses, universities, companies")
    
    if st.button("👤 Anonymize", type="primary", use_container_width=True):
        if resume_text:
            st.session_state.working_on = "Anonymizing..."
            with st.spinner("Processing..."):
                result, _ = anonymize_cv(resume_text, {'time_based': time_based})
                st.session_state.working_on = None
                if not result.startswith("Error"):
                    st.session_state.anonymized_result = result
                    st.rerun()
                else:
                    st.error(result)
        else:
            st.warning("Please provide a resume")
    
    if st.session_state.get('anonymized_result'):
        try:
            match = re.search(r'```json\s*(.*?)\s*```', st.session_state.anonymized_result, re.DOTALL)
            data = json.loads(match.group(1) if match else st.session_state.anonymized_result)
            
            st.markdown("### ✅ Anonymized")
            st.metric("Confidence", f"{data.get('anonymization_score', 0)}%")
            
            removed = data.get('items_removed', {})
            if any(removed.values()):
                st.markdown("**Removed:**")
                for k, v in removed.items():
                    if v:
                        st.write(f"• {k}: {', '.join(v) if isinstance(v, list) else v}")
            
            st.markdown(f'<div class="output-box">{data.get("anonymized_cv", "")}</div>', unsafe_allow_html=True)
            st.download_button("📥 Download", data.get("anonymized_cv", ""), "anonymized.txt", use_container_width=True)
        except:
            st.markdown(f'<div class="output-box">{st.session_state.anonymized_result}</div>', unsafe_allow_html=True)

with tab_github:
    st.markdown("### 💻 GitHub Analysis")
    st.info("Coming soon - paste a GitHub URL to analyze code quality, activity, and collaboration signals.")

with tab_salary:
    st.markdown("### 💰 Salary Estimator")
    
    c1, c2 = st.columns(2)
    with c1:
        sal_jd = st.text_area("Job Description:", height=150, key="sal_jd")
    with c2:
        sal_cv = st.text_area("Candidate CV:", height=150, key="sal_cv")
    
    location = st.selectbox("Market:", ["US - National", "US - SF Bay Area", "US - NYC", "US - Remote", "UK - London", "EU", "Canada"])
    
    if st.button("💰 Estimate", type="primary", use_container_width=True):
        if sal_jd and sal_cv:
            st.session_state.working_on = "Estimating..."
            with st.spinner("Analyzing..."):
                result, _ = estimate_salary(sal_cv, sal_jd, location)
                st.session_state.working_on = None
                if not result.startswith("Error"):
                    st.markdown("### 💵 Estimate")
                    st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
                else:
                    st.error(result)
        else:
            st.warning("Provide both JD and CV")
