"""Sharp Outreach - Boolean Search, Email Sequences & LinkedIn"""
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
    "screen": "https://screen.sharphuman.com", "interview": "https://interview.sharphuman.com",
    "outreach": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com",
    "sales": "https://sales.sharphuman.com",
}

EMAIL_TEMPLATES = {
    "3_touch_passive": {"name": "3-Touch Passive", "touches": 3, "spacing": "Day 1, 4, 8"},
    "5_touch_priority": {"name": "5-Touch Priority", "touches": 5, "spacing": "Day 1, 3, 5, 7, 10"},
    "referral_warm": {"name": "Warm Referral", "touches": 2, "spacing": "Day 1, 5"},
}

PLATFORMS = {
    "linkedin_recruiter": {"name": "LinkedIn Recruiter", "and": "AND", "or": "OR", "not": "NOT"},
    "linkedin_basic": {"name": "LinkedIn Basic", "and": "AND", "or": "OR", "not": "-"},
    "indeed": {"name": "Indeed", "and": "and", "or": "or", "not": "-"},
    "github": {"name": "GitHub", "and": " ", "or": "OR", "not": "-"},
}

# Auth functions
def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "token": token, "device_hash": "outreach",
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

def validate_session_token(token):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        if r.status_code == 200 and r.json():
            session = r.json()[0]
            ur = requests.get(f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
            if ur.status_code == 200 and ur.json():
                p = ur.json()[0]
                return {"user_id": session["user_id"], "email": p.get("email"), "plan": p.get("plan", "free")}
    except: pass
    return None

def log_usage(user_id, session_id, app, action, tokens=0):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/usage_logs",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "session_id": session_id, "app": app, "action": action, "tokens_used": tokens}, timeout=5)
    except: pass

def init_session():
    for k, v in [('authenticated', False), ('user', None), ('is_god', False), ('session_token', None),
                 ('user_plan', 'free'), ('boolean_result', None), ('email_result', None), ('linkedin_result', None)]:
        if k not in st.session_state: st.session_state[k] = v

def check_url_auth():
    token = st.query_params.get("token")
    if token and not st.session_state.authenticated:
        user_info = validate_session_token(token)
        if user_info:
            st.session_state.authenticated = True
            st.session_state.user = {"email": user_info["email"], "id": user_info["user_id"]}
            st.session_state.session_token = token
            st.session_state.user_plan = user_info.get("plan", "free")
            return True
    return False

def get_user_email():
    return st.session_state.user.get("email", "User") if st.session_state.user else "User"

def build_app_url(app_name):
    base = APP_URLS.get(app_name, "")
    token = st.session_state.get("session_token", "")
    return f"{base}?token={token}" if base and token else base

def get_jd_history(limit=20):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god": return []
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/jd_history",
            params={"user_id": f"eq.{user_id}", "order": "created_at.desc", "limit": str(limit)},
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        return r.json() if r.status_code == 200 else []
    except: return []

def call_claude(prompt, max_tokens=4000, action="outreach"):
    if not ANTHROPIC_API_KEY: return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens,
                  "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200:
            text = r.json().get("content", [{}])[0].get("text", "")
            tokens = r.json().get("usage", {}).get("output_tokens", 0)
            if st.session_state.user:
                log_usage(st.session_state.user.get("id"), st.session_state.session_token, "outreach", action, tokens)
            return text, tokens
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {e}", 0

def generate_boolean(title, must_have, nice_to_have, exclude, location, platform, experience):
    syntax = PLATFORMS.get(platform, PLATFORMS["linkedin_recruiter"])
    prompt = f"""Generate Boolean search for {syntax['name']}.

TITLE: {title}
MUST-HAVE: {must_have}
NICE-TO-HAVE: {nice_to_have}
EXCLUDE: {exclude}
LOCATION: {location}
EXPERIENCE: {experience}+ years
SYNTAX: AND={syntax['and']}, OR={syntax['or']}, NOT={syntax['not']}

OUTPUT JSON:
```json
{{"primary": "<main boolean>", "alternatives": [{{"name": "Title Focus", "string": "<boolean>"}}, {{"name": "Skills Focus", "string": "<boolean>"}}], "xray": {{"linkedin": "site:linkedin.com/in <search>", "github": "site:github.com <search>"}}, "tips": ["<tip>"]}}
```"""
    return call_claude(prompt, 2000, "boolean")

def generate_emails(template, recruiter, candidate, job, cta):
    tpl = EMAIL_TEMPLATES.get(template, EMAIL_TEMPLATES["3_touch_passive"])
    prompt = f"""Generate {tpl['touches']}-email sequence ({tpl['name']}).

RECRUITER: {recruiter}
CANDIDATE: {candidate}
JOB: {job}
CTA: {cta or '[CALENDAR_LINK]'}
TIMING: {tpl['spacing']}

OUTPUT JSON:
```json
{{"sequence": "{tpl['name']}", "emails": [{{"number": 1, "day": "Day 1", "subject": "<subject>", "body": "<email>", "cta": "<cta>"}}], "tips": ["<tip>"], "response_rate": "<X%>"}}
```

Make emails personalized, concise, value-focused."""
    return call_claude(prompt, 4000, "email_sequence")

def generate_linkedin(name, role, hook, cta):
    prompt = f"""Write LinkedIn connection request (MAX 300 chars).

NAME: {name}
ROLE: {role}
HOOK: {hook}
CTA: {cta or 'Ask to chat'}

Requirements: Under 300 chars, no generic opener, personalized, soft CTA.
Output message only."""
    return call_claude(prompt, 500, "linkedin")

def export_to_pdf(data, title):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.colors import HexColor
        from reportlab.lib.units import inch
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=18, textColor=HexColor('#6366f1'))
        body_style = ParagraphStyle('B', parent=styles['Normal'], fontSize=10)
        
        story = [Paragraph(title, title_style), Spacer(1, 12)]
        if isinstance(data, dict):
            for email in data.get('emails', []):
                story.append(Paragraph(f"<b>Email {email.get('number')}</b> - {email.get('day')}", body_style))
                story.append(Paragraph(f"Subject: {email.get('subject', '')}", body_style))
                story.append(Paragraph(email.get('body', '').replace('\n', '<br/>'), body_style))
                story.append(Spacer(1, 12))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except: return None

