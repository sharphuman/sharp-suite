"""Sharp Sales - AI Sales Call Analysis with Stage-Based Scoring"""
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
        "opening": {"name": "Opening", "weight": 15, "skills": [{"id": "rapport", "name": "Rapport Building"}, {"id": "frame", "name": "Setting the Frame"}, {"id": "permission", "name": "Permission to Proceed"}]},
        "discovery": {"name": "Discovery", "weight": 40, "skills": [{"id": "pain", "name": "Uncovering Pain & Goals"}, {"id": "probing", "name": "Probing Questions"}, {"id": "impact", "name": "Cost of Inaction"}, {"id": "timeline", "name": "Timeline & Urgency"}, {"id": "budget", "name": "Budget Discovery"}]},
        "qualify": {"name": "Qualification", "weight": 20, "skills": [{"id": "authority", "name": "Decision Authority"}, {"id": "process", "name": "Buying Process"}, {"id": "competition", "name": "Competitive Landscape"}]},
        "close": {"name": "Close", "weight": 25, "skills": [{"id": "summary", "name": "Summary & Recap"}, {"id": "next_steps", "name": "Clear Next Steps"}, {"id": "commitment", "name": "Getting Commitment"}, {"id": "stakeholders", "name": "Multi-threading"}]}
    }},
    "demo": {"name": "Demo Call", "stages": {
        "setup": {"name": "Setup", "weight": 15, "skills": [{"id": "recap", "name": "Discovery Recap"}, {"id": "agenda", "name": "Demo Agenda"}, {"id": "attendees", "name": "Attendee Check"}]},
        "demo": {"name": "Demonstration", "weight": 40, "skills": [{"id": "tailoring", "name": "Tailored Demo"}, {"id": "storytelling", "name": "Storytelling"}, {"id": "engagement", "name": "Audience Engagement"}, {"id": "objections", "name": "Objection Handling"}]},
        "value": {"name": "Value", "weight": 20, "skills": [{"id": "roi", "name": "ROI Discussion"}, {"id": "diff", "name": "Differentiation"}, {"id": "proof", "name": "Social Proof"}]},
        "close": {"name": "Close", "weight": 25, "skills": [{"id": "temp", "name": "Temperature Check"}, {"id": "concerns", "name": "Surfacing Concerns"}, {"id": "next", "name": "Next Steps"}]}
    }},
    "negotiation": {"name": "Negotiation Call", "stages": {
        "review": {"name": "Review", "weight": 20, "skills": [{"id": "recap", "name": "Proposal Recap"}, {"id": "value", "name": "Value Reinforcement"}]},
        "negotiate": {"name": "Negotiation", "weight": 50, "skills": [{"id": "listen", "name": "Listening to Concerns"}, {"id": "trade", "name": "Trading Value"}, {"id": "anchor", "name": "Anchoring"}, {"id": "creative", "name": "Creative Solutions"}]},
        "close": {"name": "Close", "weight": 30, "skills": [{"id": "ask", "name": "Asking for Close"}, {"id": "final", "name": "Final Objections"}, {"id": "paper", "name": "Paperwork Process"}]}
    }},
    "follow_up": {"name": "Follow-Up Call", "stages": {
        "reconnect": {"name": "Reconnect", "weight": 25, "skills": [{"id": "context", "name": "Context Reset"}, {"id": "changes", "name": "Situation Changes"}, {"id": "remind", "name": "Value Reminder"}]},
        "advance": {"name": "Advance", "weight": 50, "skills": [{"id": "address", "name": "Address Objections"}, {"id": "new", "name": "New Information"}, {"id": "urgency", "name": "Creating Urgency"}]},
        "commit": {"name": "Commitment", "weight": 25, "skills": [{"id": "micro", "name": "Micro-Commitment"}, {"id": "book", "name": "Book Next Meeting"}, {"id": "actions", "name": "Action Items"}]}
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
    for k, v in [('authenticated', False), ('user', None), ('is_god', False), ('session_token', None), ('user_plan', 'free'), ('working_on', None), ('wizard_step', 1), ('analysis_result', None), ('call_data', {})]:
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
    ft = uploaded_file.name.split('.')[-1].lower()
    content = uploaded_file.read()
    uploaded_file.seek(0)
    if ft == 'txt': return content.decode('utf-8', errors='ignore')
    if ft == 'pdf':
        try:
            import fitz
            return "\n".join([p.get_text() for p in fitz.open(stream=content, filetype="pdf")])
        except: return "[PDF failed]"
    if ft in ['docx', 'doc']:
        try:
            from docx import Document
            return '\n'.join([p.text for p in Document(io.BytesIO(content)).paragraphs])
        except: return "[DOCX failed]"
    if ft in ['vtt', 'srt']:
        text = content.decode('utf-8', errors='ignore')
        text = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', text)
        return '\n'.join([l.strip() for l in re.sub(r'WEBVTT.*?\n|<[^>]+>|^\d+$', '', text, flags=re.MULTILINE).split('\n') if l.strip()])
    if ft in ['mp3', 'm4a', 'wav', 'mp4', 'webm']:
        key = os.environ.get("OPENAI_API_KEY", "")
        if key:
            try:
                with tempfile.NamedTemporaryFile(suffix=f".{ft}", delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                with open(tmp_path, 'rb') as f:
                    r = requests.post("https://api.openai.com/v1/audio/transcriptions", headers={"Authorization": f"Bearer {key}"}, files={"file": f}, data={"model": "whisper-1"}, timeout=300)
                os.unlink(tmp_path)
                if r.status_code == 200: return r.json().get("text", "")
            except: pass
        return "[Audio needs OPENAI_API_KEY]"
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

def analyze_call(call_data, transcript):
    fw = CALL_FRAMEWORKS.get(call_data.get('call_type', 'discovery'))
    stages_desc = "\n".join([f"### {s['name']}\n" + "\n".join([f"- {sk['name']}" for sk in s['skills']]) for s in fw['stages'].values()])
    prompt = f"""Expert sales coach analyzing a {fw['name']}. 

CONTEXT: {call_data.get('prospect_name')} at {call_data.get('company_name')} | {call_data.get('deal_size', 'Unknown')} deal | {call_data.get('stage', 'Unknown')} stage

FRAMEWORK:\n{stages_desc}

TRANSCRIPT:\n{transcript[:15000]}

Analyze with JSON:
```json
{{"overall_score": 0-100, "overall_summary": "...", "stages": [{{"stage_name": "...", "stage_score": 0-10, "skills": [{{"skill_name": "...", "score": 0-10, "score_label": "Excellent|Good|Needs Work|Missed", "feedback": ["..."], "transcript_examples": ["..."], "improvement_example": "..."}}]}}], "key_wins": ["..."], "critical_improvements": ["..."], "deal_insights": {{"buying_signals": [], "red_flags": [], "next_steps_suggested": [], "deal_probability": "High|Medium|Low", "deal_probability_reasoning": "..."}}, "coaching_summary": "..."}}
```
Be specific. Use exact quotes."""
    return call_claude(prompt, 8000, f"analyze_{call_data.get('call_type', 'discovery')}")

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
.wizard-card { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 16px; padding: 30px; margin: 20px 0; }
.transcript-quote { background: #1a1a2e; border-left: 3px solid #6366f1; padding: 12px 16px; margin: 8px 0; border-radius: 0 8px 8px 0; font-style: italic; color: #a5b4fc; }
.improvement-box { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 16px; margin-top: 12px; }
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; z-index: 999; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
div[data-testid="stPopover"] button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 25px !important; }
</style>""", unsafe_allow_html=True)

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

st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:30px;"><img src="https://sharphuman.com/logo1-3.png" style="width:50px;"><div><h1 style="margin:0;font-size:28px;">Sharp Sales</h1><p style="color:#9ca3af;margin:0;">AI-Powered Sales Call Analysis</p></div></div>""", unsafe_allow_html=True)

if st.session_state.get('analysis_result'):
    st.markdown("## 📊 Call Analysis")
    if st.button("← New Analysis"): st.session_state.analysis_result, st.session_state.wizard_step, st.session_state.call_data = None, 1, {}; st.rerun()
    try:
        txt = st.session_state.analysis_result
        m = re.search(r'```json\s*(.*?)\s*```', txt, re.DOTALL)
        a = json.loads(m.group(1) if m else txt)
        score = a.get('overall_score', 0)
        color = "#10b981" if score >= 70 else "#eab308" if score >= 50 else "#ef4444"
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border-radius:16px;padding:30px;text-align:center;"><p style="color:#9ca3af;margin:0;">OVERALL SCORE</p><p style="color:{color};font-size:64px;font-weight:bold;margin:10px 0;">{score}<span style="font-size:24px;color:#6b7280;">/100</span></p><p style="color:#e5e5e5;">{a.get('overall_summary', '')}</p></div>""", unsafe_allow_html=True)
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
                    lbl = sk.get('score_label', 'Needs Work')
                    bc = "#10b981" if sc >= 8 else "#eab308" if sc >= 6 else "#f97316" if sc >= 4 else "#ef4444"
                    sym = "✓" if sc >= 6 else "−" if sc >= 4 else "✗"
                    st.markdown(f"<div style='background:#12121a;border-radius:12px;padding:20px;margin:12px 0;border:1px solid rgba(99,102,241,0.2);'><div style='display:flex;justify-content:space-between;'><span style='font-weight:600;color:#fff;'>{sk.get('skill_name')}</span><span style='background:rgba(99,102,241,0.2);color:{bc};padding:6px 14px;border-radius:20px;font-size:13px;'>{sym} {sc}/10</span></div></div>", unsafe_allow_html=True)
                    st.markdown("**Feedback:**")
                    for fb in sk.get('feedback', []): st.markdown(f"→ {fb}")
                    if sk.get('transcript_examples'):
                        st.markdown("**Transcript:**")
                        for q in sk.get('transcript_examples', []): st.markdown(f'<div class="transcript-quote">"{q}"</div>', unsafe_allow_html=True)
                    if sk.get('improvement_example'): st.markdown(f'<div class="improvement-box"><p style="color:#10b981;margin:0 0 8px;font-weight:600;">💡 Try this:</p><p style="color:#e5e5e5;margin:0;font-style:italic;">{sk.get("improvement_example")}</p></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("## 💼 Deal Insights")
        ins = a.get('deal_insights', {})
        c1, c2, c3 = st.columns(3)
        with c1:
            prob = ins.get('deal_probability', 'Unknown')
            pc = "#10b981" if prob == "High" else "#eab308" if prob == "Medium" else "#ef4444"
            st.markdown(f"<div style='background:#12121a;border-radius:12px;padding:20px;text-align:center;'><p style='color:#9ca3af;margin:0;font-size:12px;'>DEAL PROBABILITY</p><p style='color:{pc};font-size:28px;font-weight:bold;margin:8px 0;'>{prob}</p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("**🟢 Buying Signals**")
            for s in ins.get('buying_signals', []): st.markdown(f"• {s}")
        with c3:
            st.markdown("**🔴 Red Flags**")
            for f in ins.get('red_flags', []): st.markdown(f"• {f}")
        st.markdown("#### 📋 Next Steps")
        for s in ins.get('next_steps_suggested', []): st.markdown(f"- [ ] {s}")
        st.markdown("---")
        st.markdown("## 🎓 Coaching")
        st.markdown(f"<div style='background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border-radius:12px;padding:24px;border-left:4px solid #6366f1;'>{a.get('coaching_summary', '')}</div>", unsafe_allow_html=True)
        st.download_button("📥 Download", txt, "analysis.md", use_container_width=True)
    except Exception as e: st.error(f"Parse error: {e}"); st.markdown(st.session_state.analysis_result)
else:
    step = st.session_state.wizard_step
    st.markdown(f"""<div style="display:flex;justify-content:center;gap:20px;margin-bottom:30px;"><div style="text-align:center;"><div style="width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;{'background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white' if step==1 else 'background:#10b981;color:white' if step>1 else 'background:#1a1a2e;color:#6b7280'};">1</div><p style="color:#9ca3af;font-size:12px;margin-top:8px;">Details</p></div><div style="width:60px;height:2px;background:#1a1a2e;margin-top:20px;"></div><div style="text-align:center;"><div style="width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;{'background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white' if step==2 else 'background:#1a1a2e;color:#6b7280'};">2</div><p style="color:#9ca3af;font-size:12px;margin-top:8px;">Recording</p></div></div>""", unsafe_allow_html=True)
    if step == 1:
        st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
        st.markdown("### 📞 Call Details")
        call_type = st.radio("Call Type:", list(CALL_FRAMEWORKS.keys()), format_func=lambda x: CALL_FRAMEWORKS[x]['name'], horizontal=True)
        c1, c2 = st.columns(2)
        with c1: call_date = st.date_input("📅 Call Date", value=date.today())
        with c2: deal_size = st.text_input("💰 Deal Size", placeholder="$50,000")
        stage = st.selectbox("📊 Stage", ["Discovery", "Qualification", "Demo", "Proposal", "Negotiation", "Closed"])
        st.markdown("---")
        st.markdown("### 👤 Prospect")
        c1, c2 = st.columns(2)
        with c1: prospect_name = st.text_input("Name *", placeholder="John Smith"); prospect_email = st.text_input("Email", placeholder="john@company.com")
        with c2: prospect_title = st.text_input("Title", placeholder="VP Sales"); prospect_linkedin = st.text_input("LinkedIn", placeholder="https://linkedin.com/in/...")
        st.markdown("---")
        st.markdown("### 🏢 Company")
        c1, c2 = st.columns(2)
        with c1: company_name = st.text_input("Company *", placeholder="Acme Corp"); company_website = st.text_input("Website", placeholder="https://acme.com"); industry = st.text_input("Industry", placeholder="Software")
        with c2: headcount = st.selectbox("Headcount", ["Unknown", "1-10", "11-50", "51-200", "201-500", "500+"]); location = st.text_input("Location", placeholder="San Francisco"); revenue = st.selectbox("Revenue", ["Unknown", "<$1M", "$1-10M", "$10-50M", "$50M+"])
        st.markdown('</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c2:
            if st.button("Next →", type="primary", use_container_width=True):
                if not prospect_name or not company_name: st.warning("Enter prospect and company name")
                else:
                    st.session_state.call_data = {'call_type': call_type, 'call_date': str(call_date), 'deal_size': deal_size, 'stage': stage, 'prospect_name': prospect_name, 'prospect_title': prospect_title, 'prospect_email': prospect_email, 'prospect_linkedin': prospect_linkedin, 'company_name': company_name, 'company_website': company_website, 'industry': industry, 'headcount': headcount, 'location': location, 'revenue': revenue}
                    st.session_state.wizard_step = 2
                    st.rerun()
    elif step == 2:
        st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
        st.markdown("### 🎙️ Recording")
        input_type = st.radio("Input:", ["📁 Upload", "📝 Paste"], horizontal=True)
        transcript = ""
        if input_type == "📁 Upload":
            f = st.file_uploader("Upload file", type=['mp3', 'wav', 'm4a', 'mp4', 'txt', 'pdf', 'docx', 'vtt', 'srt'])
            if f:
                with st.spinner("Processing..."): transcript = extract_text_from_file(f)
                if transcript and not transcript.startswith("["): st.success(f"✅ {f.name}")
                else: st.warning(transcript)
        else: transcript = st.text_area("Paste transcript:", height=300, placeholder="Salesperson: Hi...\nProspect: Thanks for...")
        st.markdown("---")
        notes = st.text_area("📝 Notes/Questions", height=100, placeholder="Any specific areas to analyze?")
        st.session_state.call_data['notes'] = notes
        st.markdown('</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back", use_container_width=True): st.session_state.wizard_step = 1; st.rerun()
        with c2:
            if st.button("🚀 Analyze", type="primary", use_container_width=True):
                if not transcript: st.warning("Provide transcript")
                else:
                    st.session_state.working_on = "Analyzing..."
                    result, _ = analyze_call(st.session_state.call_data, transcript)
                    st.session_state.working_on = None
                    if not result.startswith("Error"): st.session_state.analysis_result = result; st.rerun()
                    else: st.error(result)

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
