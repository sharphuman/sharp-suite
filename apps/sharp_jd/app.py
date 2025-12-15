"""Sharp JD - Professional Job Description Writer with Cross-App Auth"""
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
                "device_hash": "jd",
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
        ('generated_jd', None),
        ('jd_metadata', None),
        ('current_status', None),
        ('imported_jd_text', None),
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
# FILE PROCESSING FUNCTIONS
# ============================================

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded files (PDF, DOCX, TXT, JSON)."""
    file_type = uploaded_file.name.split('.')[-1].lower()
    content = uploaded_file.read()
    
    if file_type == 'txt':
        return content.decode('utf-8', errors='ignore')
    
    elif file_type == 'pdf':
        try:
            import fitz  # PyMuPDF
            pdf = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in pdf:
                text += page.get_text()
            return text
        except ImportError:
            # Fallback - basic extraction
            text = content.decode('utf-8', errors='ignore')
            clean_text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
            return clean_text
    
    elif file_type in ['docx', 'doc']:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return '\n'.join([para.text for para in doc.paragraphs])
        except ImportError:
            return "[DOCX parsing requires python-docx library]"
    
    elif file_type == 'json':
        try:
            data = json.loads(content.decode('utf-8'))
            # Handle various ATS JSON formats
            if isinstance(data, dict):
                # Look for common JD fields
                jd_text = ""
                for key in ['description', 'job_description', 'jd', 'content', 'text', 'body']:
                    if key in data:
                        jd_text = data[key]
                        break
                if not jd_text:
                    # Try to extract title + requirements
                    parts = []
                    if data.get('title') or data.get('job_title'):
                        parts.append(f"Job Title: {data.get('title') or data.get('job_title')}")
                    if data.get('company'):
                        parts.append(f"Company: {data.get('company')}")
                    if data.get('requirements'):
                        parts.append(f"Requirements: {data.get('requirements')}")
                    if data.get('responsibilities'):
                        parts.append(f"Responsibilities: {data.get('responsibilities')}")
                    if data.get('qualifications'):
                        parts.append(f"Qualifications: {data.get('qualifications')}")
                    if data.get('skills'):
                        skills = data.get('skills')
                        if isinstance(skills, list):
                            skills = ', '.join(skills)
                        parts.append(f"Skills: {skills}")
                    jd_text = '\n\n'.join(parts) if parts else json.dumps(data, indent=2)
                return jd_text
            return json.dumps(data, indent=2)
        except:
            return content.decode('utf-8', errors='ignore')
    
    return content.decode('utf-8', errors='ignore')

def parse_ats_json(json_text):
    """Parse JSON from various ATS systems."""
    try:
        data = json.loads(json_text)
        
        # Common ATS formats
        jd_info = {
            'title': '',
            'company': '',
            'description': '',
            'requirements': '',
            'responsibilities': '',
            'skills': [],
            'experience_level': '',
            'location': '',
            'salary': ''
        }
        
        if isinstance(data, dict):
            # Greenhouse format
            if 'job' in data:
                data = data['job']
            
            # Extract fields
            jd_info['title'] = data.get('title') or data.get('job_title') or data.get('name', '')
            jd_info['company'] = data.get('company') or data.get('company_name') or data.get('organization', '')
            jd_info['description'] = data.get('description') or data.get('job_description') or data.get('content', '')
            jd_info['requirements'] = data.get('requirements') or data.get('qualifications') or ''
            jd_info['responsibilities'] = data.get('responsibilities') or data.get('duties') or ''
            
            skills = data.get('skills') or data.get('required_skills') or []
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(',')]
            jd_info['skills'] = skills
            
            jd_info['experience_level'] = data.get('experience_level') or data.get('seniority') or ''
            jd_info['location'] = data.get('location') or data.get('office_location') or ''
            jd_info['salary'] = data.get('salary') or data.get('compensation') or ''
        
        return jd_info
    except:
        return None

# ============================================
# HISTORY FUNCTIONS
# ============================================

def save_jd_to_history(metadata, generated_jd, seo_score, tokens_used):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god":
        return None
    
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/jd_history",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json={
                "user_id": user_id,
                "job_title": metadata.get("job_title"),
                "company": metadata.get("company"),
                "user_type": metadata.get("user_type"),
                "experience_level": metadata.get("experience_level"),
                "remote_type": metadata.get("remote_type"),
                "industry": metadata.get("industry"),
                "platform": metadata.get("platform"),
                "output_format": metadata.get("output_format"),
                "tone": metadata.get("tone"),
                "word_count": metadata.get("word_count"),
                "include_salary": metadata.get("include_salary"),
                "include_benefits": metadata.get("include_benefits"),
                "include_diversity": metadata.get("include_diversity"),
                "seo_optimized": metadata.get("seo_optimized"),
                "requirements": metadata.get("requirements"),
                "generated_jd": generated_jd,
                "seo_ats_score": seo_score,
                "tokens_used": tokens_used
            },
            timeout=10
        )
        if r.status_code in [200, 201]:
            return r.json()[0] if r.json() else None
    except:
        pass
    return None

def get_jd_history(limit=20):
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

def toggle_favorite(jd_id, is_favorite):
    try:
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/jd_history?id=eq.{jd_id}",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json"
            },
            json={"is_favorite": is_favorite},
            timeout=5
        )
    except:
        pass

def delete_jd_history(jd_id):
    try:
        requests.delete(
            f"{SUPABASE_URL}/rest/v1/jd_history?id=eq.{jd_id}",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_ANON_KEY}"},
            timeout=5
        )
    except:
        pass

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
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=3000):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", 
                          headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, 
                          json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, 
                          timeout=120)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            tokens_used = (len(prompt) + len(text)) // 4
            if st.session_state.user:
                log_usage(
                    st.session_state.user.get("id"),
                    st.session_state.get("session_token"),
                    "jd",
                    "generate_jd",
                    tokens_used
                )
            return text, tokens_used
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0

def calculate_seo_ats_score(jd_text, metadata):
    score = 50
    jd_lower = jd_text.lower()
    
    if metadata.get("job_title", "").lower() in jd_lower:
        score += 10
    
    section_keywords = ["responsibilities", "requirements", "qualifications", "benefits", "about"]
    sections_found = sum(1 for kw in section_keywords if kw in jd_lower)
    score += min(sections_found * 2, 10)
    
    word_count = len(jd_text.split())
    if 300 <= word_count <= 800:
        score += 10
    elif 200 <= word_count <= 1000:
        score += 5
    
    action_verbs = ["manage", "lead", "develop", "create", "design", "build", "implement", "drive", "collaborate"]
    if any(verb in jd_lower for verb in action_verbs):
        score += 5
    
    buzzwords = ["synergy", "leverage", "paradigm", "holistic", "bandwidth"]
    if sum(1 for bw in buzzwords if bw in jd_lower) > 2:
        score -= 5
    
    if metadata.get("include_salary"):
        score += 5
    
    if metadata.get("seo_optimized"):
        score += 5
    
    if metadata.get("include_diversity") or "equal opportunity" in jd_lower or "diversity" in jd_lower:
        score += 5
    
    return min(max(score, 1), 100)

# ============================================
# UI COMPONENTS
# ============================================

def render_auth():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}.stTextInput>div>div>input{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}.stTabs [data-baseweb="tab-list"]{background:#12121a;}.stTabs [aria-selected="true"]{background:rgba(99,102,241,0.3)!important;color:white!important;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:40px 0;"><img src="https://sharphuman.com/logo1-3.png" style="width:70px;margin-bottom:16px;"><h1 style="color:white;">Sharp JD</h1><p style="color:#9ca3af;">Job Description Writer</p></div>""", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        with tab1:
            e = st.text_input("Email", key="le")
            p = st.text_input("Password", type="password", key="lp")
            if st.button("Log In", use_container_width=True):
                if p == GOD_PASSWORD:
                    token = secrets.token_urlsafe(32)
                    st.session_state.authenticated = True
                    st.session_state.is_god = True
                    st.session_state.user = {"email": "GOD", "id": "god"}
                    st.session_state.user_plan = "god"
                    st.session_state.session_token = token
                    st.rerun()
                elif e and p:
                    r = supabase_sign_in(e, p)
                    if r["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = r["user"]
                        st.session_state.session_token = r.get("session_token")
                        st.rerun()
                    else:
                        st.error(r["message"])
            st.markdown("<p style='text-align:center;color:#6b7280;'>— or —</p>", unsafe_allow_html=True)
            me = st.text_input("Magic link", key="me", label_visibility="collapsed", placeholder="Email")
            if st.button("✨ Magic Link", use_container_width=True, key="ml"):
                if me:
                    r = supabase_magic_link(me)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
        with tab2:
            se = st.text_input("Email", key="se")
            sp = st.text_input("Password", type="password", key="sp")
            sc = st.text_input("Confirm", type="password", key="sc")
            if st.button("Create Account", use_container_width=True):
                if sp != sc:
                    st.error("Passwords don't match")
                elif len(sp) < 6:
                    st.warning("6+ chars")
                elif se and sp:
                    r = supabase_sign_up(se, sp)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])

