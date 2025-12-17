"""Sharp Outreach - Boolean Search, Email Sequences & LinkedIn"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re
import io

# ============================================
# FILE EXTRACTION
# ============================================
def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file (PDF, DOCX, TXT)"""
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
            text = "\n".join([page.get_text() for page in pdf])
            pdf.close()
            return text
        except:
            return re.sub(r'[^\x20-\x7E\n]', ' ', content.decode('utf-8', errors='ignore'))
    
    elif file_type in ['docx', 'doc']:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
        except:
            return "[DOCX extraction failed - paste content instead]"
    
    return content.decode('utf-8', errors='ignore')

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
                 ('user_plan', 'free'), ('boolean_result', None), ('email_result', None), ('linkedin_result', None), ('sales_result', None)]:
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

def generate_boolean(title, must_have, nice_to_have, exclude, location, platform, experience, context_doc=""):
    syntax = PLATFORMS.get(platform, PLATFORMS["linkedin_recruiter"])
    
    context_section = ""
    if context_doc:
        context_section = f"""
CONTEXT DOCUMENT (JD or CV):
{context_doc[:5000]}
Use this to extract additional relevant skills, terminology, and requirements.
"""
    
    prompt = f"""Generate Boolean search for {syntax['name']}.

TITLE: {title}
MUST-HAVE: {must_have}
NICE-TO-HAVE: {nice_to_have}
EXCLUDE: {exclude}
LOCATION: {location}
EXPERIENCE: {experience}+ years
SYNTAX: AND={syntax['and']}, OR={syntax['or']}, NOT={syntax['not']}
{context_section}
OUTPUT JSON:
```json
{{"primary": "<main boolean>", "alternatives": [{{"name": "Title Focus", "string": "<boolean>"}}, {{"name": "Skills Focus", "string": "<boolean>"}}], "xray": {{"linkedin": "site:linkedin.com/in <search>", "github": "site:github.com <search>"}}, "tips": ["<tip>"]}}
```"""
    return call_claude(prompt, 2000, "boolean")

def generate_emails(template, recruiter, candidate, job, cta, context_doc=""):
    tpl = EMAIL_TEMPLATES.get(template, EMAIL_TEMPLATES["3_touch_passive"])
    
    context_section = ""
    if context_doc:
        context_section = f"""
CONTEXT DOCUMENT (JD, Interview Script, or Call Notes):
{context_doc[:6000]}
Use this to personalize emails with specific talking points, requirements, and selling points.
"""
    
    prompt = f"""Generate {tpl['touches']}-email sequence ({tpl['name']}).

RECRUITER: {recruiter}
CANDIDATE: {candidate}
JOB: {job}
CTA: {cta or '[CALENDAR_LINK]'}
TIMING: {tpl['spacing']}
{context_section}
OUTPUT JSON:
```json
{{"sequence": "{tpl['name']}", "emails": [{{"number": 1, "day": "Day 1", "subject": "<subject>", "body": "<email>", "cta": "<cta>"}}], "tips": ["<tip>"], "response_rate": "<X%>"}}
```

Make emails personalized, concise, value-focused."""
    return call_claude(prompt, 4000, "email_sequence")

def generate_linkedin(name, role, hook, cta, context_doc=""):
    context_section = ""
    if context_doc:
        context_section = f"""
CONTEXT (JD or CV):
{context_doc[:2000]}
Use relevant details to personalize the message.
"""
    
    prompt = f"""Write LinkedIn connection request (MAX 300 chars).

NAME: {name}
ROLE: {role}
HOOK: {hook}
CTA: {cta or 'Ask to chat'}
{context_section}
Requirements: Under 300 chars, no generic opener, personalized, soft CTA.
Output message only."""
    return call_claude(prompt, 500, "linkedin")