def export_to_docx(data, title):
    try:
        from docx import Document
        doc = Document()
        doc.add_heading(title, 0)
        if isinstance(data, dict):
            for email in data.get('emails', []):
                doc.add_heading(f"Email {email.get('number')} - {email.get('day')}", level=1)
                doc.add_paragraph(f"Subject: {email.get('subject', '')}")
                doc.add_paragraph(email.get('body', ''))
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except: return None

# Main App
st.set_page_config(page_title="Sharp Outreach", page_icon="🎣", layout="wide")
init_session()
check_url_auth()

if not st.session_state.authenticated:
    st.title("🎣 Sharp Outreach")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login", type="primary"):
        if password == GOD_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.is_god = True
            st.session_state.user = {"email": "GOD", "id": "god"}
            st.rerun()
        elif email and password:
            result = supabase_sign_in(email, password)
            if result["success"]:
                st.session_state.authenticated = True
                st.session_state.user = result["user"]
                st.session_state.session_token = result["session_token"]
                st.rerun()
            else: st.error(result["message"])
    st.stop()

# Sidebar
with st.sidebar:
    st.image("https://sharphuman.com/logo1-3.png", width=50)
    st.markdown(f"**{get_user_email()}**")
    st.markdown("---")
    for key, label in [("portal", "🏠 Portal"), ("jd", "📝 JD"), ("screen", "🔍 Screen"), ("interview", "🎯 Interview"), ("outreach", "🎣 Outreach"), ("content", "✍️ Content"), ("sales", "💰 Sales")]:
        if key == "outreach": st.button(f"{label} ◀", disabled=True, use_container_width=True)
        else: st.link_button(label, build_app_url(key), use_container_width=True)
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

st.title("🎣 Sharp Outreach")
tab_bool, tab_email, tab_li = st.tabs(["🔍 Boolean Search", "📧 Email Sequences", "💼 LinkedIn"])