def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:12px;background:rgba(99,102,241,0.1);border-radius:8px;margin-bottom:16px;'>
            <p style='color:#9ca3af;margin:0;font-size:0.75rem;'>Logged in as</p>
            <p style='color:white;margin:0;font-weight:600;'>{get_user_email()}</p>
            <p style='color:#6366f1;margin:0;font-size:0.75rem;text-transform:uppercase;'>{st.session_state.get('user_plan', 'free')} plan</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🧭 Apps")
        
        apps = [
            ("portal", "🏠 Portal"),
            ("jd", "📝 JD Writer"),
            ("screen", "🔍 CV Screener"),
            ("interview", "🎯 Interview"),
            ("source", "🎣 Sourcing"),
            ("content", "✍️ Content"),
            ("sales", "💰 Sales"),
            ("reach", "🚀 Reach"),
            ("assistant", "🤖 Assistant"),
        ]
        
        for app_key, label in apps:
            if app_key == "jd":
                st.button(f"{label} ◀", disabled=True, use_container_width=True)
            else:
                url = build_app_url(app_key)
                st.link_button(label, url, use_container_width=True)
        
        if st.session_state.get("is_god") or st.session_state.get("user_plan") == "god":
            st.markdown("---")
            st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def render_feedback_modal():
    with st.expander("💬 Send Feedback", expanded=False):
        feedback_type = st.selectbox("Type", ["General", "Bug Report", "Feature Request", "Complaint", "Praise"], key="fb_type")
        rating = st.slider("Rating", 1, 5, 4, key="fb_rating")
        message = st.text_area("Your feedback", placeholder="Tell us what you think...", key="fb_msg")
        if st.button("Submit Feedback", key="fb_submit"):
            if message:
                if submit_feedback("jd", feedback_type.lower().replace(" ", "_"), rating, message):
                    st.success("Thanks for your feedback! 🙏")
                else:
                    st.error("Failed to submit. Please try again.")
            else:
                st.warning("Please enter a message")