def generate_sales_outreach(lead_type, your_name, your_company, contact_name, contact_company, goal, cta_link, context_doc=""):
    """Generate sales/BD outreach email based on lead type and context"""
    
    lead_descriptions = {
        "warm_lead": "Someone who has shown interest (downloaded content, attended webinar, replied to previous outreach)",
        "cold_lead": "No prior relationship - first contact",
        "existing_client": "Current paying customer - upsell, check-in, or expansion opportunity",
        "previous_client": "Former customer - re-engagement or win-back",
        "referral": "Introduced by mutual connection",
        "event_followup": "Met at conference, webinar, or networking event"
    }
    
    context_section = ""
    if context_doc:
        context_section = f"""
CONTEXT DOCUMENT (Sales call notes, LinkedIn profile, website info, etc.):
{context_doc[:6000]}

Use this context to:
- Reference specific pain points or needs mentioned
- Mention relevant details about their company/role
- Personalize based on previous interactions
- Include specific value propositions that match their situation
"""
    
    prompt = f"""Write a sales/BD outreach email.

LEAD TYPE: {lead_type.replace('_', ' ').title()}
LEAD CONTEXT: {lead_descriptions.get(lead_type, 'Business prospect')}

FROM:
- Name: {your_name or '[Your Name]'}
- Company: {your_company or '[Your Company]'}

TO:
- Name: {contact_name or '[Contact Name]'}
- Company: {contact_company or '[Their Company]'}

GOAL: {goal or 'Schedule a discovery call'}
CTA/CALENDAR: {cta_link or '[CALENDAR_LINK]'}
{context_section}
OUTPUT JSON:
```json
{{
    "subject_lines": ["<option 1>", "<option 2>", "<option 3>"],
    "email_body": "<the email - conversational, value-focused, under 150 words>",
    "ps_line": "<optional PS for extra hook>",
    "follow_up_subject": "<subject for follow-up if no reply>",
    "follow_up_body": "<shorter follow-up email - under 75 words>",
    "tips": ["<personalization tip>", "<timing tip>"]
}}
```

WRITING RULES:
1. No generic openers like "I hope this finds you well"
2. Lead with value or relevance, not your pitch
3. One clear CTA
4. Sound human, not salesy
5. Match tone to lead type (warmer for existing clients, more direct for cold)
6. If context provided, reference specific details"""
    
    return call_claude(prompt, 3000, "sales_outreach")

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

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)); border: 1px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 20px; margin-bottom: 24px;">
    <p style="margin: 0; color: #e2e8f0; font-size: 15px; line-height: 1.6;">
        <strong>Your outreach command center.</strong> Build targeted Boolean searches to find the right candidates, 
        generate personalized email sequences that get responses, craft sales outreach that opens doors, 
        and write LinkedIn messages that stay under the character limit.
    </p>
    <p style="margin: 12px 0 0 0; color: #9ca3af; font-size: 14px;">
        💡 <strong>Pro tip:</strong> Upload context docs (JDs, call notes, LinkedIn profiles) to make your outreach 
        feel personal, not templated. The AI uses your context to write like you've done your homework.
    </p>
