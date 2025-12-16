"""Sharp JD - Professional Job Description Writer with Cross-App Auth"""
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

# Import shared UI components
try:
    from shared_ui import (
        apply_global_styles,
        render_top_banner,
        render_sidebar,
        render_header,
        render_feedback_widget,
        inject_ga4,
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
    GOD_PASSWORD = "G0DHum@n101!!!"
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    APP_URLS = {
        "portal": "https://demo.sharphuman.com", "jd": "https://jd.sharphuman.com",
        "screen": "https://screen.sharphuman.com", "interview": "https://interview.sharphuman.com",
        "outreach": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com",
        "sales": "https://sales.sharphuman.com", "admin": "https://admin.sharphuman.com",
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

def init_session():
    defaults = [
        ('authenticated', False), ('user', None), ('is_god', False), ('session_token', None),
        ('user_plan', 'free'), ('generated_jd', None), ('jd_metadata', None), ('working_on', None),
        ('requirements_text', ''), ('enhanced_jd', None), ('copy_to_create', False),
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
    return f"{base}?token={token}" if base and token else base

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
            return "".join([page.get_text() for page in pdf])
        except:
            return re.sub(r'[^\x20-\x7E\n]', ' ', content.decode('utf-8', errors='ignore'))
    elif file_type in ['docx', 'doc']:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return '\n'.join([p.text for p in doc.paragraphs])
        except:
            return "[DOCX requires python-docx]"
    elif file_type == 'json':
        try:
            data = json.loads(content.decode('utf-8'))
            if isinstance(data, dict):
                for key in ['description', 'job_description', 'requirements', 'content', 'text']:
                    if key in data:
                        return data[key]
            return json.dumps(data, indent=2)
        except:
            return content.decode('utf-8', errors='ignore')
    return content.decode('utf-8', errors='ignore')

# ============================================
# EXPORT FUNCTIONS
# ============================================

def generate_docx_bytes(jd_text, metadata):
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        doc = Document()
        title = doc.add_heading(metadata.get('job_title', 'Job Description'), 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if metadata.get('company'):
            p = doc.add_paragraph(metadata.get('company'))
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()
        for line in jd_text.split('\n'):
            if line.strip():
                doc.add_paragraph(line)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except:
        return None

def generate_html(jd_text, metadata, platform="General"):
    title = metadata.get('job_title', 'Job Description')
    company = metadata.get('company', '')
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', jd_text)
    content = re.sub(r'\n', '<br>', content)
    
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{title}</title>
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;max-width:800px;margin:40px auto;padding:40px;color:#333;line-height:1.6;}}
.header{{border-bottom:3px solid #6366f1;padding-bottom:20px;margin-bottom:30px;}}
h1{{color:#1f2937;margin:0 0 10px;font-size:28px;}}
.company{{color:#6366f1;font-size:18px;font-weight:600;}}
.meta{{color:#6b7280;font-size:14px;margin-top:10px;}}
.footer{{margin-top:40px;padding-top:20px;border-top:1px solid #e5e7eb;color:#9ca3af;font-size:12px;text-align:right;}}
@media print{{body{{margin:20px;padding:20px;}}}}
</style></head><body>
<div class="header"><h1>{title}</h1>{f'<div class="company">{company}</div>' if company else ''}
<div class="meta">{metadata.get('experience_level', '')} | {metadata.get('remote_type', '')} | {metadata.get('industry', '')}</div></div>
<div class="content">{content}</div>
<div class="footer">Generated by Sharp JD | {datetime.now().strftime('%Y-%m-%d')}</div>
</body></html>"""

def generate_ats_json(jd_text, metadata):
    return json.dumps({
        "job_posting": {
            "title": metadata.get('job_title', ''),
            "company": metadata.get('company', ''),
            "location": metadata.get('remote_type', ''),
            "experience_level": metadata.get('experience_level', ''),
            "industry": metadata.get('industry', ''),
            "posted_date": datetime.now().strftime('%Y-%m-%d'),
        },
        "description": {"full_text": jd_text},
        "metadata": {"source": "Sharp JD", "generated_at": datetime.now().isoformat()}
    }, indent=2)

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
        try:
            err = r.json()
            return None, err.get('message', str(err))
        except:
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
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

def delete_jd_history(jd_id):
    try:
        requests.delete(f"{SUPABASE_URL}/rest/v1/jd_history?id=eq.{jd_id}",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=5)
    except: pass

def toggle_favorite(jd_id, is_favorite):
    try:
        requests.patch(f"{SUPABASE_URL}/rest/v1/jd_history?id=eq.{jd_id}",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json"},
            json={"is_favorite": is_favorite}, timeout=5)
    except: pass

def submit_feedback(app, feedback_type, message):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/user_feedback",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": st.session_state.user.get("id") if st.session_state.user else None,
                  "app": app, "feedback_type": feedback_type, "rating": 4, "message": message, "email": get_user_email()}, timeout=5)
        return True
    except: return False

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
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp JD", page_icon="📝", layout="wide")
init_session()
check_url_auth()

# Apply shared UI if available
if USING_SHARED:
    inject_ga4()
    apply_global_styles()
    render_top_banner(show_cta=True, cta_text="Book a Demo")

# Comprehensive styles - hide "key" text, proper theming
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

*, *::before, *::after { font-family: 'Nunito', sans-serif !important; box-sizing: border-box; }

/* App background */
.stApp, [data-testid="stAppViewContainer"] { background: #0a0a0f !important; }
[data-testid="stHeader"] { background: transparent !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0d0d14 !important; border-right: 1px solid rgba(99,102,241,0.2); }
section[data-testid="stSidebar"] > div { background: #0d0d14 !important; }
section[data-testid="stSidebar"] * { color: #e5e5e5 !important; }

/* CRITICAL: Hide orphaned "key" text from Material Icons */
section[data-testid="stSidebar"] > div > div:first-child > div:first-child { display: none !important; }

/* Text colors */
h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
p, span, label, div, li { color: #e5e5e5; }

/* Form inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div,
[data-baseweb="select"] > div { background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: #ffffff !important; border-radius: 8px !important; }

/* Multiselect tags */
[data-baseweb="tag"] { background: rgba(99,102,241,0.3) !important; color: white !important; }

/* Buttons */
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stButton > button:hover { opacity: 0.9; }
.stDownloadButton > button { background: #1a1a2e !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 8px; border-bottom: 1px solid rgba(99,102,241,0.2); }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #9ca3af !important; border: none !important; border-bottom: 2px solid transparent; padding: 12px 20px !important; }
.stTabs [aria-selected="true"] { background: transparent !important; color: #fff !important; border-bottom: 2px solid #6366f1 !important; }

/* Radio */
.stRadio > div { flex-direction: row !important; gap: 12px; flex-wrap: wrap; }
.stRadio > div > label { background: #12121a !important; padding: 10px 16px !important; border-radius: 8px !important; border: 1px solid rgba(99,102,241,0.2) !important; }

/* Checkbox */
.stCheckbox > label { color: #e5e5e5 !important; }

/* File uploader */
[data-testid="stFileUploader"] { background: #12121a !important; border: 1px dashed rgba(99,102,241,0.3) !important; border-radius: 8px !important; padding: 20px !important; }

/* Selectbox/Multiselect dropdown */
[data-baseweb="popover"], [data-baseweb="menu"] { background: #12121a !important; }
[role="option"] { color: #e5e5e5 !important; }
[role="option"]:hover { background: rgba(99,102,241,0.2) !important; }

/* Slider */
.stSlider > div > div { background: rgba(99,102,241,0.3) !important; }

/* Metrics */
[data-testid="stMetricValue"] { color: #fff !important; }
[data-testid="stMetricLabel"] { color: #9ca3af !important; }

/* Success/Error */
.stSuccess { background: rgba(16,185,129,0.1) !important; border: 1px solid #10b981 !important; }
.stError { background: rgba(239,68,68,0.1) !important; border: 1px solid #ef4444 !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid #f59e0b !important; }
.stInfo { background: rgba(99,102,241,0.1) !important; border: 1px solid #6366f1 !important; }

/* Custom */
.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.metric-card { background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)); border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; text-align: center; }
.output-box { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; margin: 16px 0; white-space: pre-wrap; color: #e5e5e5; }
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; z-index: 999; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
.active-app { background: rgba(99,102,241,0.3) !important; border: 1px solid #6366f1 !important; }
</style>""", unsafe_allow_html=True)

# Auth
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;">
            <h1 style="margin:0;">Sharp JD</h1>
            <p style="color:#9ca3af;">AI Job Description Writer</p>
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

# Working status
if st.session_state.working_on:
    st.markdown(f'<div class="status-badge">{st.session_state.working_on}</div>', unsafe_allow_html=True)

# Sidebar - Use shared UI if available
if USING_SHARED:
    render_sidebar(
        current_app="jd",
        user_email=get_user_email(),
        user_plan=st.session_state.get('user_plan', 'free'),
        session_token=st.session_state.get('session_token', '')
    )
else:
    with st.sidebar:
        st.markdown(f"""<div class="user-card">
            <p style="color:#9ca3af;margin:0;font-size:12px;">Logged in as</p>
            <p style="color:#fff;margin:4px 0;font-weight:600;">{get_user_email()}</p>
            <p style="color:#6366f1;margin:0;font-size:12px;text-transform:uppercase;">{st.session_state.get('user_plan','free')} plan</p>
        </div>""", unsafe_allow_html=True)
        
        st.markdown("**Apps**")
        apps = [
            ("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"),
            ("interview", "🎯 Interview"), ("outreach", "🚀 Outreach"), ("content", "✍️ Content"),
            ("sales", "💰 Sales"),
        ]
        for key, label in apps:
            if key == "jd":
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

# Floating feedback at bottom of page (not sidebar)
# Will be added at end of main content

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:30px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:50px;">
    <div><h1 style="margin:0;font-size:28px;">Sharp JD</h1><p style="color:#9ca3af;margin:0;">AI-Powered Job Descriptions</p></div>
</div>""", unsafe_allow_html=True)

# Check for copy_to_create flag
if st.session_state.get('copy_to_create') and st.session_state.get('enhanced_jd'):
    st.session_state.requirements_text = st.session_state.enhanced_jd
    st.session_state.copy_to_create = False
    st.info("✅ Enhanced JD copied to Requirements! Switch to Create JD tab.")

# Tabs
tab_create, tab_import, tab_history = st.tabs(["✏️ Create JD", "📄 Import/Enhance", "📜 History"])

with tab_create:
    st.markdown("### 📋 Job Details")
    
    c1, c2 = st.columns(2)
    with c1:
        job_title = st.text_input("Job Title *", placeholder="e.g. Senior Software Engineer")
        company = st.text_input("Company", placeholder="e.g. Acme Corp")
        experience_level = st.selectbox("Level", ["Entry Level", "Mid Level", "Senior", "Lead", "Manager", "Director", "Executive"])
    
    with c2:
        industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Education", "Media", "Consulting", "Government", "Non-Profit", "Other"])
        remote_type = st.selectbox("Work Type", ["Remote", "Hybrid", "On-site"])
        tone = st.selectbox("Tone", ["Professional", "Casual/Startup", "Formal/Corporate", "Friendly", "Bold/Exciting"])
    
    # User type - Recruiter or Internal HR
    user_type = st.radio("I am a:", ["🏢 Recruiter (Agency)", "👔 Internal HR / TA"], horizontal=True)
    
    st.markdown("### 📝 Requirements")
    
    # Option to load from file OR paste
    req_source = st.radio("Source:", ["📝 Type/Paste", "📄 Upload File"], horizontal=True, key="req_src")
    
    if req_source == "📄 Upload File":
        req_file = st.file_uploader("Upload requirements (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt', 'json'], key="req_upload")
        if req_file:
            st.session_state.requirements_text = extract_text_from_file(req_file)
            st.success(f"✅ Loaded from {req_file.name}")
    
    # Text area with pre-filled content if available
    requirements = st.text_area(
        "Key requirements & responsibilities",
        value=st.session_state.get('requirements_text', ''),
        height=150,
        placeholder="• 5+ years experience\n• Python, AWS\n• Leadership skills...\n\nOr paste an existing JD to build from..."
    )
    
    # Update session state
    st.session_state.requirements_text = requirements
    
    # Options row
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
        st.markdown("---")
        st.markdown("### 📄 Your Job Description")
        
        meta = st.session_state.jd_metadata or {}
        seo = calculate_seo_score(st.session_state.generated_jd, meta)
        words = len(st.session_state.generated_jd.split())
        
        # Stats
        c1, c2, c3 = st.columns(3)
        with c1:
            color = "#10b981" if seo >= 70 else "#f59e0b" if seo >= 50 else "#ef4444"
            st.markdown(f'<div class="metric-card"><p style="color:#9ca3af;margin:0;font-size:12px;">SEO Score</p><p style="color:{color};font-size:28px;font-weight:bold;margin:0;">{seo}/100</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><p style="color:#9ca3af;margin:0;font-size:12px;">Words</p><p style="color:#fff;font-size:28px;font-weight:bold;margin:0;">{words}</p></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><p style="color:#9ca3af;margin:0;font-size:12px;">Characters</p><p style="color:#fff;font-size:28px;font-weight:bold;margin:0;">{len(st.session_state.generated_jd):,}</p></div>', unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown(f'<div class="output-box">{st.session_state.generated_jd}</div>', unsafe_allow_html=True)
        
        # Export
        st.markdown("### 📥 Export")
        exp_c1, exp_c2 = st.columns(2)
        with exp_c1:
            export_platform = st.selectbox("Platform:", ["General", "LinkedIn", "Indeed", "Company Careers", "Glassdoor"])
        with exp_c2:
            export_format = st.selectbox("Format:", ["Plain Text (.txt)", "HTML/PDF (.html)", "Word (.docx)", "Markdown (.md)", "ATS JSON (.json)"])
        
        file_title = meta.get('job_title', 'job_description').lower().replace(' ', '_')
        
        if "Plain Text" in export_format:
            st.download_button("📥 Download", st.session_state.generated_jd, f"{file_title}.txt", "text/plain", use_container_width=True)
        elif "HTML" in export_format:
            st.download_button("📥 Download", generate_html(st.session_state.generated_jd, meta, export_platform), f"{file_title}.html", "text/html", use_container_width=True)
        elif "Word" in export_format:
            docx = generate_docx_bytes(st.session_state.generated_jd, meta)
            if docx:
                st.download_button("📥 Download", docx, f"{file_title}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            else:
                st.warning("DOCX requires python-docx")
        elif "Markdown" in export_format:
            st.download_button("📥 Download", st.session_state.generated_jd, f"{file_title}.md", "text/markdown", use_container_width=True)
        elif "JSON" in export_format:
            st.download_button("📥 Download", generate_ats_json(st.session_state.generated_jd, meta), f"{file_title}.json", "application/json", use_container_width=True)
        
        # Actions
        st.markdown("### 💾 Actions")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("💾 Save to History", use_container_width=True):
                st.session_state.working_on = "Saving..."
                saved, err = save_jd_to_history(meta, st.session_state.generated_jd, seo, meta.get('tokens_used', 0))
                st.session_state.working_on = None
                if saved:
                    st.success("✅ Saved!")
                else:
                    st.error(f"Save failed: {err}")
        with c2:
            st.link_button("📤 Open in Screener", build_app_url("screen"), use_container_width=True)
        with c3:
            if st.button("🔄 Start New", use_container_width=True):
                st.session_state.generated_jd = None
                st.session_state.jd_metadata = None
                st.session_state.requirements_text = ''
                st.rerun()
        
        # Refine
        st.markdown("---")
        st.markdown("### ✏️ Refine")
        refine = st.text_input("What to change?", placeholder="Make shorter, add Python, more casual...")
        if st.button("✨ Apply Changes", use_container_width=True):
            if refine:
                st.session_state.working_on = "Refining..."
                with st.spinner("Refining..."):
                    result, _ = call_claude(f"Modify this JD:\n\n{st.session_state.generated_jd}\n\nChanges: {refine}\n\nOutput only the modified JD.")
                    st.session_state.working_on = None
                    if not result.startswith("Error"):
                        st.session_state.generated_jd = result
                        st.rerun()
                    else:
                        st.error(result)

with tab_import:
    st.markdown("### 📄 Import & Enhance")
    st.markdown("Upload or paste an existing JD to enhance, optimize, or reformat.")
    
    src = st.radio("Source:", ["📄 Upload", "📝 Paste", "🔗 JSON/ATS"], horizontal=True, key="imp_src")
    
    imported = ""
    if src == "📄 Upload":
        f = st.file_uploader("Upload JD (PDF, DOCX, TXT, JSON)", type=['pdf', 'docx', 'txt', 'json'], key="imp_file")
        if f:
            imported = extract_text_from_file(f)
            st.success(f"✅ Loaded {f.name}")
            if st.checkbox("Preview", key="imp_preview"):
                st.text_area("Content:", imported[:2000], height=150, disabled=True)
    elif src == "🔗 JSON/ATS":
        imported = st.text_area("Paste ATS JSON:", height=150, placeholder='{"title": "...", "description": "..."}')
        if imported:
            try:
                data = json.loads(imported)
                st.success("✅ Valid JSON")
                # Extract description
                for key in ['description', 'job_description', 'content']:
                    if key in data:
                        imported = data[key]
                        break
            except:
                pass
    else:
        imported = st.text_area("Paste existing JD:", height=200, placeholder="Paste job description here...")
    
    if imported:
        st.markdown("---")
        st.markdown("### 🎯 Enhancement Options")
        
        # Multi-select for actions
        actions = st.multiselect(
            "Select enhancements (multiple allowed):",
            ["Rewrite & Improve", "Optimize for ATS/SEO", "Make Concise", "Expand Detail", "Change Tone", "Add Missing Sections"],
            default=["Rewrite & Improve"]
        )
        
        if "Change Tone" in actions:
            new_tone = st.selectbox("New tone:", ["Professional", "Casual/Startup", "Formal", "Friendly", "Bold"])
        else:
            new_tone = "Professional"
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✨ Enhance JD", type="primary", use_container_width=True):
                if actions:
                    st.session_state.working_on = "Enhancing..."
                    
                    action_text = ", ".join(actions)
                    prompt = f"""Enhance this job description with the following actions: {action_text}

{"Change the tone to: " + new_tone if "Change Tone" in actions else ""}

## ORIGINAL JD:
{imported}

## INSTRUCTIONS:
- Apply ALL selected enhancements
- Keep the core job requirements intact
- Output a polished, ready-to-use job description
- If "Add Missing Sections" is selected, add: About Company, About Role, Responsibilities, Requirements, Benefits, How to Apply

Output only the enhanced job description."""

                    with st.spinner("Enhancing..."):
                        result, _ = call_claude(prompt)
                        st.session_state.working_on = None
                        if not result.startswith("Error"):
                            st.session_state.enhanced_jd = result
                            st.rerun()
                        else:
                            st.error(result)
                else:
                    st.warning("Select at least one enhancement")
        
        with c2:
            if st.button("📋 Copy to Create Tab", use_container_width=True):
                st.session_state.requirements_text = imported
                st.success("✅ Copied! Switch to Create JD tab.")
    
    # Show enhanced result
    if st.session_state.get('enhanced_jd'):
        st.markdown("---")
        st.markdown("### ✅ Enhanced JD")
        st.markdown(f'<div class="output-box">{st.session_state.enhanced_jd}</div>', unsafe_allow_html=True)
        
        # Actions for enhanced JD
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button("📥 Download", st.session_state.enhanced_jd, "enhanced_jd.txt", "text/plain", use_container_width=True)
        with c2:
            if st.button("📋 → Create Tab", use_container_width=True, key="copy_enhanced"):
                st.session_state.requirements_text = st.session_state.enhanced_jd
                st.session_state.copy_to_create = True
                st.rerun()
        with c3:
            if st.button("💾 Save to History", use_container_width=True, key="save_enhanced"):
                st.session_state.working_on = "Saving..."
                saved, err = save_jd_to_history({"job_title": "Enhanced JD"}, st.session_state.enhanced_jd, 70, 0)
                st.session_state.working_on = None
                if saved:
                    st.success("✅ Saved!")
                else:
                    st.error(f"Failed: {err}")
        with c4:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.enhanced_jd = None
                st.rerun()

with tab_history:
    st.markdown("### 📜 Your JD History")
    
    if st.session_state.user.get("id") == "god":
        st.info("History not available in GOD mode. Log in with a regular account.")
    else:
        history = get_jd_history(50)
        
        if not history:
            st.markdown('<p style="text-align:center;color:#6b7280;padding:40px;">No saved JDs yet. Create and save a JD to see it here!</p>', unsafe_allow_html=True)
        else:
            # Search and filter
            c1, c2 = st.columns([3, 1])
            with c1:
                search = st.text_input("🔍 Search", placeholder="Filter by job title...", label_visibility="collapsed")
            with c2:
                show_favs = st.checkbox("⭐ Favorites")
            
            # Filter
            filtered = history
            if search:
                filtered = [h for h in filtered if search.lower() in (h.get("job_title") or "").lower()]
            if show_favs:
                filtered = [h for h in filtered if h.get("is_favorite")]
            
            if not filtered:
                st.info("No matching JDs found.")
            else:
                for item in filtered:
                    is_fav = item.get("is_favorite", False)
                    title = item.get('job_title', 'Untitled')
                    company = item.get('company', '')
                    date = item.get('created_at', '')[:10] if item.get('created_at') else ''
                    score = item.get('seo_ats_score', '?')
                    level = item.get('experience_level', '')
                    remote = item.get('remote_type', '')
                    
                    st.markdown(f"""<div style="background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:16px;margin:8px 0;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <strong style="font-size:16px;">{'⭐ ' if is_fav else ''}{title}</strong>
                                {f'<span style="color:#9ca3af;margin-left:8px;">@ {company}</span>' if company else ''}
                            </div>
                            <span style="color:#6366f1;font-size:14px;">{date}</span>
                        </div>
                        <p style="color:#9ca3af;margin:8px 0;font-size:13px;">Score: {score}/100 | {level} | {remote}</p>
                    </div>""", unsafe_allow_html=True)
                    
                    # Actions
                    c1, c2, c3, c4, c5 = st.columns(5)
                    with c1:
                        if st.button("📋 Load", key=f"load_{item['id']}", use_container_width=True):
                            st.session_state.generated_jd = item.get("generated_jd")
                            st.session_state.jd_metadata = item
                            st.rerun()
                    with c2:
                        if st.button("📝 → Create", key=f"tocreate_{item['id']}", use_container_width=True):
                            st.session_state.requirements_text = item.get("generated_jd", "")
                            st.info("Copied to Requirements! Switch to Create tab.")
                    with c3:
                        fav_label = "★" if is_fav else "☆"
                        if st.button(fav_label, key=f"fav_{item['id']}", use_container_width=True):
                            toggle_favorite(item['id'], not is_fav)
                            st.rerun()
                    with c4:
                        st.download_button("📥", item.get("generated_jd", ""), f"jd_{item['id'][:8]}.txt", key=f"dl_{item['id']}", use_container_width=True)
                    with c5:
                        if st.button("🗑️", key=f"del_{item['id']}", use_container_width=True):
                            delete_jd_history(item['id'])
                            st.rerun()
                    
                    st.markdown("---")

# ============================================
# FLOATING FEEDBACK (Bottom of page)
# ============================================
st.markdown("---")
with st.container():
    fb_col1, fb_col2, fb_col3 = st.columns([2, 1, 1])
    with fb_col3:
        if st.checkbox("💬 Send Feedback", key="show_fb"):
            fb_type = st.selectbox("Type", ["Bug", "Feature", "General"], key="fb_type")
            fb_msg = st.text_area("Message", height=100, key="fb_msg", placeholder="Your feedback...")
            if st.button("Submit Feedback", key="fb_submit"):
                if fb_msg:
                    submit_feedback("jd", fb_type.lower(), fb_msg)
                    st.success("Thanks! 🙏")