with tab_bool:
    st.subheader("Boolean Search Generator")
    load_src = st.selectbox("Load From:", ["Manual", "From JD History"])
    jd_data = None
    if load_src == "From JD History":
        history = get_jd_history(15)
        if history:
            opts = {f"{j.get('job_title', 'Untitled')} ({j.get('created_at', '')[:10]})": j for j in history}
            sel = st.selectbox("Select JD:", list(opts.keys()))
            if sel: jd_data = opts[sel]; st.success(f"Loaded: {jd_data.get('job_title')}")
        else: st.info("No JDs found")
    
    c1, c2 = st.columns(2)
    with c1:
        title = st.text_input("Job Title", value=jd_data.get('job_title', '') if jd_data else "")
        must = st.text_area("Must-Have Skills", height=100)
        nice = st.text_area("Nice-to-Have", height=80)
    with c2:
        platform = st.selectbox("Platform", list(PLATFORMS.keys()), format_func=lambda x: PLATFORMS[x]['name'])
        location = st.text_input("Location")
        exclude = st.text_input("Exclude")
        exp = st.slider("Min Experience", 0, 20, 3)
    
    if st.button("🔍 Generate Boolean", type="primary", use_container_width=True):
        if title and must:
            with st.spinner("Generating..."):
                result, _ = generate_boolean(title, must, nice, exclude, location, platform, exp)
                if not result.startswith("Error"): st.session_state.boolean_result = result; st.rerun()
                else: st.error(result)
    
    if st.session_state.get('boolean_result'):
        try:
            m = re.search(r'```json\s*(.*?)\s*```', st.session_state.boolean_result, re.DOTALL)
            data = json.loads(m.group(1) if m else st.session_state.boolean_result)
            st.subheader("Primary Search")
            st.code(data.get('primary', ''))
            st.download_button("📋 Copy", data.get('primary', ''), "boolean.txt")
            for alt in data.get('alternatives', []):
                with st.expander(alt.get('name')): st.code(alt.get('string', ''))
            st.download_button("📥 Export All", json.dumps(data, indent=2), "boolean_all.json")
        except Exception as e: st.error(f"Parse error: {e}")

with tab_email:
    st.subheader("Email Sequence Generator")
    c1, c2 = st.columns(2)
    with c1:
        rec_name = st.text_input("Your Name", key="rec_name")
        rec_company = st.text_input("Your Company", key="rec_company")
        cta = st.text_input("Calendar Link", key="cta")
    with c2:
        cand_name = st.text_input("Candidate Name", key="cand_name")
        cand_role = st.text_input("Candidate Current Role", key="cand_role")
        job_title = st.text_input("Target Role", key="job_title")
    
    template = st.selectbox("Template", list(EMAIL_TEMPLATES.keys()), format_func=lambda x: EMAIL_TEMPLATES[x]['name'])
    
    if st.button("📧 Generate Sequence", type="primary", use_container_width=True):
        if cand_name and job_title:
            with st.spinner("Generating..."):
                recruiter = f"Name: {rec_name}, Company: {rec_company}"
                candidate = f"Name: {cand_name}, Role: {cand_role}"
                job = f"Title: {job_title}"
                result, _ = generate_emails(template, recruiter, candidate, job, cta)
                if not result.startswith("Error"): st.session_state.email_result = result; st.rerun()
                else: st.error(result)
    
    if st.session_state.get('email_result'):
        try:
            m = re.search(r'```json\s*(.*?)\s*```', st.session_state.email_result, re.DOTALL)
            data = json.loads(m.group(1) if m else st.session_state.email_result)
            st.subheader(f"📬 {data.get('sequence', 'Sequence')}")
            for email in data.get('emails', []):
                with st.expander(f"Email {email.get('number')} - {email.get('day')}"):
                    st.markdown(f"**Subject:** {email.get('subject')}")
                    st.text_area("Body", email.get('body', ''), height=150, key=f"e{email.get('number')}")
            c1, c2, c3 = st.columns(3)
            with c1:
                pdf = export_to_pdf(data, "Email Sequence")
                if pdf: st.download_button("📑 PDF", pdf, "sequence.pdf", "application/pdf", use_container_width=True)
            with c2:
                docx = export_to_docx(data, "Email Sequence")
                if docx: st.download_button("📄 DOCX", docx, "sequence.docx", use_container_width=True)
            with c3: st.download_button("🔗 JSON", json.dumps(data, indent=2), "sequence.json", use_container_width=True)
        except Exception as e: st.error(f"Parse error: {e}")

with tab_li:
    st.subheader("LinkedIn Connection Request")
    li_name = st.text_input("Candidate Name", key="li_name")
    li_role = st.text_input("Target Role", key="li_role")
    li_hook = st.selectbox("Hook", ["Recent post", "Mutual connection", "Shared background", "Open source work", "Industry expertise", "Custom"])
    if li_hook == "Custom": li_hook = st.text_input("Custom Hook")
    li_cta = st.text_input("CTA Link (optional)")
    
    if st.button("💼 Generate Message", type="primary", use_container_width=True):
        if li_name and li_role:
            with st.spinner("Generating..."):
                result, _ = generate_linkedin(li_name, li_role, li_hook, li_cta)
                if not result.startswith("Error"): st.session_state.linkedin_result = result; st.rerun()
                else: st.error(result)
    
    if st.session_state.get('linkedin_result'):
        msg = st.session_state.linkedin_result
        st.text_area("Your Message", msg, height=100)
        chars = len(msg)
        if chars <= 300: st.success(f"✅ {chars}/300 chars")
        else: st.error(f"⚠️ {chars}/300 - Over limit!")
        st.download_button("📋 Copy", msg, "linkedin.txt")