</div>
""", unsafe_allow_html=True)

tab_bool, tab_email, tab_sales, tab_li = st.tabs(["🔍 Boolean Search", "📧 Candidate Sequences", "💼 Sales Outreach", "🔗 LinkedIn"])

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
    
    # Context Document Section
    with st.expander("📄 Add Context Document (Optional)", expanded=False):
        st.caption("Upload a JD or CV to extract additional skills and terminology")
        bool_context_method = st.radio("Input:", ["📤 Upload", "📝 Paste"], horizontal=True, key="bool_ctx_method")
        bool_context_doc = ""
        if bool_context_method == "📤 Upload":
            bool_file = st.file_uploader("Upload JD or CV", type=['pdf', 'docx', 'txt'], key="bool_upload")
            if bool_file:
                bool_context_doc = extract_text_from_file(bool_file)
                st.success(f"✅ Loaded {bool_file.name}")
        else:
            bool_context_doc = st.text_area("Paste JD or CV:", height=150, key="bool_paste")
    
    if st.button("🔍 Generate Boolean", type="primary", use_container_width=True):
        if title and must:
            with st.spinner("Generating..."):
                result, _ = generate_boolean(title, must, nice, exclude, location, platform, exp, bool_context_doc)
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
    
    # Context Document Section
    with st.expander("📄 Add Context Document (Optional)", expanded=False):
        st.caption("Upload a JD, interview script, or sales call notes to personalize emails")
        email_context_method = st.radio("Input:", ["📤 Upload", "📝 Paste"], horizontal=True, key="email_ctx_method")
        email_context_doc = ""
        if email_context_method == "📤 Upload":
            email_file = st.file_uploader("Upload document", type=['pdf', 'docx', 'txt'], key="email_upload")
            if email_file:
                email_context_doc = extract_text_from_file(email_file)
                st.success(f"✅ Loaded {email_file.name}")
        else:
            email_context_doc = st.text_area("Paste JD, interview script, or call notes:", height=150, key="email_paste")
    
    if st.button("📧 Generate Sequence", type="primary", use_container_width=True):
        if cand_name and job_title:
            with st.spinner("Generating..."):
                recruiter = f"Name: {rec_name}, Company: {rec_company}"
                candidate = f"Name: {cand_name}, Role: {cand_role}"
                job = f"Title: {job_title}"
                result, _ = generate_emails(template, recruiter, candidate, job, cta, email_context_doc)
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

with tab_sales:
    st.subheader("Sales & BD Outreach")
    st.caption("Generate personalized outreach emails for prospects and clients")
    
    # Lead Type Selection
    lead_type = st.selectbox("Lead Type", [
        ("warm_lead", "🔥 Warm Lead - Showed interest (downloaded content, attended webinar)"),
        ("cold_lead", "❄️ Cold Lead - First contact, no prior relationship"),
        ("existing_client", "⭐ Existing Client - Upsell, check-in, or expansion"),
        ("previous_client", "🔄 Previous Client - Re-engagement or win-back"),
        ("referral", "🤝 Referral - Introduced by mutual connection"),
        ("event_followup", "📅 Event Follow-up - Met at conference or webinar")
    ], format_func=lambda x: x[1])
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Your Info**")
        sales_your_name = st.text_input("Your Name", key="sales_name")
        sales_your_company = st.text_input("Your Company", key="sales_company")
        sales_cta = st.text_input("Calendar/CTA Link", key="sales_cta", placeholder="https://calendly.com/...")
    
    with c2:
        st.markdown("**Contact Info**")
        sales_contact_name = st.text_input("Contact Name", key="sales_contact")
        sales_contact_company = st.text_input("Their Company", key="sales_contact_co")
        sales_goal = st.selectbox("Goal", [
            "Schedule a discovery call",
            "Book a demo",
            "Re-engage conversation",
            "Upsell/expand services",
            "Get referral introduction",
            "Follow up on proposal",
            "Check in on satisfaction",
            "Custom"
        ], key="sales_goal")
        if sales_goal == "Custom":
            sales_goal = st.text_input("Custom Goal", key="sales_custom_goal")
    
    # Context Document Section
    with st.expander("📄 Add Context (Recommended)", expanded=True):
        st.caption("Upload sales call notes, their LinkedIn, company website info, or previous correspondence")
        sales_context_method = st.radio("Input:", ["📤 Upload", "📝 Paste"], horizontal=True, key="sales_ctx_method")
        sales_context_doc = ""
        if sales_context_method == "📤 Upload":
            sales_file = st.file_uploader("Upload context document", type=['pdf', 'docx', 'txt'], key="sales_upload")
            if sales_file:
                sales_context_doc = extract_text_from_file(sales_file)
                st.success(f"✅ Loaded {sales_file.name}")
        else:
            sales_context_doc = st.text_area(
                "Paste context:", 
                height=150, 
                key="sales_paste",
                placeholder="Paste any relevant info:\n- Sales call notes\n- Their LinkedIn summary\n- Company 'About' page\n- Previous email thread\n- Pain points discussed"
            )
    
    if st.button("✉️ Generate Outreach Email", type="primary", use_container_width=True):
        if sales_contact_name or sales_contact_company:
            with st.spinner("Generating personalized outreach..."):
                result, _ = generate_sales_outreach(
                    lead_type[0], 
                    sales_your_name, 
                    sales_your_company,
                    sales_contact_name, 
                    sales_contact_company, 
                    sales_goal, 
                    sales_cta,
                    sales_context_doc
                )
                if not result.startswith("Error"): 
                    st.session_state.sales_result = result
                    st.rerun()
                else: 
                    st.error(result)
        else:
            st.warning("Enter contact name or company")
    
    if st.session_state.get('sales_result'):
        try:
            m = re.search(r'```json\s*(.*?)\s*```', st.session_state.sales_result, re.DOTALL)
            data = json.loads(m.group(1) if m else st.session_state.sales_result)
            
            st.markdown("---")
            
            # Subject Lines
            st.markdown("### 📬 Subject Line Options")
            for i, subj in enumerate(data.get('subject_lines', []), 1):
                st.code(subj, language=None)
            
            # Main Email
            st.markdown("### ✉️ Email Body")
            email_body = data.get('email_body', '')
            st.text_area("Main Email", email_body, height=200, key="sales_main_email")
            
            # PS Line
            if data.get('ps_line'):
                st.markdown("**P.S. Line:**")
                st.info(data.get('ps_line'))
            
            # Follow-up
            with st.expander("📨 Follow-up Email (if no reply)"):
                st.markdown(f"**Subject:** {data.get('follow_up_subject', '')}")
                st.text_area("Follow-up Body", data.get('follow_up_body', ''), height=100, key="sales_followup")
            
            # Tips
            if data.get('tips'):
                with st.expander("💡 Tips"):
                    for tip in data.get('tips', []):
                        st.markdown(f"• {tip}")
            
            # Export
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1:
                full_email = f"Subject: {data.get('subject_lines', [''])[0]}\n\n{email_body}"
                if data.get('ps_line'):
                    full_email += f"\n\nP.S. {data.get('ps_line')}"
                st.download_button("📋 Copy Email", full_email, "outreach_email.txt", use_container_width=True)
            with c2:
                st.download_button("🔗 Export JSON", json.dumps(data, indent=2), "outreach.json", use_container_width=True)
            with c3:
                if st.button("🔄 Clear", use_container_width=True):
                    st.session_state.sales_result = None
                    st.rerun()
                    
        except Exception as e: 
            st.error(f"Parse error: {e}")
            st.text(st.session_state.sales_result)

with tab_li:
    st.subheader("LinkedIn Connection Request")
    li_name = st.text_input("Candidate Name", key="li_name")
    li_role = st.text_input("Target Role", key="li_role")
    li_hook = st.selectbox("Hook", ["Recent post", "Mutual connection", "Shared background", "Open source work", "Industry expertise", "Custom"])
    if li_hook == "Custom": li_hook = st.text_input("Custom Hook")
    li_cta = st.text_input("CTA Link (optional)")
    
    # Context Document Section
    with st.expander("📄 Add Context Document (Optional)", expanded=False):
        st.caption("Upload a JD or CV to personalize your message")
        li_context_method = st.radio("Input:", ["📤 Upload", "📝 Paste"], horizontal=True, key="li_ctx_method")
        li_context_doc = ""
        if li_context_method == "📤 Upload":
            li_file = st.file_uploader("Upload JD or CV", type=['pdf', 'docx', 'txt'], key="li_upload")
            if li_file:
                li_context_doc = extract_text_from_file(li_file)
                st.success(f"✅ Loaded {li_file.name}")
        else:
            li_context_doc = st.text_area("Paste JD or CV:", height=150, key="li_paste")
    
    if st.button("💼 Generate Message", type="primary", use_container_width=True):
        if li_name and li_role:
            with st.spinner("Generating..."):
                result, _ = generate_linkedin(li_name, li_role, li_hook, li_cta, li_context_doc)
                if not result.startswith("Error"): st.session_state.linkedin_result = result; st.rerun()
                else: st.error(result)
    
    if st.session_state.get('linkedin_result'):
        msg = st.session_state.linkedin_result
        st.text_area("Your Message", msg, height=100)
        chars = len(msg)
        if chars <= 300: st.success(f"✅ {chars}/300 chars")
        else: st.error(f"⚠️ {chars}/300 - Over limit!")
        st.download_button("📋 Copy", msg, "linkedin.txt")
