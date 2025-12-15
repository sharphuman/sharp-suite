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
        ('save_error', None),
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
            return "[DOCX parsing requires python-docx library]"
    
    elif file_type == 'json':
        try:
            data = json.loads(content.decode('utf-8'))
            if isinstance(data, dict):
                jd_text = ""
                for key in ['description', 'job_description', 'jd', 'content', 'text', 'body']:
                    if key in data:
                        jd_text = data[key]
                        break
                if not jd_text:
                    parts = []
                    if data.get('title') or data.get('job_title'):
                        parts.append(f"Job Title: {data.get('title') or data.get('job_title')}")
                    if data.get('company'):
                        parts.append(f"Company: {data.get('company')}")
                    if data.get('requirements'):
                        parts.append(f"Requirements: {data.get('requirements')}")
                    if data.get('responsibilities'):
                        parts.append(f"Responsibilities: {data.get('responsibilities')}")
                    jd_text = '\n\n'.join(parts) if parts else json.dumps(data, indent=2)
                return jd_text
            return json.dumps(data, indent=2)
        except:
            return content.decode('utf-8', errors='ignore')
    
    return content.decode('utf-8', errors='ignore')

# ============================================
# EXPORT FUNCTIONS
# ============================================

def generate_docx_bytes(jd_text, metadata):
    """Generate DOCX file bytes."""
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        
        # Title
        title = doc.add_heading(metadata.get('job_title', 'Job Description'), 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Company
        if metadata.get('company'):
            company_para = doc.add_paragraph(metadata.get('company'))
            company_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()  # Spacer
        
        # JD Content
        for line in jd_text.split('\n'):
            if line.strip():
                doc.add_paragraph(line)
        
        # Footer
        doc.add_paragraph()
        footer = doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
        footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Save to bytes
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        return None

def generate_pdf_html(jd_text, metadata):
    """Generate HTML for PDF export (open in browser, print to PDF)."""
    title = metadata.get('job_title', 'Job Description')
    company = metadata.get('company', '')
    
    # Convert markdown-style formatting to HTML
    content_html = jd_text
    content_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content_html)
    content_html = re.sub(r'\n', r'<br>', content_html)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            max-width: 800px; 
            margin: 40px auto; 
            padding: 40px;
            color: #333; 
            line-height: 1.6; 
        }}
        .header {{ 
            border-bottom: 3px solid #6366f1; 
            padding-bottom: 20px; 
            margin-bottom: 30px; 
        }}
        .header h1 {{ 
            color: #1f2937; 
            margin: 0 0 10px 0; 
            font-size: 28px; 
        }}
        .header .company {{ 
            color: #6366f1; 
            font-size: 18px; 
            font-weight: 600; 
        }}
        .header .meta {{ 
            color: #6b7280; 
            font-size: 14px; 
            margin-top: 10px; 
        }}
        .content {{ 
            font-size: 15px; 
        }}
        .content strong {{ 
            color: #1f2937; 
        }}
        .footer {{ 
            margin-top: 40px; 
            padding-top: 20px; 
            border-top: 1px solid #e5e7eb; 
            color: #9ca3af; 
            font-size: 12px; 
            text-align: right; 
        }}
        @media print {{ 
            body {{ margin: 20px; padding: 20px; }}
            .header {{ border-bottom-width: 2px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        {f'<div class="company">{company}</div>' if company else ''}
        <div class="meta">
            {metadata.get('remote_type', '')} | {metadata.get('experience_level', '')} | {metadata.get('industry', '')}
        </div>
    </div>
    <div class="content">
        {content_html}
    </div>
    <div class="footer">
        Generated by Sharp JD | {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
</body>
</html>"""
    return html

def generate_ats_json(jd_text, metadata):
    """Generate ATS-compatible JSON export."""
    # Extract sections from JD text
    sections = {
        'responsibilities': '',
        'requirements': '',
        'benefits': '',
        'about': ''
    }
    
    jd_lower = jd_text.lower()
    
    # Try to extract sections
    resp_match = re.search(r'responsibilities[:\s]*\n(.*?)(?=\n\n|\nrequirements|\nqualifications|\nbenefits|$)', jd_text, re.IGNORECASE | re.DOTALL)
    if resp_match:
        sections['responsibilities'] = resp_match.group(1).strip()
    
    req_match = re.search(r'(?:requirements|qualifications)[:\s]*\n(.*?)(?=\n\n|\nresponsibilities|\nbenefits|$)', jd_text, re.IGNORECASE | re.DOTALL)
    if req_match:
        sections['requirements'] = req_match.group(1).strip()
    
    ben_match = re.search(r'benefits[:\s]*\n(.*?)(?=\n\n|$)', jd_text, re.IGNORECASE | re.DOTALL)
    if ben_match:
        sections['benefits'] = ben_match.group(1).strip()
    
    # Extract skills (look for bullet points or comma-separated lists)
    skills = []
    skill_patterns = [
        r'(?:proficiency|experience|knowledge|skills?)[:\s]+(?:in\s+)?([^.\n]+)',
        r'•\s*([A-Z][a-zA-Z+#]+(?:\s+[A-Z][a-zA-Z+#]+)?)',
    ]
    for pattern in skill_patterns:
        matches = re.findall(pattern, jd_text)
        skills.extend([s.strip() for s in matches if len(s.strip()) > 2])
    
    # Build ATS JSON
    ats_data = {
        "job_posting": {
            "title": metadata.get('job_title', ''),
            "company": metadata.get('company', ''),
            "location": metadata.get('remote_type', 'Not specified'),
            "employment_type": "Full-time",
            "experience_level": metadata.get('experience_level', ''),
            "industry": metadata.get('industry', ''),
            "posted_date": datetime.now().strftime('%Y-%m-%d'),
        },
        "description": {
            "full_text": jd_text,
            "summary": jd_text[:500] + "..." if len(jd_text) > 500 else jd_text,
            "responsibilities": sections['responsibilities'],
            "requirements": sections['requirements'],
            "benefits": sections['benefits'],
        },
        "skills": {
            "required": list(set(skills[:10])),
            "preferred": list(set(skills[10:20])) if len(skills) > 10 else [],
        },
        "compensation": {
            "salary_range": "Competitive" if not metadata.get('include_salary') else "See description",
            "benefits_offered": metadata.get('include_benefits', True),
        },
        "metadata": {
            "source": "Sharp JD",
            "format_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "seo_optimized": metadata.get('seo_optimized', False),
            "platform_target": metadata.get('platform', 'General'),
        }
    }
    
    return json.dumps(ats_data, indent=2)

# ============================================
# HISTORY FUNCTIONS
# ============================================

def save_jd_to_history(metadata, generated_jd, seo_score, tokens_used):
    """Save JD to history with proper error handling."""
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    
    if not user_id:
        return None, "No user ID found"
    
    if user_id == "god":
        return None, "History not available in GOD mode"
    
    # Build the payload - only include non-None values
    payload = {
        "user_id": user_id,
        "generated_jd": generated_jd,
        "seo_ats_score": seo_score,
        "tokens_used": tokens_used or 0
    }
    
    # Add optional fields only if they have values
    optional_fields = [
        ("job_title", "job_title"),
        ("company", "company"),
        ("user_type", "user_type"),
        ("experience_level", "experience_level"),
        ("remote_type", "remote_type"),
        ("industry", "industry"),
        ("platform", "platform"),
        ("output_format", "output_format"),
        ("tone", "tone"),
        ("word_count", "word_count"),
        ("include_salary", "include_salary"),
        ("include_benefits", "include_benefits"),
        ("include_diversity", "include_diversity"),
        ("seo_optimized", "seo_optimized"),
        ("requirements", "requirements"),
    ]
    
    for meta_key, db_key in optional_fields:
        value = metadata.get(meta_key)
        if value is not None:
            payload[db_key] = value
    
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/jd_history",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=payload,
            timeout=10
        )
        
        if r.status_code in [200, 201]:
            result = r.json()
            return result[0] if result else None, None
        else:
            error_msg = f"Status {r.status_code}"
            try:
                error_data = r.json()
                if isinstance(error_data, dict):
                    error_msg = error_data.get('message', error_data.get('error', str(error_data)))
            except:
                error_msg = r.text[:200] if r.text else error_msg
            return None, error_msg
    except Exception as e:
        return None, str(e)

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
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%); }
    * { font-family: 'Nunito', sans-serif !important; }
    </style>""", unsafe_allow_html=True)
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
                    st.success(r["message"]) if r["success"] else st.error(r["message"])
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
                    st.success(r["message"]) if r["success"] else st.error(r["message"])

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
            ("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"),
            ("interview", "🎯 Interview"), ("source", "🎣 Sourcing"), ("content", "✍️ Content"),
            ("sales", "💰 Sales"), ("reach", "🚀 Reach"), ("assistant", "🤖 Assistant"),
        ]
        for app_key, label in apps:
            if app_key == "jd":
                st.button(f"{label} ◀", disabled=True, use_container_width=True)
            else:
                st.link_button(label, build_app_url(app_key), use_container_width=True)
        
        if st.session_state.get("is_god") or st.session_state.get("user_plan") == "god":
            st.markdown("---")
            st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
        
        st.markdown("---")
        with st.expander("💬 Feedback"):
            fb_type = st.selectbox("Type", ["General", "Bug", "Feature"], key="fb_type")
            fb_msg = st.text_area("Message", key="fb_msg", height=80)
            if st.button("Send", key="fb_send"):
                if fb_msg:
                    submit_feedback("jd", fb_type.lower(), 4, fb_msg)
                    st.success("Thanks! 🙏")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
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

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%); }
h1,h2,h3 { color: white !important; }
p, span, label, .stMarkdown { color: #e5e5e5 !important; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { 
    background: rgba(18,18,26,0.8) !important; 
    border: 1px solid rgba(99,102,241,0.3) !important; 
    color: white !important; 
}
.output-box { background: rgba(18,18,26,0.9); border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; margin: 10px 0; color: #e5e5e5; white-space: pre-wrap; }
.metric-card { background: rgba(99,102,241,0.1); border-radius: 10px; padding: 15px; text-align: center; }
</style>""", unsafe_allow_html=True)

render_sidebar()

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:45px;">
    <div><h1 style="margin:0;">Sharp JD</h1><p style="color:#9ca3af;margin:0;">AI-Powered Job Descriptions</p></div>
</div>""", unsafe_allow_html=True)

# Main tabs
tab_create, tab_import, tab_history = st.tabs(["✏️ Create JD", "📄 Import/Enhance JD", "📜 History"])

with tab_create:
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

    st.markdown("### 📝 Requirements & Details")
    requirements = st.text_area(
        "Key Requirements & Responsibilities", 
        height=120,
        placeholder="• 5+ years Python experience\n• Team leadership skills\n• Cloud platform expertise (AWS/GCP)..."
    )

    st.markdown("### ⚙️ Output Settings")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        platform = st.selectbox("Target Platform", [
            "LinkedIn", "Indeed", "Company Careers Page", "Glassdoor", 
            "ZipRecruiter", "Monster", "General/Multi-platform"
        ])
    with col2:
        output_format = st.selectbox("Output Format", ["Plain Text", "ATS-Ready HTML", "Markdown"])
    with col3:
        tone = st.selectbox("Tone", ["Professional", "Casual/Startup", "Formal/Corporate", "Friendly", "Bold/Exciting"])
    with col4:
        word_count = st.slider("Target Word Count", 200, 1200, 500, step=50)

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

    st.markdown("---")
    
    if st.button("📝 Generate Job Description", type="primary", use_container_width=True):
        if not job_title:
            st.warning("Please enter a job title")
        else:
            user_context = "an external recruiter at a staffing agency" if "Recruiter" in user_type else "an internal HR/TA professional"
            
            format_instructions = {
                "Plain Text": "Use plain text formatting with clear section headers.",
                "ATS-Ready HTML": "Format as clean HTML optimized for ATS parsing.",
                "Markdown": "Format using Markdown with headers and bullet points."
            }
            
            platform_tips = {
                "LinkedIn": "Optimize for LinkedIn's format. Keep scannable with short paragraphs.",
                "Indeed": "Front-load important information. Indeed users scan quickly.",
                "Company Careers Page": "Can be more detailed and branded.",
                "General/Multi-platform": "Create a versatile JD that works across platforms."
            }
            
            prompt = f"""You are an expert job description writer. Write a compelling job description:

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
- Target Platform: {platform} - {platform_tips.get(platform, "")}
- Format: {output_format} - {format_instructions.get(output_format, "")}
- Tone: {tone}
- Target Length: ~{word_count} words

**Sections to Include:**
- About the Company (brief, compelling)
- About the Role
- Key Responsibilities (5-7 bullet points)
- Requirements (Must-have and Nice-to-have separated)
{"- Salary Range: Include placeholder like '$X - $Y based on experience'" if include_salary else ""}
{"- Benefits & Perks section" if include_benefits else ""}
{"- Equal Opportunity / Diversity statement" if include_diversity else ""}
- How to Apply

{"**SEO Optimization:** Include relevant keywords naturally throughout." if seo_optimized else ""}

Write the job description now. Make it compelling, clear, and professional."""

            with st.spinner("✨ Crafting your job description..."):
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
                    st.rerun()
                else:
                    st.error(result)

    # Display Generated JD
    if st.session_state.generated_jd:
        st.markdown("---")
        st.markdown("### 📄 Generated Job Description")
        
        metadata = st.session_state.jd_metadata or {}
        seo_score = calculate_seo_ats_score(st.session_state.generated_jd, metadata)
        word_count_actual = len(st.session_state.generated_jd.split())
        char_count = len(st.session_state.generated_jd)
        
        # Stats
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            score_color = "#10b981" if seo_score >= 70 else "#f59e0b" if seo_score >= 50 else "#ef4444"
            st.markdown(f"""<div class="metric-card">
                <p style="color:#9ca3af;margin:0;font-size:0.7rem;">SEO/ATS Score</p>
                <p style="color:{score_color};font-size:1.5rem;font-weight:bold;margin:0;">{seo_score}/100</p>
            </div>""", unsafe_allow_html=True)
        with stat_col2:
            st.markdown(f"""<div class="metric-card">
                <p style="color:#9ca3af;margin:0;font-size:0.7rem;">Word Count</p>
                <p style="color:white;font-size:1.5rem;font-weight:bold;margin:0;">{word_count_actual}</p>
            </div>""", unsafe_allow_html=True)
        with stat_col3:
            st.markdown(f"""<div class="metric-card">
                <p style="color:#9ca3af;margin:0;font-size:0.7rem;">Characters</p>
                <p style="color:white;font-size:1.5rem;font-weight:bold;margin:0;">{char_count:,}</p>
            </div>""", unsafe_allow_html=True)
        with stat_col4:
            st.markdown(f"""<div class="metric-card">
                <p style="color:#9ca3af;margin:0;font-size:0.7rem;">Format</p>
                <p style="color:white;font-size:1rem;font-weight:bold;margin:0;">{metadata.get('output_format', 'Plain Text')}</p>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown(f'<div class="output-box">{st.session_state.generated_jd}</div>', unsafe_allow_html=True)
        
        # Export Options
        st.markdown("### 📥 Export Options")
        exp_col1, exp_col2, exp_col3, exp_col4, exp_col5 = st.columns(5)
        
        with exp_col1:
            # Plain text
            st.download_button(
                "📄 TXT",
                st.session_state.generated_jd,
                file_name=f"jd_{metadata.get('job_title', 'job').lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with exp_col2:
            # HTML/PDF
            pdf_html = generate_pdf_html(st.session_state.generated_jd, metadata)
            st.download_button(
                "📑 HTML/PDF",
                pdf_html,
                file_name=f"jd_{metadata.get('job_title', 'job').lower().replace(' ', '_')}.html",
                mime="text/html",
                use_container_width=True,
                help="Open in browser, then Print → Save as PDF"
            )
        
        with exp_col3:
            # DOCX
            docx_bytes = generate_docx_bytes(st.session_state.generated_jd, metadata)
            if docx_bytes:
                st.download_button(
                    "📝 DOCX",
                    docx_bytes,
                    file_name=f"jd_{metadata.get('job_title', 'job').lower().replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            else:
                st.button("📝 DOCX", disabled=True, use_container_width=True, help="Install python-docx for DOCX export")
        
        with exp_col4:
            # ATS JSON
            ats_json = generate_ats_json(st.session_state.generated_jd, metadata)
            st.download_button(
                "🔗 ATS JSON",
                ats_json,
                file_name=f"jd_{metadata.get('job_title', 'job').lower().replace(' ', '_')}_ats.json",
                mime="application/json",
                use_container_width=True
            )
        
        with exp_col5:
            # Markdown
            st.download_button(
                "📋 Markdown",
                st.session_state.generated_jd,
                file_name=f"jd_{metadata.get('job_title', 'job').lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        # Action buttons
        st.markdown("### 💾 Actions")
        act_col1, act_col2, act_col3 = st.columns(3)
        
        with act_col1:
            if st.button("💾 Save to History", use_container_width=True):
                saved, error = save_jd_to_history(metadata, st.session_state.generated_jd, seo_score, 0)
                if saved:
                    st.success("✅ Saved to history!")
                else:
                    st.error(f"Failed to save: {error}")
        
        with act_col2:
            if st.button("📤 Send to Screener", use_container_width=True):
                st.info("Feature coming soon - will open CV Screener with this JD loaded")
        
        with act_col3:
            if st.button("🔄 Start New", use_container_width=True):
                st.session_state.generated_jd = None
                st.session_state.jd_metadata = None
                st.rerun()
        
        # Refinement
        st.markdown("---")
        st.markdown("### ✏️ Refine This JD")
        refine_prompt = st.text_input(
            "What would you like to change?",
            placeholder="e.g. Make it shorter, add more technical requirements, change tone..."
        )
        
        if st.button("✨ Apply Changes", use_container_width=True):
            if refine_prompt:
                refine_full_prompt = f"""Here is a job description:

{st.session_state.generated_jd}

Please modify it according to this request: {refine_prompt}

Keep the same general structure and format, but apply the requested changes. Output only the modified job description."""

                with st.spinner("✨ Applying your changes..."):
                    refined, _ = call_claude(refine_full_prompt)
                    if not refined.startswith("Error"):
                        st.session_state.generated_jd = refined
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
    
    if import_source == "📄 Upload File":
        uploaded_jd = st.file_uploader("Upload JD (PDF, DOCX, TXT, JSON)", type=['pdf', 'docx', 'doc', 'txt', 'json'], key="jd_file_upload")
        if uploaded_jd:
            imported_text = extract_text_from_file(uploaded_jd)
            st.success(f"✅ Extracted {len(imported_text)} characters from {uploaded_jd.name}")
            if st.checkbox("Show extracted text"):
                st.text_area("Extracted:", imported_text[:2000], height=150, disabled=True)
    
    elif import_source == "🔗 JSON/ATS Format":
        st.markdown("Paste JSON from ATS systems like Greenhouse, Lever, Workday, etc.")
        json_input = st.text_area("Paste JSON:", height=200, placeholder='{"title": "...", "description": "..."}')
        if json_input:
            try:
                data = json.loads(json_input)
                st.success("✅ Valid JSON")
                # Extract text
                if isinstance(data, dict):
                    for key in ['description', 'job_description', 'content', 'text']:
                        if key in data:
                            imported_text = data[key]
                            break
                    if not imported_text:
                        imported_text = json.dumps(data, indent=2)
            except:
                st.error("Invalid JSON format")
    else:
        imported_text = st.text_area("Paste existing JD:", height=250, placeholder="Paste your existing job description here...")
    
    if imported_text:
        st.markdown("---")
        st.markdown("### 🎯 Enhancement Options")
        
        enhance_action = st.selectbox("What would you like to do?", [
            "🔄 Rewrite & Improve",
            "📊 Optimize for ATS/SEO",
            "✂️ Make More Concise",
            "📝 Expand with More Detail",
            "🎨 Change Tone",
            "🔀 Reformat for Platform"
        ])
        
        enh_col1, enh_col2 = st.columns(2)
        with enh_col1:
            if enhance_action == "🎨 Change Tone":
                new_tone = st.selectbox("New tone:", ["Professional", "Casual/Startup", "Formal", "Friendly"])
            elif enhance_action == "🔀 Reformat for Platform":
                target_platform = st.selectbox("Target platform:", ["LinkedIn", "Indeed", "Company Careers"])
        with enh_col2:
            output_fmt = st.selectbox("Output Format:", ["Plain Text", "HTML", "Markdown"], key="enhance_fmt")
        
        if st.button("✨ Enhance JD", type="primary", use_container_width=True):
            action_prompts = {
                "🔄 Rewrite & Improve": "Completely rewrite and improve this job description.",
                "📊 Optimize for ATS/SEO": "Optimize for ATS systems and SEO with relevant keywords.",
                "✂️ Make More Concise": "Make more concise, remove fluff while keeping essentials.",
                "📝 Expand with More Detail": "Expand with more specific details and context.",
                "🎨 Change Tone": f"Rewrite with a {new_tone if enhance_action == '🎨 Change Tone' else 'professional'} tone.",
                "🔀 Reformat for Platform": f"Reformat for {target_platform if enhance_action == '🔀 Reformat for Platform' else 'LinkedIn'}."
            }
            
            prompt = f"""{action_prompts.get(enhance_action, action_prompts["🔄 Rewrite & Improve"])}

## ORIGINAL JD:
{imported_text}

## OUTPUT FORMAT: {output_fmt}

Provide only the enhanced job description."""

            with st.spinner("✨ Enhancing..."):
                result, _ = call_claude(prompt, max_tokens=3000)
                
                if not result.startswith("Error"):
                    st.session_state.generated_jd = result
                    st.session_state.jd_metadata = {"job_title": "Enhanced JD", "output_format": output_fmt}
                    st.success("✅ JD enhanced! See Create tab for full options.")
                    st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
                else:
                    st.error(result)

with tab_history:
    st.markdown("### 📜 Your JD History")
    
    if st.session_state.user.get("id") == "god":
        st.info("History is not available in GOD mode. Log in with a regular account.")
    else:
        history = get_jd_history(50)
        
        if not history:
            st.markdown("""<div style="text-align:center;padding:60px;color:#6b7280;">
                <p style="font-size:1.2rem;">📝 No saved JDs yet</p>
                <p>Generate and save a job description to see it here!</p>
            </div>""", unsafe_allow_html=True)
        else:
            search = st.text_input("🔍 Search", placeholder="Search by job title...")
            show_favorites = st.checkbox("⭐ Favorites only")
            
            filtered = history
            if search:
                filtered = [h for h in filtered if search.lower() in (h.get("job_title") or "").lower()]
            if show_favorites:
                filtered = [h for h in filtered if h.get("is_favorite")]
            
            for item in filtered:
                with st.expander(f"{'⭐ ' if item.get('is_favorite') else ''}{item.get('job_title', 'Untitled')} - {item.get('company', 'N/A')} ({item.get('created_at', '')[:10]})"):
                    st.markdown(f"**Platform:** {item.get('platform', 'N/A')} | **Format:** {item.get('output_format', 'N/A')} | **Score:** {item.get('seo_ats_score', 'N/A')}/100")
                    
                    st.text_area("Content:", item.get("generated_jd", "")[:500] + "...", height=100, disabled=True, key=f"preview_{item['id']}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("📋 Load", key=f"load_{item['id']}", use_container_width=True):
                            st.session_state.generated_jd = item.get("generated_jd")
                            st.session_state.jd_metadata = item
                            st.rerun()
                    with col2:
                        is_fav = item.get("is_favorite", False)
                        if st.button("⭐" if not is_fav else "★", key=f"fav_{item['id']}", use_container_width=True):
                            toggle_favorite(item['id'], not is_fav)
                            st.rerun()
                    with col3:
                        st.download_button("📥", item.get("generated_jd", ""), f"jd_{item['id'][:8]}.txt", use_container_width=True)
                    with col4:
                        if st.button("🗑️", key=f"del_{item['id']}", use_container_width=True):
                            delete_jd_history(item['id'])
                            st.rerun()
