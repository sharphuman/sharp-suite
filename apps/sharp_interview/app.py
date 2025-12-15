"""Sharp Interview v4 - Enhanced Evaluation System with Multi-Candidate Comparison"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re
import io
import base64
import subprocess
import tempfile

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
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/user_feedback",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": st.session_state.user.get("id") if st.session_state.user else None,
                  "app": app, "feedback_type": feedback_type, "rating": 4, "message": message,
                  "email": get_user_email()}, timeout=10)
        return r.status_code in [200, 201]
    except: return False

def init_session():
    defaults = [
        ('authenticated', False), ('user', None), ('is_god', False), ('session_token', None),
        ('user_plan', 'free'), ('generated_questions', None), ('evaluation_result', None),
        ('working_on', None), ('jd_text', ''),
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
    """Extract text from various file formats"""
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
        except:
            return "[PDF extraction failed - install PyMuPDF]"
    
    elif file_type in ['docx', 'doc']:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return '\n'.join([p.text for p in doc.paragraphs])
        except:
            return "[DOCX extraction failed - install python-docx]"
    
    elif file_type in ['vtt', 'srt']:
        text = content.decode('utf-8', errors='ignore')
        # Remove timestamps and formatting
        text = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', text)
        text = re.sub(r'WEBVTT.*?\n', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        return '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
    
    elif file_type in ['mp3', 'm4a', 'wav', 'mp4', 'webm']:
        return transcribe_audio(content, file_type)
    
    return content.decode('utf-8', errors='ignore')

def transcribe_audio(content, file_type):
    """Transcribe audio using Whisper API or local whisper"""
    # Try OpenAI Whisper API first
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key:
        try:
            with tempfile.NamedTemporaryFile(suffix=f".{file_type}", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            with open(tmp_path, 'rb') as audio_file:
                r = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    files={"file": audio_file},
                    data={"model": "whisper-1"},
                    timeout=300
                )
            os.unlink(tmp_path)
            
            if r.status_code == 200:
                return r.json().get("text", "")
        except Exception as e:
            pass
    
    return "[Audio transcription requires OPENAI_API_KEY environment variable for Whisper API]"

# ============================================
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=6000, action="interview"):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=180)
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


def generate_evaluation(transcript, jd_text, cv_texts, focus_areas, candidate_names):
    """
    Enhanced evaluation with proof-heavy scoring, CV validation, and multi-candidate comparison.
    """
    num_candidates = len(cv_texts)
    
    # Build candidate sections
    candidate_sections = ""
    for i, (cv, name) in enumerate(zip(cv_texts, candidate_names)):
        candidate_sections += f"""
### CANDIDATE {i+1}: {name}
**CV/Resume:**
{cv}

---
"""
    
    comparison_section = ""
    if num_candidates > 1:
        comparison_section = """
## PART 4: EXECUTIVE COMPARISON (Required for multiple candidates)

Create a side-by-side comparison table:

| Criteria | """ + " | ".join(candidate_names) + """ |
|----------|""" + "|".join(["------" for _ in candidate_names]) + """|
| Overall Score | X/100 | X/100 |
| Technical Skills | X/10 | X/10 |
| Communication | X/10 | X/10 |
| Cultural Fit | X/10 | X/10 |
| CV Accuracy | High/Med/Low | High/Med/Low |
| Recommendation | Hire/No Hire | Hire/No Hire |

### HEAD-TO-HEAD ANALYSIS:
For each focus area, who performed better and why?