def render_history_sidebar():
    st.markdown("---")
    st.markdown("#### 📜 Recent JDs")
    
    history = get_jd_history(10)
    
    if not history:
        st.caption("No saved JDs yet")
        return
    
    for item in history:
        title = item.get("job_title", "Untitled")[:25]
        date = item.get("created_at", "")[:10]
        is_fav = "⭐" if item.get("is_favorite") else ""
        if st.button(f"{is_fav} {title}", key=f"hist_{item['id']}", use_container_width=True, help=date):
            st.session_state.generated_jd = item.get("generated_jd")
            st.session_state.jd_metadata = item
            st.rerun()

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp JD", page_icon="📝", layout="wide")
init_session()
check_url_auth()

if not st.session_state.authenticated:
    render_auth()
    st.stop()

# Main styles
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%); }
h1,h2,h3 { color: white !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > div {
    background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important;
}
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; }
.output-box { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 24px; margin: 16px 0; }
p, span, label { color: #e5e5e5 !important; }
.status-badge { background: rgba(99,102,241,0.2); border: 1px solid rgba(99,102,241,0.4); border-radius: 8px; padding: 8px 16px; display: inline-block; }
</style>""", unsafe_allow_html=True)

# Sidebar
render_sidebar()
with st.sidebar:
    render_history_sidebar()
    st.markdown("---")
    render_feedback_modal()

# Header with status
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;">
        <img src="https://sharphuman.com/logo1-3.png" style="width:45px;">
        <div><h1 style="margin:0;">Sharp JD</h1><p style="color:#9ca3af;margin:0;">AI-Powered Job Descriptions</p></div>
    </div>""", unsafe_allow_html=True)
