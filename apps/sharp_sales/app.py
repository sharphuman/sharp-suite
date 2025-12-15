"""Sharp Sales - AI Sales Call Analysis (Single Screen)"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta, date
import secrets
import json
import re
import io
import tempfile

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
GOD_PASSWORD = os.environ.get("GOD_PASSWORD", "G0DHum@n101!!!")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

APP_URLS = {"portal": "https://demo.sharphuman.com", "jd": "https://jd.sharphuman.com", "screen": "https://screen.sharphuman.com", "interview": "https://hire.sharphuman.com", "source": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com", "sales": "https://sales.sharphuman.com", "reach": "https://reach.sharphuman.com", "assistant": "https://assistant.sharphuman.com", "admin": "https://admin.sharphuman.com"}

CALL_FRAMEWORKS = {
    "discovery": {"name": "Discovery Call", "stages": {
        "opening": {"name": "Opening", "weight": 15, "skills": ["Rapport Building", "Setting the Frame", "Permission to Proceed"]},
        "discovery": {"name": "Discovery", "weight": 40, "skills": ["Uncovering Pain & Goals", "Probing Questions", "Cost of Inaction", "Timeline & Urgency", "Budget Discovery"]},
        "qualify": {"name": "Qualification", "weight": 20, "skills": ["Decision Authority", "Buying Process", "Competitive Landscape"]},
        "close": {"name": "Close", "weight": 25, "skills": ["Summary & Recap", "Clear Next Steps", "Getting Commitment", "Multi-threading"]}
    }},
    "demo": {"name": "Demo/Presentation", "stages": {
        "setup": {"name": "Setup", "weight": 15, "skills": ["Discovery Recap", "Demo Agenda", "Attendee Check"]},
        "demo": {"name": "Demonstration", "weight": 40, "skills": ["Tailored Demo", "Storytelling", "Audience Engagement", "Objection Handling"]},
        "value": {"name": "Value", "weight": 20, "skills": ["ROI Discussion", "Differentiation", "Social Proof"]},
        "close": {"name": "Close", "weight": 25, "skills": ["Temperature Check", "Surfacing Concerns", "Next Steps"]}
    }},
    "proposal": {"name": "Proposal Call", "stages": {
        "review": {"name": "Proposal Review", "weight": 30, "skills": ["Proposal Walkthrough", "Pricing Presentation", "Value Justification", "Addressing Questions"]},
        "concerns": {"name": "Concerns", "weight": 35, "skills": ["Objection Handling", "Risk Mitigation", "Competitor Comparison", "Stakeholder Concerns"]},
        "close": {"name": "Close", "weight": 35, "skills": ["Decision Timeline", "Next Steps", "Verbal Commitment", "Contract Process"]}
    }},
    "negotiation": {"name": "Negotiation Call", "stages": {
        "review": {"name": "Review", "weight": 20, "skills": ["Proposal Recap", "Value Reinforcement"]},
        "negotiate": {"name": "Negotiation", "weight": 50, "skills": ["Listening to Concerns", "Trading Value", "Anchoring", "Creative Solutions"]},
        "close": {"name": "Close", "weight": 30, "skills": ["Asking for Close", "Final Objections", "Paperwork Process"]}
    }},
    "interview": {"name": "Customer Interview", "stages": {
        "intro": {"name": "Introduction", "weight": 15, "skills": ["Rapport Building", "Setting Context", "Permission & Recording"]},
        "discovery": {"name": "Discovery", "weight": 50, "skills": ["Open-Ended Questions", "Active Listening", "Follow-up Probes", "Capturing Insights", "Pain Point Exploration"]},
        "close": {"name": "Wrap-Up", "weight": 35, "skills": ["Summary of Key Points", "Additional Questions", "Next Steps", "Thank You & Follow-up"]}
    }},
    "follow_up": {"name": "Follow-Up Call", "stages": {
        "reconnect": {"name": "Reconnect", "weight": 25, "skills": ["Context Reset", "Situation Changes", "Value Reminder"]},
        "advance": {"name": "Advance", "weight": 50, "skills": ["Address Objections", "New Information", "Creating Urgency"]},
        "commit": {"name": "Commitment", "weight": 25, "skills": ["Micro-Commitment", "Book Next Meeting", "Action Items"]}
    }}
}

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try: requests.post(f"{SUPABASE_URL}/rest/v1/sessions", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "sales", "is_active": True, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()}, timeout=10)
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
        data = r.json()
        return {"success": True, "message": "Check email!"} if r.status_code == 200 and data.get("user") else {"success": False, "message": data.get("error_description") or "Failed"}
    except Exception as e: return {"success": False, "message": str(e)}

def validate_session_token(token):
    if not token: return None
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        if r.status_code == 200 and r.json():
            session = r.json()[0]
            expires = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
            if expires.replace(tzinfo=None) > datetime.utcnow():
                ur = requests.get(f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
                if ur.status_code == 200 and ur.json():
                    p = ur.json()[0]
                    return {"user_id": session["user_id"], "email": p.get("email"), "plan": p.get("plan", "free"), "token": token}
    except: pass
    return None

def log_usage(user_id, session_id, app, action, tokens_used=0):
    try: requests.post(f"{SUPABASE_URL}/rest/v1/usage_logs", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": user_id, "session_id": session_id, "app": app, "action": action, "tokens_used": tokens_used}, timeout=5)
    except: pass

def submit_feedback(app, feedback_type, message):
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/user_feedback", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": st.session_state.user.get("id") if st.session_state.user else None, "app": app, "feedback_type": feedback_type, "rating": 4, "message": message, "email": get_user_email()}, timeout=10)
        return r.status_code in [200, 201]
    except: return False

def init_session():
    for k, v in [('authenticated', False), ('user', None), ('is_god', False), ('session_token', None), ('user_plan', 'free'), ('working_on', None), ('analysis_result', None)]:
        if k not in st.session_state: st.session_state[k] = v

def check_url_auth():
    token = st.query_params.get("auth")
    if token and not st.session_state.authenticated:
        user_info = validate_session_token(token)
        if user_info:
            st.session_state.authenticated, st.session_state.user = True, {"email": user_info["email"], "id": user_info["user_id"]}
            st.session_state.session_token, st.session_state.user_plan = token, user_info.get("plan", "free")
            st.session_state.is_god = user_info.get("plan") == "god"
            return True
    return False

def get_user_email(): return st.session_state.user.get("email", "User") if st.session_state.user else ("GOD" if st.session_state.is_god else "User")
def build_app_url(app_name):
    base, token = APP_URLS.get(app_name, ""), st.session_state.get("session_token", "")
    return f"{base}?auth={token}" if base and token else base

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded files with robust DOCX handling"""
    file_type = uploaded_file.name.split('.')[-1].lower()
    content = uploaded_file.read()
    uploaded_file.seek(0)
    
    if file_type == 'txt':
        return content.decode('utf-8', errors='ignore')
    
    elif file_type == 'pdf':
        try:
            import fitz
            pdf = fitz.open(stream=content, filetype="pdf")
            return "\n".join([page.get_text() for page in pdf])
        except Exception as e:
            return f"[PDF extraction error: {e}]"
    
    elif file_type in ['docx', 'doc']:
        # Try python-docx first
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            # Also get text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            paragraphs.append(cell.text.strip())
            if paragraphs:
                return '\n\n'.join(paragraphs)
        except Exception as e:
            pass
        
        # Fallback: try to extract raw text from DOCX (it's a zip file)
        try:
            import zipfile
            from xml.etree import ElementTree
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                xml_content = z.read('word/document.xml')
                tree = ElementTree.fromstring(xml_content)
                texts = []
                for elem in tree.iter():
                    if elem.text:
                        texts.append(elem.text)
                if texts:
                    return ' '.join(texts)
        except:
            pass
        
        return "[DOCX extraction failed - please paste the transcript directly]"
    
    elif file_type in ['vtt', 'srt']:
        text = content.decode('utf-8', errors='ignore')
        # Remove timestamps and formatting
        text = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', text)
        text = re.sub(r'WEBVTT.*?\n', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    elif file_type in ['mp3', 'm4a', 'wav', 'mp4', 'webm', 'ogg']:
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            try:
                with tempfile.NamedTemporaryFile(suffix=f".{file_type}", delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                with open(tmp_path, 'rb') as f:
                    r = requests.post("https://api.openai.com/v1/audio/transcriptions", headers={"Authorization": f"Bearer {openai_key}"}, files={"file": f}, data={"model": "whisper-1"}, timeout=300)
                os.unlink(tmp_path)
                if r.status_code == 200:
                    return r.json().get("text", "")
                return f"[Transcription error: {r.status_code}]"
            except Exception as e:
                return f"[Transcription error: {e}]"
        return "[Audio transcription requires OPENAI_API_KEY environment variable]"
    
    # Default: try to decode as text
    return content.decode('utf-8', errors='ignore')

def call_claude(prompt, max_tokens=8000, action="sales"):
    if not ANTHROPIC_API_KEY: return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=180)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            if st.session_state.user: log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "sales", action, (len(prompt)+len(text))//4)
            return text, (len(prompt)+len(text))//4
        return f"Error: {r.status_code}", 0
    except Exception as e: return f"Error: {e}", 0

def analyze_call(call_type, prospect_name, company_name, deal_size, stage, notes, transcript):
    fw = CALL_FRAMEWORKS.get(call_type, CALL_FRAMEWORKS['discovery'])
    stages_desc = "\n".join([f"### {s['name']} (Weight: {s['weight']}%)\nSkills: {', '.join(s['skills'])}" for s in fw['stages'].values()])
    
    prompt = f"""You are an expert sales coach analyzing a {fw['name']}.

## CALL CONTEXT
- Prospect: {prospect_name or 'Unknown'} at {company_name or 'Unknown Company'}
- Deal Size: {deal_size or 'Unknown'}
- Stage: {stage or 'Unknown'}
- Notes: {notes or 'None'}

## EVALUATION FRAMEWORK
{stages_desc}

## TRANSCRIPT
{transcript[:20000]}

---

Analyze this call thoroughly. For each stage and skill, provide specific feedback with exact quotes from the transcript.

Return your analysis in this JSON format:
```json
{{
    "overall_score": <0-100>,
    "overall_summary": "<2-3 sentence executive summary>",
    "stages": [
        {{
            "stage_name": "<Stage Name>",
            "stage_score": <0-10>,
            "skills": [
                {{
                    "skill_name": "<Skill Name>",
                    "score": <0-10>,
                    "score_label": "<Excellent|Good|Needs Work|Missed>",
                    "feedback": ["<specific feedback point>", "<another point>"],
                    "transcript_examples": ["<exact quote from transcript>"],
                    "improvement_example": "<what they could have said instead>"
                }}
            ]
        }}
    ],
    "key_wins": ["<something done well>", "<another strength>"],
    "critical_improvements": ["<most important fix>", "<second priority>"],
    "deal_insights": {{
        "buying_signals": ["<signal identified>"],
        "red_flags": ["<concern>"],
        "next_steps_suggested": ["<recommended action>"],
        "deal_probability": "<High|Medium|Low>",
        "deal_probability_reasoning": "<why>"
    }},
    "coaching_summary": "<paragraph of personalized coaching advice>"
}}
```

Be specific. Use exact quotes. Be constructive but honest."""

    return call_claude(prompt, 8000, f"analyze_{call_type}")

st.set_page_config(page_title="Sharp Sales", page_icon="💰", layout="wide")
init_session()
check_url_auth()

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
.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div, [data-baseweb="select"] > div { background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: #fff !important; border-radius: 8px !important; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stDownloadButton > button { background: #1a1a2e !important; border: 1px solid rgba(99,102,241,0.3) !important; }
.stRadio > div { flex-direction: row !important; gap: 8px; flex-wrap: wrap; }
.stRadio > div > label { background: #12121a !important; padding: 10px 16px !important; border-radius: 8px !important; border: 1px solid rgba(99,102,241,0.2) !important; }
[data-testid="stFileUploader"] { background: #12121a !important; border: 1px dashed rgba(99,102,241,0.3) !important; border-radius: 8px !important; }
.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.input-section { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; margin: 12px 0; }
.transcript-quote { background: #1a1a2e; border-left: 3px solid #6366f1; padding: 12px 16px; margin: 8px 0; border-radius: 0 8px 8px 0; font-style: italic; color: #a5b4fc; }
.improvement-box { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 16px; margin-top: 12px; }
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; z-index: 999; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
div[data-testid="stPopover"] button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 25px !important; }
</style>""", unsafe_allow_html=True)

# Auth
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="margin:0;">Sharp Sales</h1><p style="color:#9ca3af;">AI Sales Call Analysis</p></div>""", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Log In", "Sign Up"])
        with t1:
            email, pwd = st.text_input("Email", key="l_email"), st.text_input("Password", type="password", key="l_pwd")
            if st.button("Log In", use_container_width=True):
                if pwd == GOD_PASSWORD:
                    st.session_state.authenticated, st.session_state.is_god, st.session_state.user = True, True, {"email": "GOD", "id": "god"}
                    st.session_state.session_token = secrets.token_urlsafe(32)
                    st.rerun()
                elif email and pwd:
                    r = supabase_sign_in(email, pwd)
                    if r["success"]: st.session_state.authenticated, st.session_state.user, st.session_state.session_token = True, r["user"], r.get("session_token"); st.rerun()
                    else: st.error(r["message"])
        with t2:
            s_email, s_pwd, s_conf = st.text_input("Email", key="s_email"), st.text_input("Password", type="password", key="s_pwd"), st.text_input("Confirm", type="password", key="s_conf")
            if st.button("Create Account", use_container_width=True):
                if s_pwd != s_conf: st.error("Passwords don't match")
                elif len(s_pwd) < 6: st.warning("6+ characters")
                elif s_email and s_pwd:
                    r = supabase_sign_up(s_email, s_pwd)
                    st.success(r["message"]) if r["success"] else st.error(r["message"])
    st.stop()

if st.session_state.working_on: st.markdown(f'<div class="status-badge">{st.session_state.working_on}</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"""<div class="user-card"><p style="color:#9ca3af;margin:0;font-size:12px;">Logged in as</p><p style="color:#fff;margin:4px 0;font-weight:600;">{get_user_email()}</p><p style="color:#6366f1;margin:0;font-size:12px;text-transform:uppercase;">{st.session_state.get('user_plan','free')} plan</p></div>""", unsafe_allow_html=True)
    st.markdown("**Apps**")
    for key, label in [("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"), ("interview", "🎯 Interview"), ("source", "🎣 Sourcing"), ("content", "✍️ Content"), ("sales", "💰 Sales"), ("reach", "🚀 Reach"), ("assistant", "🤖 Assistant")]:
        if key == "sales": st.markdown(f"<div style='background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:10px 16px;border-radius:8px;text-align:center;margin:4px 0;color:white;font-weight:600;'>{label} ◀</div>", unsafe_allow_html=True)
        else: st.link_button(label, build_app_url(key), use_container_width=True)
    if st.session_state.get("is_god"): st.markdown("---"); st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:30px;"><img src="https://sharphuman.com/logo1-3.png" style="width:50px;"><div><h1 style="margin:0;font-size:28px;">Sharp Sales</h1><p style="color:#9ca3af;margin:0;">AI-Powered Sales Call Analysis</p></div></div>""", unsafe_allow_html=True)

# Check for results
if st.session_state.get('analysis_result'):
    # Results View
    if st.button("← New Analysis", type="secondary"):
        st.session_state.analysis_result = None
        st.rerun()
    
    try:
        txt = st.session_state.analysis_result
        m = re.search(r'```json\s*(.*?)\s*```', txt, re.DOTALL)
        a = json.loads(m.group(1) if m else txt)
        
        score = a.get('overall_score', 0)
        color = "#10b981" if score >= 70 else "#eab308" if score >= 50 else "#ef4444"
        
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border-radius:16px;padding:30px;text-align:center;margin-bottom:24px;">
            <p style="color:#9ca3af;margin:0;">OVERALL SCORE</p>
            <p style="color:{color};font-size:64px;font-weight:bold;margin:10px 0;">{score}<span style="font-size:24px;color:#6b7280;">/100</span></p>
            <p style="color:#e5e5e5;">{a.get('overall_summary', '')}</p>
        </div>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ✅ Key Wins")
            for w in a.get('key_wins', []): st.markdown(f"<div style='background:rgba(16,185,129,0.1);border-left:3px solid #10b981;padding:12px;margin:8px 0;border-radius:0 8px 8px 0;'>{w}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("#### 🎯 Critical Improvements")
            for i in a.get('critical_improvements', []): st.markdown(f"<div style='background:rgba(239,68,68,0.1);border-left:3px solid #ef4444;padding:12px;margin:8px 0;border-radius:0 8px 8px 0;'>{i}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("## 📈 Stage Analysis")
        
        for stg in a.get('stages', []):
            with st.expander(f"**{stg.get('stage_name')}** — {stg.get('stage_score', 0)}/10"):
                for sk in stg.get('skills', []):
                    sc = sk.get('score', 0)
                    bc = "#10b981" if sc >= 8 else "#eab308" if sc >= 6 else "#f97316" if sc >= 4 else "#ef4444"
                    sym = "✓" if sc >= 6 else "−" if sc >= 4 else "✗"
                    
                    st.markdown(f"<div style='background:#12121a;border-radius:12px;padding:16px;margin:12px 0;border:1px solid rgba(99,102,241,0.2);'><div style='display:flex;justify-content:space-between;'><span style='font-weight:600;color:#fff;'>{sk.get('skill_name')}</span><span style='background:rgba(99,102,241,0.2);color:{bc};padding:6px 14px;border-radius:20px;font-size:13px;'>{sym} {sc}/10</span></div></div>", unsafe_allow_html=True)
                    
                    st.markdown("**Feedback:**")
                    for fb in sk.get('feedback', []): st.markdown(f"→ {fb}")
                    
                    if sk.get('transcript_examples'):
                        st.markdown("**From the call:**")
                        for q in sk.get('transcript_examples', []): st.markdown(f'<div class="transcript-quote">"{q}"</div>', unsafe_allow_html=True)
                    
                    if sk.get('improvement_example'):
                        st.markdown(f'<div class="improvement-box"><p style="color:#10b981;margin:0 0 8px;font-weight:600;">💡 Try this instead:</p><p style="color:#e5e5e5;margin:0;font-style:italic;">{sk.get("improvement_example")}</p></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("## 💼 Deal Insights")
        
        ins = a.get('deal_insights', {})
        c1, c2, c3 = st.columns(3)
        with c1:
            prob = ins.get('deal_probability', 'Unknown')
            pc = "#10b981" if prob == "High" else "#eab308" if prob == "Medium" else "#ef4444"
            st.markdown(f"<div style='background:#12121a;border-radius:12px;padding:20px;text-align:center;'><p style='color:#9ca3af;margin:0;font-size:12px;'>DEAL PROBABILITY</p><p style='color:{pc};font-size:28px;font-weight:bold;margin:8px 0;'>{prob}</p><p style='color:#6b7280;font-size:11px;'>{ins.get('deal_probability_reasoning', '')[:80]}...</p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("**🟢 Buying Signals**")
            for s in ins.get('buying_signals', []): st.markdown(f"• {s}")
        with c3:
            st.markdown("**🔴 Red Flags**")
            for f in ins.get('red_flags', []): st.markdown(f"• {f}")
        
        st.markdown("#### 📋 Suggested Next Steps")
        for s in ins.get('next_steps_suggested', []): st.markdown(f"- [ ] {s}")
        
        st.markdown("---")
        st.markdown("## 🎓 Coaching Summary")
        st.markdown(f"<div style='background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border-radius:12px;padding:24px;border-left:4px solid #6366f1;'>{a.get('coaching_summary', '')}</div>", unsafe_allow_html=True)
        
        st.download_button("📥 Download Full Analysis", txt, "sales_analysis.md", use_container_width=True)
        
    except Exception as e:
        st.error(f"Parse error: {e}")
        st.text(st.session_state.analysis_result)

else:
    # Input Form (Single Screen)
    st.markdown("### 📞 Call Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("**Call Information**")
        call_type = st.selectbox("Call Type", list(CALL_FRAMEWORKS.keys()), format_func=lambda x: CALL_FRAMEWORKS[x]['name'])
        
        c1, c2 = st.columns(2)
        with c1:
            prospect_name = st.text_input("Prospect Name", placeholder="John Smith")
        with c2:
            company_name = st.text_input("Company", placeholder="Acme Corp")
        
        c1, c2 = st.columns(2)
        with c1:
            deal_size = st.text_input("Deal Size", placeholder="$50,000")
        with c2:
            stage = st.selectbox("Sales Stage", ["Discovery", "Qualification", "Demo", "Proposal", "Negotiation", "Closed"])
        
        notes = st.text_area("Notes/Questions (optional)", height=80, placeholder="Any specific areas you want analyzed?")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("**Call Recording / Transcript**")
        
        input_method = st.radio("Input Method:", ["📝 Paste Transcript", "📁 Upload File"], horizontal=True)
        
        transcript = ""
        
        if input_method == "📝 Paste Transcript":
            transcript = st.text_area(
                "Paste your transcript here:",
                height=250,
                placeholder="Salesperson: Hi John, thanks for taking the time today...\nProspect: Of course, happy to chat...\n\nPaste the full conversation transcript here."
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload recording or transcript",
                type=['txt', 'pdf', 'docx', 'doc', 'vtt', 'srt', 'mp3', 'wav', 'm4a', 'mp4', 'webm'],
                help="Supports: TXT, PDF, DOCX, VTT, SRT, MP3, WAV, M4A, MP4, WebM"
            )
            if uploaded_file:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    transcript = extract_text_from_file(uploaded_file)
                
                if transcript and not transcript.startswith("["):
                    st.success(f"✅ Loaded: {uploaded_file.name} ({len(transcript):,} characters)")
                    with st.expander("Preview transcript"):
                        st.text(transcript[:2000] + ("..." if len(transcript) > 2000 else ""))
                else:
                    st.warning(transcript)
                    st.info("💡 If upload fails, try pasting the transcript directly instead.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyze Button
    st.markdown("---")
    
    if st.button("🚀 Analyze Call", type="primary", use_container_width=True):
        if not transcript or len(transcript.strip()) < 100:
            st.warning("Please provide a transcript (paste or upload). Minimum 100 characters required.")
        else:
            st.session_state.working_on = "Analyzing your call..."
            result, _ = analyze_call(call_type, prospect_name, company_name, deal_size, stage, notes, transcript)
            st.session_state.working_on = None
            
            if not str(result).startswith("Error"):
                st.session_state.analysis_result = result
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
        fm = st.text_area("Message", height=100, placeholder="...", label_visibility="collapsed", key="fb_msg")
        if st.button("Send", type="primary", use_container_width=True, key="fb_send"):
            if fm:
                if submit_feedback("sales", ft.split()[1].lower() if ft else "general", fm): st.success("Thanks! 🙏")
                else: st.error("Failed")