### FINAL RANKING:
1. [Name] - [Why they're #1]
2. [Name] - [Why they're #2]
(etc.)

### HIRING RECOMMENDATION:
Which candidate(s) should advance? Why?
"""

    prompt = f"""You are an expert interview evaluator. Analyze this interview with PROOF-HEAVY scoring.

## JOB DESCRIPTION:
{jd_text}

## FOCUS AREAS TO EVALUATE:
{', '.join(focus_areas) if focus_areas else 'Technical Skills, Communication, Problem Solving, Cultural Fit, Leadership'}

## CANDIDATES:
{candidate_sections}

## INTERVIEW TRANSCRIPT:
{transcript}

---

# EVALUATION INSTRUCTIONS

You must be RIGOROUS and EVIDENCE-BASED. Every score must be backed by PROOF from the transcript.

**CRITICAL DISTINCTION:**
- A "CLAIM" is when candidate says they did something: "I led a team of 10"
- "PROOF" is when they demonstrate HOW: "We had daily standups, I handled conflicts by..."

Score based on PROOF, not claims. If someone claims experience but can't explain details, that's a RED FLAG.

---

## PART 1: INDIVIDUAL SCORECARDS

For EACH candidate, provide:

### [CANDIDATE NAME] - DETAILED SCORECARD

#### OVERALL SCORE: X/100

---

**For EACH focus area ({', '.join(focus_areas) if focus_areas else 'Technical Skills, Communication, Problem Solving, Cultural Fit, Leadership'}):**

#### [FOCUS AREA NAME]: X/10

**Score Justification:**
[2-3 sentences explaining WHY this score]

**PROOF Evidence (Required - 2-3 quotes):**
> Quote 1: "[Exact quote from transcript showing demonstrated skill]"
> Quote 2: "[Another quote proving capability]"

**Claims vs Reality:**
- CV Claims: [What their CV says about this area]
- Interview Reality: [Did they prove it? Specific examples?]
- Consistency: ✅ Verified / ⚠️ Partially Verified / ❌ Not Demonstrated

**Red Flags:** [Any concerning gaps or inconsistencies]

---

#### CV ACCURACY CHECK

| CV Claim | Interview Evidence | Verified? |
|----------|-------------------|-----------|
| [Claim 1 from CV] | [Quote or lack thereof] | ✅/⚠️/❌ |
| [Claim 2 from CV] | [Quote or lack thereof] | ✅/⚠️/❌ |
| [Claim 3 from CV] | [Quote or lack thereof] | ✅/⚠️/❌ |

**CV Trust Score:** X/10
- 10 = Everything verified with detailed proof
- 5 = Some claims verified, some not discussed
- 1 = Major discrepancies or evasive answers

---

## PART 2: INTERVIEW QUALITY ANALYSIS

### Talk Time Ratio
- Interviewer: X%
- Candidate: X%
- Assessment: [Was candidate given enough time? Did they dominate?]

### Communication Quality
- Clarity: X/10
- Structure: X/10 (STAR method, organized thoughts)
- Conciseness: X/10

### Technical Depth
- Surface Level: [Topics they mentioned but didn't go deep]
- Deep Knowledge: [Topics where they showed real expertise with specifics]

### Red Flags Summary
1. [Concern 1 with evidence]
2. [Concern 2 with evidence]

### Strengths Summary
1. [Strength 1 with evidence]
2. [Strength 2 with evidence]

---

## PART 3: HIRING RECOMMENDATION

### For [Each Candidate Name]:

**Recommendation:** [STRONG HIRE | HIRE | LEAN YES | ON THE FENCE | LEAN NO | NO HIRE | STRONG NO]

**Confidence Level:** [HIGH | MEDIUM | LOW] - [Why this confidence level]

**Key Reasons:**
1. [Reason 1]
2. [Reason 2]
3. [Reason 3]

**Risk Assessment:**
- Hiring Risk: [What could go wrong]
- Not Hiring Risk: [What we'd miss]

**Suggested Next Steps:**
- [ ] [Action item 1]
- [ ] [Action item 2]

**Questions for Next Round:**
1. [Probe question 1 to verify concerns]
2. [Probe question 2 to validate claims]

{comparison_section}

---

## PART 5: EXECUTIVE SUMMARY (1 paragraph)

[Concise summary for hiring manager - who to hire and why, key differentiators, main concerns]

---

Be thorough, specific, and evidence-based. No generic statements without proof."""

    return call_claude(prompt, max_tokens=8000, action="evaluate_interview")


# ============================================
# EXPORT FUNCTIONS
# ============================================

def export_to_markdown(content, filename="evaluation"):
    """Export evaluation to markdown file"""
    return content, f"{filename}.md"

def export_to_docx(content, filename="evaluation"):
    """Export evaluation to DOCX using docx-js"""
    try:
        # Create a Node.js script to generate DOCX
        js_content = f'''
const {{ Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, BorderStyle, Table, TableRow, TableCell, WidthType }} = require('docx');
const fs = require('fs');

const content = {json.dumps(content)};

// Parse markdown-like content into docx elements
function parseContent(text) {{
    const elements = [];
    const lines = text.split('\\n');
    
    for (const line of lines) {{
        if (line.startsWith('# ')) {{
            elements.push(new Paragraph({{
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({{ text: line.slice(2), bold: true, size: 32 }})]
            }}));
        }} else if (line.startsWith('## ')) {{
            elements.push(new Paragraph({{
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({{ text: line.slice(3), bold: true, size: 28 }})]
            }}));
        }} else if (line.startsWith('### ')) {{
            elements.push(new Paragraph({{
                heading: HeadingLevel.HEADING_3,
                children: [new TextRun({{ text: line.slice(4), bold: true, size: 24 }})]
            }}));
        }} else if (line.startsWith('#### ')) {{
            elements.push(new Paragraph({{
                children: [new TextRun({{ text: line.slice(5), bold: true, size: 22 }})]
            }}));
        }} else if (line.startsWith('> ')) {{
            elements.push(new Paragraph({{
                indent: {{ left: 720 }},
                children: [new TextRun({{ text: line.slice(2), italics: true, color: "666666" }})]
            }}));
        }} else if (line.startsWith('- ')) {{
            elements.push(new Paragraph({{
                bullet: {{ level: 0 }},
                children: [new TextRun(line.slice(2))]
            }}));
        }} else if (line.trim()) {{
            // Handle bold and other formatting
            let runs = [];
            let remaining = line;
            const boldRegex = /\\*\\*([^*]+)\\*\\*/g;
            let lastIndex = 0;
            let match;
            
            while ((match = boldRegex.exec(line)) !== null) {{
                if (match.index > lastIndex) {{
                    runs.push(new TextRun(line.slice(lastIndex, match.index)));
                }}
                runs.push(new TextRun({{ text: match[1], bold: true }}));
                lastIndex = match.index + match[0].length;
            }}
            if (lastIndex < line.length) {{
                runs.push(new TextRun(line.slice(lastIndex)));
            }}
            if (runs.length === 0) {{
                runs.push(new TextRun(line));
            }}
            elements.push(new Paragraph({{ children: runs }}));
        }} else {{
            elements.push(new Paragraph({{ children: [] }}));
        }}
    }}
    return elements;
}}

const doc = new Document({{
    styles: {{
        default: {{
            document: {{
                run: {{ font: "Arial", size: 22 }}
            }}
        }}
    }},
    sections: [{{
        properties: {{
            page: {{ margin: {{ top: 1440, right: 1440, bottom: 1440, left: 1440 }} }}
        }},
        children: parseContent(content)
    }}]
}});

Packer.toBuffer(doc).then(buffer => {{
    fs.writeFileSync('/tmp/evaluation.docx', buffer);
    console.log('DOCX created successfully');
}});
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_content)
            js_path = f.name
        
        result = subprocess.run(['node', js_path], capture_output=True, text=True, timeout=30)
        os.unlink(js_path)
        
        if os.path.exists('/tmp/evaluation.docx'):
            with open('/tmp/evaluation.docx', 'rb') as f:
                return f.read(), f"{filename}.docx"
        
    except Exception as e:
        st.warning(f"DOCX export failed: {e}. Falling back to Markdown.")
    
    return content.encode(), f"{filename}.md"

def export_to_pdf(content, filename="evaluation"):
    """Export evaluation to PDF using markdown → PDF conversion"""
    try:
        # Write markdown to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            md_path = f.name
        
        pdf_path = md_path.replace('.md', '.pdf')
        
        # Try pandoc first
        result = subprocess.run(
            ['pandoc', md_path, '-o', pdf_path, '--pdf-engine=wkhtmltopdf'],
            capture_output=True, text=True, timeout=30
        )
        
        os.unlink(md_path)
        
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
            os.unlink(pdf_path)
            return pdf_content, f"{filename}.pdf"
        
    except Exception as e:
        st.warning(f"PDF export failed: {e}. Falling back to Markdown.")
    
    return content.encode(), f"{filename}.md"


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

.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.output-box { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; margin: 16px 0; white-space: pre-wrap; color: #e5e5e5; }
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; z-index: 999; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }

.score-card { background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)); border: 1px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 20px; margin: 10px 0; }
.score-high { border-left: 4px solid #10b981; }
.score-mid { border-left: 4px solid #f59e0b; }
.score-low { border-left: 4px solid #ef4444; }

div[data-testid="stPopover"] button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 25px !important; padding: 10px 20px !important; font-weight: 600 !important; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3); }
</style>""", unsafe_allow_html=True)

# Auth
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;">
            <h1 style="margin:0;">Sharp Interview</h1>
            <p style="color:#9ca3af;">Questions • Evaluation • Scorecards</p>
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
    <div><h1 style="margin:0;font-size:28px;">Sharp Interview</h1><p style="color:#9ca3af;margin:0;">Questions • Evaluation • Scorecards</p></div>
</div>""", unsafe_allow_html=True)

# Tabs
tab_questions, tab_evaluate = st.tabs(["📝 Generate Questions", "📊 Interview Evaluation"])

# ============================================
# TAB 1: GENERATE QUESTIONS
# ============================================
with tab_questions:
    st.markdown("### 📝 Generate Interview Questions")
    
    c1, c2 = st.columns(2)
    
    with c1:
        job_title = st.text_input("🎯 Job Title *", placeholder="e.g., Senior Software Engineer")
        
        # JD Source
        jd_src = st.radio("Job Description:", ["📝 Paste", "📜 From Sharp JD", "📄 Upload"], horizontal=True, key="q_jd_src")
        
        if jd_src == "📜 From Sharp JD":
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
        
        # CV for bespoke questions
        st.markdown("##### 📄 Candidate CV (Optional)")
        cv_src = st.radio("CV Source:", ["None", "📝 Paste", "📄 Upload"], horizontal=True, key="q_cv_src")
        cv_text = ""
        if cv_src == "📝 Paste":
            cv_text = st.text_area("Paste CV:", height=100, key="q_cv_paste",
                placeholder="Paste candidate's resume for personalized questions...")
        elif cv_src == "📄 Upload":
            cv_file = st.file_uploader("Upload CV", type=['pdf', 'docx', 'txt'], key="q_cv_file")
            if cv_file:
                cv_text = extract_text_from_file(cv_file)
                st.success(f"✅ Loaded {cv_file.name}")
        
        exclude_illegal = st.checkbox("🔒 Exclude Legally Risky Questions", value=True,
            help="Excludes questions about age, religion, family status, etc.")
    
    if st.button("🎯 Generate Questions", type="primary", use_container_width=True):
        if not job_title or not requirements:
            st.warning("Please enter job title and requirements")
        else:
            st.session_state.working_on = "Generating questions..."
            result, _ = generate_questions(job_title, requirements, stage, duration, focus_areas, cv_text, exclude_illegal)
            st.session_state.working_on = None
            if not result.startswith("Error"):
                st.session_state.generated_questions = result
                st.rerun()
            else:
                st.error(result)
    
    if st.session_state.get('generated_questions'):
        st.markdown("---")
        st.markdown("### 📋 Generated Questions")
        st.markdown(st.session_state.generated_questions)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download Questions", st.session_state.generated_questions,
                f"interview_questions_{job_title.lower().replace(' ', '_')}.md", use_container_width=True)
        with c2:
            if st.button("🔄 Clear", use_container_width=True, key="clear_q"):
                st.session_state.generated_questions = None
                st.rerun()


# ============================================
# TAB 2: INTERVIEW EVALUATION (MERGED)
# ============================================
with tab_evaluate:
    st.markdown("### 📊 Interview Evaluation")
    st.markdown("*Upload transcript + JD + up to 3 CVs for comprehensive, proof-heavy scoring*")
    
    # Transcript Upload
    st.markdown("#### 📝 Interview Transcript *")
    transcript_src = st.radio("Transcript Source:", ["📝 Paste", "📄 Upload File"], horizontal=True, key="t_src")
    
    transcript = ""
    if transcript_src == "📄 Upload File":
        transcript_file = st.file_uploader(
            "Upload Transcript", 
            type=['txt', 'pdf', 'docx', 'vtt', 'srt', 'mp3', 'm4a', 'wav', 'mp4', 'webm'],
            key="t_file",
            help="Supports TXT, PDF, DOCX, VTT, SRT, and audio files (MP3, M4A, WAV)"
        )
        if transcript_file:
            with st.spinner("Processing file..."):
                transcript = extract_text_from_file(transcript_file)
            if transcript and not transcript.startswith("["):
                st.success(f"✅ Loaded {transcript_file.name} ({len(transcript)} characters)")
            else:
                st.warning(transcript)
    else:
        transcript = st.text_area("Paste Transcript:", height=200, key="t_paste",
            placeholder="Paste the interview transcript here...\n\nInterviewer: Tell me about yourself.\nCandidate: I've been working in...")
    
    st.markdown("---")
    
    # JD and CVs in columns
    col_jd, col_cv = st.columns(2)
    
    with col_jd:
        st.markdown("#### 📋 Job Description *")
        jd_src_eval = st.radio("JD Source:", ["📝 Paste", "📜 From Sharp JD", "📄 Upload"], horizontal=True, key="e_jd_src")
        
        jd_text_eval = ""
        if jd_src_eval == "📜 From Sharp JD":
            history = get_jd_history(15)
            if history:
                opts = {f"{j['job_title']}": j for j in history}
                sel = st.selectbox("Select:", list(opts.keys()), key="e_jd_sel")
                if sel:
                    jd_text_eval = opts[sel].get('generated_jd', '')
                    st.success(f"✅ Loaded")
            else:
                st.info("No saved JDs")
        elif jd_src_eval == "📄 Upload":
            jd_file = st.file_uploader("Upload JD", type=['pdf', 'docx', 'txt'], key="e_jd_file")
            if jd_file:
                jd_text_eval = extract_text_from_file(jd_file)
                st.success(f"✅ Loaded {jd_file.name}")
        else:
            jd_text_eval = st.text_area("Paste JD:", height=150, key="e_jd_paste",
                placeholder="Paste job description here...")
    
    with col_cv:
        st.markdown("#### 👥 Candidate CVs (Up to 3)")
        num_candidates = st.radio("Number of Candidates:", [1, 2, 3], horizontal=True, key="num_cands")
        
        cv_texts = []
        candidate_names = []
        
        for i in range(num_candidates):
            with st.expander(f"Candidate {i+1}", expanded=(i==0)):
                name = st.text_input(f"Name", key=f"cand_name_{i}", placeholder=f"Candidate {i+1} Name")
                candidate_names.append(name or f"Candidate {i+1}")
                
                cv_src_cand = st.radio("CV:", ["📝 Paste", "📄 Upload"], horizontal=True, key=f"cv_src_{i}")
                if cv_src_cand == "📄 Upload":
                    cv_file = st.file_uploader("Upload", type=['pdf', 'docx', 'txt'], key=f"cv_file_{i}")
                    if cv_file:
                        cv_texts.append(extract_text_from_file(cv_file))
                        st.success(f"✅ {cv_file.name}")
                    else:
                        cv_texts.append("")
                else:
                    cv_text = st.text_area("Paste CV:", height=100, key=f"cv_paste_{i}",
                        placeholder="Paste candidate's resume...")
                    cv_texts.append(cv_text)
    
    st.markdown("---")
    
    # Focus Areas
    st.markdown("#### 🎯 Focus Areas to Score")
    eval_focus = st.multiselect(
        "Select areas to evaluate:",
        ["Technical Skills", "Problem Solving", "Communication", "Leadership", "Cultural Fit",
         "Domain Expertise", "System Design", "Behavioral Competencies", "Strategic Thinking", "Team Collaboration"],
        default=["Technical Skills", "Communication", "Problem Solving", "Cultural Fit"],
        key="eval_focus"
    )
    
    # Generate Button
    if st.button("📊 Generate Evaluation", type="primary", use_container_width=True):
        if not transcript:
            st.warning("Please provide interview transcript")
        elif not jd_text_eval:
            st.warning("Please provide job description")
        elif not any(cv_texts):
            st.warning("Please provide at least one candidate CV")
        else:
            st.session_state.working_on = "Analyzing interview..."
            result, _ = generate_evaluation(
                transcript, 
                jd_text_eval, 
                [cv for cv in cv_texts if cv],  # Filter empty
                eval_focus,
                [n for n, cv in zip(candidate_names, cv_texts) if cv]  # Match names to non-empty CVs
            )
            st.session_state.working_on = None
            
            if not result.startswith("Error"):
                st.session_state.evaluation_result = result
                st.rerun()
            else:
                st.error(result)
    
    # Display Results
    if st.session_state.get('evaluation_result'):
        st.markdown("---")
        st.markdown("### 📊 Evaluation Results")
        
        # Export options
        st.markdown("#### 📥 Export Options")
        export_cols = st.columns(4)
        
        with export_cols[0]:
            md_content, md_name = export_to_markdown(st.session_state.evaluation_result, "interview_evaluation")
            st.download_button("📄 Markdown", md_content, md_name, use_container_width=True)
        
        with export_cols[1]:
            if st.button("📘 DOCX", use_container_width=True, key="export_docx"):
                docx_content, docx_name = export_to_docx(st.session_state.evaluation_result, "interview_evaluation")
                st.download_button("Download DOCX", docx_content, docx_name, key="dl_docx")
        
        with export_cols[2]:
            if st.button("📕 PDF", use_container_width=True, key="export_pdf"):
                pdf_content, pdf_name = export_to_pdf(st.session_state.evaluation_result, "interview_evaluation")
                st.download_button("Download PDF", pdf_content, pdf_name, key="dl_pdf")
        
        with export_cols[3]:
            if st.button("🔄 Clear Results", use_container_width=True, key="clear_eval"):
                st.session_state.evaluation_result = None
                st.rerun()
        
        st.markdown("---")
        
        # Display the evaluation
        st.markdown(st.session_state.evaluation_result)


# ============================================
# FLOATING FEEDBACK
# ============================================
st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)

_, _, _, fb_col = st.columns([4, 1, 1, 1])
with fb_col:
    with st.popover("💬 Feedback"):
        st.markdown("**Send Feedback**")
        fb_type = st.segmented_control("Type", ["🐛 Bug", "✨ Feature", "💬 General"], 
                                        default="💬 General", label_visibility="collapsed")
        fb_msg = st.text_area("Message", height=100, placeholder="What's on your mind?",
                              label_visibility="collapsed", key="fb_msg")
        if st.button("Send Feedback", type="primary", use_container_width=True, key="fb_send"):
            if fb_msg:
                t = fb_type.split()[1].lower() if fb_type else "general"
                success = submit_feedback("interview", t, fb_msg)
                if success:
                    st.success("Thanks! 🙏")
                else:
                    st.error("Failed to send")