with header_col2:
    if st.session_state.current_status:
        st.markdown(f"""<div style="text-align:right;padding-top:20px;">
            <div class="status-badge">✨ {st.session_state.current_status}</div>
        </div>""", unsafe_allow_html=True)

# Main tabs
tab_create, tab_import, tab_history = st.tabs(["✏️ Create JD", "📄 Import/Enhance JD", "📜 History"])

with tab_create:
    # Row 1: Basic Info
    st.markdown("### 📋 Basic Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        job_title = st.text_input("Job Title *", placeholder="e.g. Senior Software Engineer")
        company = st.text_input("Company Name", placeholder="e.g. Acme Corp")
    
    with col2:
        user_type = st.selectbox("I am a:", ["Recruiter (Agency)", "Internal HR / TA"])
        experience_level = st.selectbox("Experience Level", ["Entry Level", "Mid Level", "Senior", "Lead", "Manager", "Director", "Executive"])
    
    with col3:
        industry = st.selectbox("Industry", [
            "Technology", "Healthcare", "Finance", "Retail", "Manufacturing", 
            "Education", "Media", "Consulting", "Government", "Non-Profit", "Other"
        ])
        remote_type = st.selectbox("Work Type", ["Remote", "Hybrid", "On-site"])

    # Row 2: Requirements
    st.markdown("### 📝 Requirements & Details")
    requirements = st.text_area(
        "Key Requirements & Responsibilities", 
        height=120,
        placeholder="• 5+ years Python experience\n• Team leadership skills\n• Cloud platform expertise (AWS/GCP)\n• Strong communication skills..."
    )

    # Row 3: Output Settings
    st.markdown("### ⚙️ Output Settings")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        platform = st.selectbox("Target Platform", [
            "LinkedIn", "Indeed", "Company Careers Page", "Glassdoor", 
            "ZipRecruiter", "Monster", "General/Multi-platform"
        ])
    
    with col2:
        output_format = st.selectbox("Output Format", [
            "Plain Text", "ATS-Ready HTML", "Markdown"
        ])
    
    with col3:
        tone = st.selectbox("Tone", ["Professional", "Casual/Startup", "Formal/Corporate", "Friendly", "Bold/Exciting"])
    
    with col4:
        word_count = st.slider("Target Word Count", 200, 1200, 500, step=50)

    # Row 4: Options
    st.markdown("### 🎯 Include Sections")
    opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)
    
    with opt_col1:
        include_salary = st.checkbox("💰 Salary Range", value=False)
    with opt_col2:
        include_benefits = st.checkbox("🎁 Benefits Section", value=True)
    with opt_col3:
        include_diversity = st.checkbox("🌈 Diversity Statement", value=True)
    with opt_col4:
        seo_optimized = st.checkbox("🔍 SEO Optimized", value=True)

    # Generate Button
    st.markdown("---")
    
    if st.button("📝 Generate Job Description", type="primary", use_container_width=True):
        if not job_title:
            st.warning("Please enter a job title")
        else:
            st.session_state.current_status = "Crafting your JD..."
            
            user_context = "an external recruiter at a staffing agency" if "Recruiter" in user_type else "an internal HR/TA professional"
            
            format_instructions = {
                "Plain Text": "Use plain text formatting with clear section headers.",
                "ATS-Ready HTML": "Format as clean HTML that's optimized for ATS parsing. Use semantic tags like <h2>, <h3>, <ul>, <li>.",
                "Markdown": "Format using Markdown with headers (##), bullet points, and bold text."
            }
            
            platform_tips = {
                "LinkedIn": "Optimize for LinkedIn's job posting format. Keep it scannable with short paragraphs. Use industry keywords for search visibility.",
                "Indeed": "Front-load important information. Indeed users scan quickly. Include salary if possible for better visibility.",
                "Company Careers Page": "Can be more detailed and branded. Include company culture and values.",
                "Glassdoor": "Be transparent and detailed. Glassdoor users research thoroughly.",
                "General/Multi-platform": "Create a versatile JD that works across multiple platforms."
            }
            
            prompt = f"""You are an expert job description writer. Write a compelling job description with the following specifications:

**Context:** I am {user_context} writing this JD.

**Job Details:**
- Title: {job_title}
- Company: {company or "A growing company"}
- Experience Level: {experience_level}
- Industry: {industry}
- Work Type: {remote_type}

**Requirements provided:**
{requirements or "Standard requirements for this role level"}

**Output Specifications:**
- Target Platform: {platform}
- {platform_tips.get(platform, "")}
- Format: {output_format}
- {format_instructions.get(output_format, "")}
- Tone: {tone}
- Target Length: Approximately {word_count} words

**Sections to Include:**
- About the Company (brief, compelling)
- About the Role
- Key Responsibilities (5-7 bullet points)
- Requirements (Must-have and Nice-to-have separated)
{"- Salary Range: Include a placeholder like '$X - $Y based on experience'" if include_salary else ""}
{"- Benefits & Perks section" if include_benefits else ""}
{"- Equal Opportunity / Diversity statement" if include_diversity else ""}
- How to Apply

{"**SEO Optimization:** Include relevant industry keywords naturally throughout. Optimize for job board search algorithms." if seo_optimized else ""}

Write the job description now. Make it compelling, clear, and professional."""

            with st.spinner("✨ Crafting your job description... Analyzing role requirements and industry standards."):
                result, tokens = call_claude(prompt, max_tokens=3000)
                
                if not result.startswith("Error"):
                    metadata = {
                        "job_title": job_title,
                        "company": company,
                        "user_type": user_type,
                        "experience_level": experience_level,
                        "remote_type": remote_type,
                        "industry": industry,
                        "platform": platform,
                        "output_format": output_format,
                        "tone": tone,
                        "word_count": word_count,
                        "include_salary": include_salary,
                        "include_benefits": include_benefits,
                        "include_diversity": include_diversity,
                        "seo_optimized": seo_optimized,
                        "requirements": requirements
                    }
                    
                    st.session_state.generated_jd = result
                    st.session_state.jd_metadata = metadata
                    st.session_state.current_status = None
                    st.rerun()
                else:
                    st.error(result)
                    st.session_state.current_status = None

    # Display Generated JD
    if st.session_state.generated_jd:
        st.markdown("---")
        st.markdown("### 📄 Generated Job Description")
        
        seo_score = calculate_seo_ats_score(st.session_state.generated_jd, st.session_state.jd_metadata or {})
        word_count_actual = len(st.session_state.generated_jd.split())
        char_count = len(st.session_state.generated_jd)
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            score_color = "#10b981" if seo_score >= 70 else "#f59e0b" if seo_score >= 50 else "#ef4444"
            st.markdown(f"""<div style="text-align:center;">
                <p style="color:#9ca3af;margin:0;font-size:0.75rem;">SEO/ATS Score</p>
                <p style="color:{score_color};font-size:1.5rem;font-weight:bold;margin:0;">{seo_score}/100</p>
            </div>""", unsafe_allow_html=True)
        with stat_col2:
            st.markdown(f"""<div style="text-align:center;">
                <p style="color:#9ca3af;margin:0;font-size:0.75rem;">Word Count</p>
                <p style="color:white;font-size:1.5rem;font-weight:bold;margin:0;">{word_count_actual}</p>
            </div>""", unsafe_allow_html=True)
        with stat_col3:
            st.markdown(f"""<div style="text-align:center;">
                <p style="color:#9ca3af;margin:0;font-size:0.75rem;">Characters</p>
                <p style="color:white;font-size:1.5rem;font-weight:bold;margin:0;">{char_count:,}</p>
            </div>""", unsafe_allow_html=True)
        with stat_col4:
            st.markdown(f"""<div style="text-align:center;">
                <p style="color:#9ca3af;margin:0;font-size:0.75rem;">Format</p>
                <p style="color:white;font-size:1rem;font-weight:bold;margin:0;">{st.session_state.jd_metadata.get('output_format', 'Plain Text') if st.session_state.jd_metadata else 'Plain Text'}</p>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown(f'<div class="output-box">{st.session_state.generated_jd}</div>', unsafe_allow_html=True)
        
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
        
        with btn_col1:
            fmt = st.session_state.jd_metadata.get('output_format', 'Plain Text') if st.session_state.jd_metadata else 'Plain Text'
            ext = ".html" if "HTML" in fmt else ".md" if "Markdown" in fmt else ".txt"
            mime = "text/html" if "HTML" in fmt else "text/markdown" if "Markdown" in fmt else "text/plain"
            
            st.download_button(
                "📥 Download",
                st.session_state.generated_jd,
                file_name=f"job_description_{job_title.lower().replace(' ', '_') if job_title else 'jd'}{ext}",
                mime=mime,
                use_container_width=True
            )
        
        with btn_col2:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.code(st.session_state.generated_jd, language=None)
                st.info("👆 Select all and copy (Ctrl+A, Ctrl+C)")
        
        with btn_col3:
            if st.button("💾 Save to History", use_container_width=True):
                if st.session_state.user.get("id") != "god":
                    saved = save_jd_to_history(
                        st.session_state.jd_metadata or {},
                        st.session_state.generated_jd,
                        seo_score,
                        0
                    )
                    if saved:
                        st.success("Saved to history! ✓")
                    else:
                        st.error("Failed to save")
                else:
                    st.warning("History not available in GOD mode")
        
        with btn_col4:
            if st.button("🔄 Start New", use_container_width=True):
                st.session_state.generated_jd = None
                st.session_state.jd_metadata = None
                st.rerun()
        
        st.markdown("---")
        st.markdown("### ✏️ Refine This JD")
        
        refine_prompt = st.text_input(
            "What would you like to change?",
            placeholder="e.g. Make it shorter, add more technical requirements, change tone to more casual..."
        )
        
        if st.button("✨ Apply Changes", use_container_width=True):
            if refine_prompt:
                st.session_state.current_status = "Refining..."
                
                refine_full_prompt = f"""Here is a job description:

{st.session_state.generated_jd}

Please modify it according to this request: {refine_prompt}

Keep the same general structure and format, but apply the requested changes. Output only the modified job description."""

                with st.spinner("✨ Applying your changes..."):
                    refined, _ = call_claude(refine_full_prompt)
                    if not refined.startswith("Error"):
                        st.session_state.generated_jd = refined
                        st.session_state.current_status = None
                        st.rerun()
                    else:
                        st.error(refined)
            else:
                st.warning("Please describe what you'd like to change")

with tab_import:
    st.markdown("### 📄 Import & Enhance Existing JD")
    st.markdown("Upload or paste an existing job description to enhance, reformat, or optimize it.")
    
    import_source = st.radio("Import Source:", ["📄 Upload File", "📝 Paste Text", "🔗 JSON/ATS Format"], horizontal=True)
    
    imported_text = ""
    imported_metadata = {}
    
    if import_source == "📄 Upload File":
        uploaded_jd = st.file_uploader(
            "Upload JD (PDF, DOCX, TXT, JSON)",
            type=['pdf', 'docx', 'doc', 'txt', 'json'],
            key="jd_file_upload"
        )
        if uploaded_jd:
            imported_text = extract_text_from_file(uploaded_jd)
            st.success(f"✅ Extracted {len(imported_text)} characters from {uploaded_jd.name}")
            with st.expander("Preview Extracted Text"):
                st.text(imported_text[:2000] + "..." if len(imported_text) > 2000 else imported_text)
    
    elif import_source == "🔗 JSON/ATS Format":
        st.markdown("Paste JSON from ATS systems like Greenhouse, Lever, Workday, etc.")
        json_input = st.text_area(
            "Paste JSON:",
            height=200,
            placeholder='{"title": "Software Engineer", "company": "Acme Corp", "description": "...", "requirements": "...", "skills": ["Python", "AWS"]}'
        )
        if json_input:
            parsed = parse_ats_json(json_input)
            if parsed:
                st.success("✅ Successfully parsed ATS JSON")
                imported_metadata = parsed
                
                # Build text from parsed data
                parts = []
                if parsed.get('title'):
                    parts.append(f"**Job Title:** {parsed['title']}")
                if parsed.get('company'):
                    parts.append(f"**Company:** {parsed['company']}")
                if parsed.get('description'):
                    parts.append(f"\n{parsed['description']}")
                if parsed.get('requirements'):
                    parts.append(f"\n**Requirements:**\n{parsed['requirements']}")
                if parsed.get('responsibilities'):
                    parts.append(f"\n**Responsibilities:**\n{parsed['responsibilities']}")
                if parsed.get('skills'):
                    parts.append(f"\n**Skills:** {', '.join(parsed['skills'])}")
                
                imported_text = '\n'.join(parts)
                
                with st.expander("Parsed Fields"):
                    for k, v in parsed.items():
                        if v:
                            st.markdown(f"**{k}:** {v}")
            else:
                st.error("Could not parse JSON. Please check the format.")
    
    else:
        imported_text = st.text_area(
            "Paste existing JD:",
            height=250,
            placeholder="Paste your existing job description here..."
        )
    
    if imported_text:
        st.markdown("---")
        st.markdown("### 🎯 Enhancement Options")
        
        enh_col1, enh_col2 = st.columns(2)
        
        with enh_col1:
            enhance_action = st.selectbox("What would you like to do?", [
                "🔄 Rewrite & Improve",
                "📊 Optimize for ATS/SEO",
                "✂️ Make More Concise",
                "📝 Expand with More Detail",
                "🎨 Change Tone",
                "🔀 Reformat for Platform"
            ])
            
            if enhance_action == "🎨 Change Tone":
                new_tone = st.selectbox("New tone:", ["Professional", "Casual/Startup", "Formal/Corporate", "Friendly", "Bold/Exciting"])
            elif enhance_action == "🔀 Reformat for Platform":
                target_platform = st.selectbox("Target platform:", ["LinkedIn", "Indeed", "Company Careers", "Glassdoor"])
        
        with enh_col2:
            output_fmt = st.selectbox("Output Format:", ["Plain Text", "ATS-Ready HTML", "Markdown"], key="enhance_fmt")
            enhance_word_target = st.slider("Target Word Count:", 200, 1200, 500, step=50, key="enhance_words")
        
        additional_instructions = st.text_input(
            "Additional instructions (optional):",
            placeholder="e.g. Add a remote work section, emphasize Python skills, include salary range..."
        )
        
        if st.button("✨ Enhance JD", type="primary", use_container_width=True):
            st.session_state.current_status = "Enhancing..."
            
            action_prompts = {
                "🔄 Rewrite & Improve": "Completely rewrite and improve this job description. Make it more compelling, clearer, and professional while maintaining all key information.",
                "📊 Optimize for ATS/SEO": "Optimize this job description for ATS systems and SEO. Add relevant keywords, improve scannability, and ensure proper formatting for applicant tracking systems.",
                "✂️ Make More Concise": "Make this job description more concise and to-the-point. Remove fluff, redundancy, and unnecessary jargon while keeping all essential information.",
                "📝 Expand with More Detail": "Expand this job description with more detail. Add more specific responsibilities, clearer requirements, and better context about the role and company.",
                "🎨 Change Tone": f"Rewrite this job description with a {new_tone if enhance_action == '🎨 Change Tone' else 'professional'} tone while maintaining all key information.",
                "🔀 Reformat for Platform": f"Reformat this job description specifically for {target_platform if enhance_action == '🔀 Reformat for Platform' else 'LinkedIn'}. Optimize length, formatting, and content for that platform's best practices."
            }
            
            format_instructions = {
                "Plain Text": "Use plain text formatting with clear section headers.",
                "ATS-Ready HTML": "Format as clean HTML optimized for ATS parsing.",
                "Markdown": "Format using Markdown with headers and bullet points."
            }
            
            prompt = f"""You are an expert job description writer. {action_prompts.get(enhance_action, action_prompts["🔄 Rewrite & Improve"])}

## ORIGINAL JD:
{imported_text}

## OUTPUT REQUIREMENTS:
- Format: {output_fmt}
- {format_instructions.get(output_fmt, "")}
- Target length: ~{enhance_word_target} words
{f"- Additional instructions: {additional_instructions}" if additional_instructions else ""}

Provide only the enhanced job description, no explanations."""

            with st.spinner("✨ Enhancing your job description..."):
                result, tokens = call_claude(prompt, max_tokens=3000)
                
                if not result.startswith("Error"):
                    # Extract title from original or use default
                    title_match = re.search(r'(?:job title|position|role)[:\s]*([^\n]+)', imported_text, re.IGNORECASE)
                    extracted_title = title_match.group(1).strip() if title_match else "Enhanced JD"
                    
                    st.session_state.generated_jd = result
                    st.session_state.jd_metadata = {
                        "job_title": imported_metadata.get('title') or extracted_title,
                        "company": imported_metadata.get('company', ''),
                        "output_format": output_fmt,
                        "source": "imported",
                        "enhancement_type": enhance_action
                    }
                    st.session_state.current_status = None
                    st.success("✅ JD enhanced! View in the Create tab or below.")
                    
                    # Show result inline
                    st.markdown("### 📄 Enhanced Job Description")
                    st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
                    
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        ext = ".html" if "HTML" in output_fmt else ".md" if "Markdown" in output_fmt else ".txt"
                        st.download_button("📥 Download Enhanced JD", result, f"enhanced_jd{ext}", use_container_width=True)
                    with dl_col2:
                        if st.button("💾 Save to History", key="save_enhanced"):
                            if st.session_state.user.get("id") != "god":
                                saved = save_jd_to_history(st.session_state.jd_metadata, result, 75, tokens)
                                if saved:
                                    st.success("Saved! ✓")
                else:
                    st.error(result)
                    st.session_state.current_status = None

with tab_history:
    st.markdown("### 📜 Your JD History")
    
    if st.session_state.user.get("id") == "god":
        st.info("History is not available in GOD mode. Log in with a regular account to save and view history.")
    else:
        history = get_jd_history(50)
        
        if not history:
            st.markdown("""<div style="text-align:center;padding:60px;color:#6b7280;">
                <p style="font-size:1.2rem;">📝 No saved JDs yet</p>
                <p>Generate your first job description and save it to see it here!</p>
            </div>""", unsafe_allow_html=True)
        else:
            filter_col1, filter_col2 = st.columns([2, 1])
            with filter_col1:
                search = st.text_input("🔍 Search", placeholder="Search by job title...")
            with filter_col2:
                show_favorites = st.checkbox("⭐ Favorites only")
            
            filtered = history
            if search:
                filtered = [h for h in filtered if search.lower() in (h.get("job_title") or "").lower()]
            if show_favorites:
                filtered = [h for h in filtered if h.get("is_favorite")]
            
            for item in filtered:
                with st.expander(f"{'⭐ ' if item.get('is_favorite') else ''}{item.get('job_title', 'Untitled')} - {item.get('company', 'No company')} ({item.get('created_at', '')[:10]})"):
                    st.markdown(f"""
                    **Platform:** {item.get('platform', 'N/A')} | **Format:** {item.get('output_format', 'N/A')} | **Score:** {item.get('seo_ats_score', 'N/A')}/100
                    """)
                    
                    st.markdown(f'<div class="output-box">{item.get("generated_jd", "")[:500]}...</div>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("📋 Load", key=f"load_{item['id']}", use_container_width=True):
                            st.session_state.generated_jd = item.get("generated_jd")
                            st.session_state.jd_metadata = item
                            st.rerun()
                    with col2:
                        is_fav = item.get("is_favorite", False)
                        if st.button("⭐ Unfavorite" if is_fav else "☆ Favorite", key=f"fav_{item['id']}", use_container_width=True):
                            toggle_favorite(item['id'], not is_fav)
                            st.rerun()
                    with col3:
                        if st.button("📤 To Screener", key=f"screen_{item['id']}", use_container_width=True):
                            st.info(f"Use this JD in CV Screener: ID {item['id'][:8]}...")
                    with col4:
                        if st.button("🗑️ Delete", key=f"del_{item['id']}", use_container_width=True):
                            delete_jd_history(item['id'])
                            st.rerun()
