"""Sharp Interview - AI Interview Evaluation with Multi-Candidate Comparison"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re
import io
import tempfile
import zipfile
from xml.etree import ElementTree

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
GOD_PASSWORD = os.environ.get("GOD_PASSWORD", "G0DHum@n101!!!")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

APP_URLS = {"portal": "https://demo.sharphuman.com", "jd": "https://jd.sharphuman.com", "screen": "https://screen.sharphuman.com", "interview": "https://hire.sharphuman.com", "source": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com", "sales": "https://sales.sharphuman.com", "reach": "https://reach.sharphuman.com", "assistant": "https://assistant.sharphuman.com", "admin": "https://admin.sharphuman.com"}

FOCUS_AREAS = ["Technical Skills", "Problem Solving", "Communication", "Leadership", "Cultural Fit", "Experience Depth", "Motivation", "Collaboration"]
INTERVIEW_STAGES = ["Phone Screen", "Technical Round", "Hiring Manager", "Final Round", "Culture Fit", "Panel Interview"]

# ============================================
# AUTH FUNCTIONS
# ============================================

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions", 
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, 
            json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "interview", "is_active": True, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()}, timeout=10)
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
        if r.status_code == 200 and data.get("user"):
            return {"success": True, "message": "Check email!"}
        return {"success": False, "message": data.get("error_description") or "Failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def validate_session_token(token):
    if not token:
        return None
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
    except:
        pass
    return None

def log_usage(user_id, session_id, app, action, tokens_used=0):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/usage_logs", 
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, 
            json={"user_id": user_id, "session_id": session_id, "app": app, "action": action, "tokens_used": tokens_used}, timeout=5)
    except:
        pass

def submit_feedback(app, feedback_type, message):
    try:
        email = get_user_email()
        user_id = st.session_state.user.get("id") if st.session_state.user else None
        r = requests.post(f"{SUPABASE_URL}/rest/v1/user_feedback", 
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, 
            json={"user_id": user_id, "app": app, "feedback_type": feedback_type, "rating": 4, "message": message, "email": email}, timeout=10)
        return r.status_code in [200, 201]
    except:
        return False

def get_jd_history(limit=20):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god":
        return []
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/jd_history?user_id=eq.{user_id}&order=created_at.desc&limit={limit}", 
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def init_session():
    defaults = [
        ('authenticated', False), ('user', None), ('is_god', False), ('session_token', None),
        ('user_plan', 'free'), ('working_on', None), ('current_step', 'input'),
        ('candidates', []), ('current_candidate', None), ('comparison_result', None),
        ('questions_result', None), ('jd_text', ''), ('cv_text', '')
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
# FILE EXTRACTION (ROBUST)
# ============================================

def is_readable_text(text):
    """Check if extracted text is actually readable (not garbled)"""
    if not text or len(text.strip()) < 10:
        return False
    # Count printable ASCII and common unicode characters
    readable_chars = sum(1 for c in text if c.isprintable() or c in '\n\r\t')
    ratio = readable_chars / len(text)
    # Also check for too many special/control characters
    special_chars = sum(1 for c in text if ord(c) > 127 and not c.isalnum())
    special_ratio = special_chars / len(text) if len(text) > 0 else 0
    return ratio > 0.85 and special_ratio < 0.3

def clean_extracted_text(text):
    """Clean up extracted text by removing problematic characters"""
    if not text:
        return ""
    # Remove null bytes and other control characters (except newlines/tabs)
    cleaned = ''.join(c if c.isprintable() or c in '\n\r\t' else ' ' for c in text)
    # Normalize whitespace
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.name.split('.')[-1].lower()
    content = uploaded_file.read()
    uploaded_file.seek(0)
    
    if file_type == 'txt':
        text = content.decode('utf-8', errors='ignore')
        return clean_extracted_text(text)
    
    elif file_type == 'pdf':
        extracted_text = ""
        
        # Try PyMuPDF first
        try:
            import fitz
            pdf = fitz.open(stream=content, filetype="pdf")
            text_parts = []
            for page in pdf:
                page_text = page.get_text()
                if page_text:
                    text_parts.append(page_text)
            pdf.close()
            extracted_text = "\n".join(text_parts)
        except Exception as e:
            pass
        
        # Clean and validate the extracted text
        if extracted_text:
            cleaned = clean_extracted_text(extracted_text)
            if is_readable_text(cleaned):
                return cleaned
        
        # Fallback: try pdfplumber if available
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                extracted_text = "\n".join(text_parts)
                if extracted_text:
                    cleaned = clean_extracted_text(extracted_text)
                    if is_readable_text(cleaned):
                        return cleaned
        except:
            pass
        
        return "[PDF extraction failed - the PDF may be scanned/image-based. Please paste the content directly.]"
    
    elif file_type in ['docx', 'doc']:
        # Try python-docx
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            paragraphs = []
            for p in doc.paragraphs:
                if p.text.strip():
                    paragraphs.append(p.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            paragraphs.append(cell.text.strip())
            if paragraphs:
                text = '\n\n'.join(paragraphs)
                cleaned = clean_extracted_text(text)
                if is_readable_text(cleaned):
                    return cleaned
        except Exception as e:
            pass
        
        # Fallback: raw XML from ZIP
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                if 'word/document.xml' in z.namelist():
                    xml_content = z.read('word/document.xml')
                    tree = ElementTree.fromstring(xml_content)
                    texts = []
                    for elem in tree.iter():
                        if elem.text and elem.text.strip():
                            texts.append(elem.text.strip())
                    if texts:
                        text = ' '.join(texts)
                        cleaned = clean_extracted_text(text)
                        if is_readable_text(cleaned):
                            return cleaned
        except:
            pass
        
        return "[DOCX extraction failed - please paste the content directly]"
    
    elif file_type in ['vtt', 'srt']:
        text = content.decode('utf-8', errors='ignore')
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
                    r = requests.post("https://api.openai.com/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {openai_key}"},
                        files={"file": f}, data={"model": "whisper-1"}, timeout=300)
                os.unlink(tmp_path)
                if r.status_code == 200:
                    return r.json().get("text", "")
            except:
                pass
        return "[Audio transcription requires OPENAI_API_KEY]"
    
    return content.decode('utf-8', errors='ignore')

# ============================================
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=8000, action="interview"):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=180)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            if st.session_state.user:
                log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "interview", action, (len(prompt)+len(text))//4)
            return text, (len(prompt)+len(text))//4
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {e}", 0

# ============================================
# QUESTION GENERATOR
# ============================================

def generate_questions(job_title, requirements, stage, duration, focus_areas, cv_text="", exclude_illegal=True):
    prompt = f"""You are an expert interviewer. Generate interview questions for:

## ROLE: {job_title}

## REQUIREMENTS:
{requirements[:4000]}

## INTERVIEW STAGE: {stage}
## DURATION: {duration} minutes
## FOCUS AREAS: {', '.join(focus_areas)}

{f"## CANDIDATE CV (for tailored questions):{chr(10)}{cv_text[:3000]}" if cv_text else ""}

{"IMPORTANT: Exclude any questions that could be considered discriminatory (age, religion, family status, etc.)" if exclude_illegal else ""}

Generate a structured interview guide with:

```json
{{
    "opening": {{
        "icebreaker": "<warm-up question>",
        "role_intro": "<question about their understanding of the role>"
    }},
    "questions": [
        {{
            "category": "<focus area>",
            "question": "<the interview question>",
            "follow_ups": ["<follow-up 1>", "<follow-up 2>"],
            "what_to_look_for": "<what a good answer includes>",
            "red_flags": "<warning signs in answers>",
            "time_estimate": "<minutes>"
        }}
    ],
    "closing": {{
        "candidate_questions": "<invite their questions>",
        "next_steps": "<explain process>",
        "timeline": "<when they'll hear back>"
    }},
    "evaluation_criteria": [
        {{
            "criterion": "<what to evaluate>",
            "weight": "<High/Medium/Low>",
            "indicators": ["<positive indicator>", "<negative indicator>"]
        }}
    ]
}}
```

Generate {max(3, duration // 10)} questions appropriate for {duration} minutes. Prioritize behavioral (STAR) and situational questions."""

    return call_claude(prompt, max_tokens=4000, action="generate_questions")

# ============================================
# EVALUATION FUNCTIONS
# ============================================

def evaluate_candidate(candidate_name, cv_text, jd_text, transcript, focus_areas):
    prompt = f"""You are an expert interview evaluator. Analyze this candidate's interview.

## CANDIDATE: {candidate_name}

## JOB DESCRIPTION
{jd_text[:5000]}

## CANDIDATE CV
{cv_text[:5000]}

## INTERVIEW TRANSCRIPT
{transcript[:12000]}

## FOCUS AREAS: {', '.join(focus_areas)}

---

## EVALUATION RULES:
1. **PROOF vs CLAIMS**: Score based on DEMONSTRATED ability with specifics, not just claims
2. **CV Verification**: Check if CV claims are backed up in the interview
3. **Red Flags**: Note evasive answers, inconsistencies, or gaps

Return JSON:

```json
{{
    "candidate_name": "{candidate_name}",
    "overall_score": <0-100>,
    "overall_summary": "<2-3 sentence summary>",
    "recommendation": "<STRONG HIRE | HIRE | LEAN YES | ON THE FENCE | LEAN NO | NO HIRE | STRONG NO>",
    "recommendation_confidence": "<HIGH | MEDIUM | LOW>",
    "focus_areas": [
        {{
            "area": "<Focus Area>",
            "score": <0-10>,
            "score_label": "<Excellent|Good|Adequate|Weak|Not Demonstrated>",
            "evidence": ["<quote from transcript>"],
            "assessment": "<2-3 sentence assessment>"
        }}
    ],
    "cv_verification": {{
        "trust_score": <0-10>,
        "verified_claims": ["<verified>"],
        "unverified_claims": ["<not demonstrated>"],
        "inconsistencies": ["<any contradictions>"]
    }},
    "interview_quality": {{
        "communication_score": <0-10>,
        "depth_of_answers": "<Deep|Moderate|Surface-level>",
        "engagement_level": "<High|Medium|Low>",
        "red_flags": ["<concern>"],
        "green_flags": ["<positive>"]
    }},
    "strengths": ["<strength 1>", "<strength 2>"],
    "concerns": ["<concern 1>", "<concern 2>"],
    "questions_for_next_round": ["<question>"],
    "hiring_risk": "<risk if hired>",
    "not_hiring_risk": "<risk if not hired>"
}}
```

Be specific. Use exact quotes as evidence."""

    return call_claude(prompt, max_tokens=6000, action="evaluate_candidate")

def compare_candidates(candidates_data):
    candidates_json = json.dumps(candidates_data, indent=2)
    
    prompt = f"""Compare these candidates and provide hiring recommendation:

## CANDIDATES
{candidates_json}

Return JSON:

```json
{{
    "comparison_table": {{
        "headers": ["Metric", "Candidate1", "Candidate2", ...],
        "rows": [
            ["Overall Score", ...],
            ["Recommendation", ...],
            ["Technical", ...],
            ["Communication", ...],
            ["CV Trust", ...],
            ["Key Strength", ...],
            ["Main Concern", ...]
        ]
    }},
    "head_to_head": [
        {{
            "area": "<area>",
            "winner": "<name>",
            "analysis": "<why>"
        }}
    ],
    "final_ranking": [
        {{
            "rank": 1,
            "candidate": "<name>",
            "reasoning": "<why>"
        }}
    ],
    "hiring_recommendation": {{
        "primary_choice": "<name>",
        "primary_reasoning": "<why>",
        "backup_choice": "<name or None>",
        "backup_reasoning": "<why>",
        "proceed_to_next_round": ["<names>"],
        "do_not_proceed": ["<names>"]
    }},
    "executive_summary": "<3-4 sentences for hiring manager>"
}}
```"""

    return call_claude(prompt, max_tokens=5000, action="compare_candidates")

# ============================================
# EXPORT FUNCTIONS
# ============================================

def export_to_markdown(data, title="Evaluation"):
    if isinstance(data, dict):
        md = f"# {title}\n\n"
        md += f"**Overall Score:** {data.get('overall_score', 'N/A')}/100\n"
        md += f"**Recommendation:** {data.get('recommendation', 'N/A')}\n\n"
        md += f"## Summary\n{data.get('overall_summary', '')}\n\n"
        
        md += "## Strengths\n"
        for s in data.get('strengths', []):
            md += f"- {s}\n"
        
        md += "\n## Concerns\n"
        for c in data.get('concerns', []):
            md += f"- {c}\n"
        
        md += "\n## Focus Areas\n"
        for fa in data.get('focus_areas', []):
            md += f"### {fa.get('area')} - {fa.get('score', 0)}/10\n"
            md += f"{fa.get('assessment', '')}\n\n"
        
        return md
    return str(data)

def export_to_docx(data, title="Evaluation"):
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        doc.add_heading(title, 0)
        
        if isinstance(data, dict):
            p = doc.add_paragraph()
            p.add_run(f"Overall Score: {data.get('overall_score', 'N/A')}/100").bold = True
            doc.add_paragraph(f"Recommendation: {data.get('recommendation', 'N/A')}")
            doc.add_paragraph(data.get('overall_summary', ''))
            
            doc.add_heading("Strengths", level=1)
            for s in data.get('strengths', []):
                doc.add_paragraph(s, style='List Bullet')
            
            doc.add_heading("Concerns", level=1)
            for c in data.get('concerns', []):
                doc.add_paragraph(c, style='List Bullet')
            
            doc.add_heading("Focus Areas", level=1)
            for fa in data.get('focus_areas', []):
                doc.add_heading(f"{fa.get('area')} - {fa.get('score', 0)}/10", level=2)
                doc.add_paragraph(fa.get('assessment', ''))
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        return None

# ============================================
# DISPLAY FUNCTIONS
# ============================================

def display_candidate_result(result_data, candidate_name):
    score = result_data.get('overall_score', 0)
    score_color = "#10b981" if score >= 75 else "#eab308" if score >= 50 else "#ef4444"
    rec = result_data.get('recommendation', 'N/A')
    rec_color = "#10b981" if "HIRE" in rec and "NO" not in rec else "#ef4444" if "NO" in rec else "#eab308"
    
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border-radius:16px;padding:30px;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
            <div>
                <h2 style="margin:0;color:#fff;">{candidate_name}</h2>
                <p style="color:#9ca3af;margin:4px 0 0;">{result_data.get('overall_summary', '')}</p>
            </div>
            <div style="text-align:center;">
                <p style="color:#9ca3af;margin:0;font-size:12px;">OVERALL SCORE</p>
                <p style="color:{score_color};font-size:48px;font-weight:bold;margin:0;">{score}<span style="font-size:18px;color:#6b7280;">/100</span></p>
                <span style="background:{rec_color};color:white;padding:6px 16px;border-radius:20px;font-size:12px;font-weight:600;">{rec}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Strengths")
        for s in result_data.get('strengths', []):
            st.markdown(f"<div style='background:rgba(16,185,129,0.1);border-left:3px solid #10b981;padding:10px 14px;margin:6px 0;border-radius:0 8px 8px 0;font-size:14px;'>{s}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("#### Concerns")
        for c in result_data.get('concerns', []):
            st.markdown(f"<div style='background:rgba(239,68,68,0.1);border-left:3px solid #ef4444;padding:10px 14px;margin:6px 0;border-radius:0 8px 8px 0;font-size:14px;'>{c}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Focus Area Scores")
    
    for area in result_data.get('focus_areas', []):
        area_name = str(area.get('area', 'Unknown Area'))
        # Sanitize area name - remove any non-printable characters
        area_name = ''.join(c if c.isprintable() else '' for c in area_name)
        if not area_name:
            area_name = "Focus Area"
        
        area_score = area.get('score', 0)
        if not isinstance(area_score, (int, float)):
            try:
                area_score = int(area_score)
            except:
                area_score = 0
        
        area_color = "#10b981" if area_score >= 8 else "#eab308" if area_score >= 6 else "#f97316" if area_score >= 4 else "#ef4444"
        
        with st.expander(f"{area_name} — {area_score}/10"):
            assessment = str(area.get('assessment', 'No assessment available'))
            assessment = ''.join(c if c.isprintable() or c in '\n' else ' ' for c in assessment)
            st.markdown(f"**Assessment:** {assessment}")
            if area.get('evidence'):
                st.markdown("**Evidence:**")
                for ev in area.get('evidence', []):
                    ev_clean = ''.join(c if c.isprintable() or c in '\n' else ' ' for c in str(ev))
                    st.markdown(f"<div style='background:#1a1a2e;border-left:3px solid #6366f1;padding:10px 14px;margin:6px 0;border-radius:0 8px 8px 0;font-style:italic;color:#a5b4fc;'>\"{ev_clean}\"</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    cv_ver = result_data.get('cv_verification', {})
    trust_score = cv_ver.get('trust_score', 0)
    trust_color = "#10b981" if trust_score >= 8 else "#eab308" if trust_score >= 6 else "#ef4444"
    
    st.markdown("### CV Verification")
    st.markdown(f"<div style='display:inline-block;background:rgba(99,102,241,0.1);padding:8px 16px;border-radius:8px;margin-bottom:12px;'><span style='color:#9ca3af;'>CV Trust Score:</span> <span style='color:{trust_color};font-weight:bold;font-size:18px;'>{trust_score}/10</span></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Verified Claims**")
        for v in cv_ver.get('verified_claims', []):
            st.markdown(f"- {v}")
    with col2:
        st.markdown("**Unverified Claims**")
        for u in cv_ver.get('unverified_claims', []):
            st.markdown(f"- {u}")
    
    if cv_ver.get('inconsistencies'):
        st.markdown("**Inconsistencies**")
        for i in cv_ver.get('inconsistencies', []):
            st.warning(i)
    
    st.markdown("---")
    
    iq = result_data.get('interview_quality', {})
    st.markdown("### Interview Quality")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Communication", f"{iq.get('communication_score', 0)}/10")
    with col2:
        st.metric("Answer Depth", iq.get('depth_of_answers', 'N/A'))
    with col3:
        st.metric("Engagement", iq.get('engagement_level', 'N/A'))
    
    col1, col2 = st.columns(2)
    with col1:
        if iq.get('green_flags'):
            st.markdown("**Green Flags**")
            for g in iq.get('green_flags', []):
                st.markdown(f"- {g}")
    with col2:
        if iq.get('red_flags'):
            st.markdown("**Red Flags**")
            for r in iq.get('red_flags', []):
                st.markdown(f"- {r}")
    
    st.markdown("---")
    
    st.markdown("### Risk Assessment")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Risk if Hired:**")
        st.info(result_data.get('hiring_risk', 'N/A'))
    with col2:
        st.markdown("**Risk if NOT Hired:**")
        st.info(result_data.get('not_hiring_risk', 'N/A'))
    
    if result_data.get('questions_for_next_round'):
        st.markdown("### Questions for Next Round")
        for q in result_data.get('questions_for_next_round', []):
            st.markdown(f"- {q}")

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp Interview", page_icon="🎯", layout="wide")
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
[data-baseweb="tag"] { background: rgba(99,102,241,0.3) !important; color: white !important; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stDownloadButton > button { background: #1a1a2e !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; }
[data-testid="stFileUploader"] { background: #12121a !important; border: 1px dashed rgba(99,102,241,0.3) !important; border-radius: 8px !important; }
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 8px; border-bottom: 1px solid rgba(99,102,241,0.2); }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #9ca3af !important; }
.stTabs [aria-selected="true"] { color: #fff !important; border-bottom: 2px solid #6366f1 !important; }
.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.input-card { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; margin: 12px 0; }
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
            <h1 style="margin:0;">Sharp Interview</h1>
            <p style="color:#9ca3af;">AI Interview Evaluation</p>
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
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
    st.stop()

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
    apps = [("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"), ("interview", "🎯 Interview"), ("source", "🎣 Sourcing"), ("content", "✍️ Content"), ("sales", "💰 Sales"), ("reach", "🚀 Reach"), ("assistant", "🤖 Assistant")]
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
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:30px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:50px;">
    <div>
        <h1 style="margin:0;font-size:28px;">Sharp Interview</h1>
        <p style="color:#9ca3af;margin:0;">AI-Powered Interview Evaluation</p>
    </div>
</div>""", unsafe_allow_html=True)

# Show evaluated candidates
if st.session_state.candidates:
    names = [c.get("candidate_name", "Candidate") for c in st.session_state.candidates]
    chips = " ".join([f"<span style='display:inline-block;background:rgba(99,102,241,0.2);color:#a5b4fc;padding:6px 14px;border-radius:20px;margin:4px;font-size:13px;'>{n}</span>" for n in names])
    st.markdown(f"**Evaluated:** {chips}", unsafe_allow_html=True)

# Main Tabs
tab_evaluate, tab_questions = st.tabs(["🎯 Evaluate Interview", "❓ Generate Questions"])

# ============================================
# TAB 1: EVALUATE INTERVIEW
# ============================================
with tab_evaluate:
    step = st.session_state.current_step
    
    # COMPARISON VIEW
    if step == 'comparison' and len(st.session_state.candidates) >= 2:
        st.markdown("## Candidate Comparison")
        
        if st.button("← Back to Results"):
            st.session_state.current_step = 'results'
            st.rerun()
        
        if st.session_state.comparison_result:
            try:
                txt = st.session_state.comparison_result
                m = re.search(r'```json\s*(.*?)\s*```', txt, re.DOTALL)
                comp = json.loads(m.group(1) if m else txt)
                
                st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border-radius:16px;padding:24px;margin-bottom:24px;">
                    <h3 style="margin:0 0 12px;">Executive Summary</h3>
                    <p style="color:#e5e5e5;margin:0;">{comp.get('executive_summary', '')}</p>
                </div>""", unsafe_allow_html=True)
                
                st.markdown("### Final Ranking")
                for r in comp.get('final_ranking', []):
                    rank_color = "#10b981" if r['rank'] == 1 else "#eab308" if r['rank'] == 2 else "#6b7280"
                    st.markdown(f"""<div style="background:#12121a;border-left:4px solid {rank_color};padding:16px;margin:8px 0;border-radius:0 12px 12px 0;">
                        <span style="color:{rank_color};font-size:24px;font-weight:bold;">#{r['rank']}</span>
                        <span style="color:#fff;font-size:18px;margin-left:12px;">{r['candidate']}</span>
                        <p style="color:#9ca3af;margin:8px 0 0;">{r['reasoning']}</p>
                    </div>""", unsafe_allow_html=True)
                
                hr = comp.get('hiring_recommendation', {})
                st.markdown("### Hiring Recommendation")
                st.success(f"**Primary Choice:** {hr.get('primary_choice', 'N/A')}\n\n{hr.get('primary_reasoning', '')}")
                if hr.get('backup_choice') and hr.get('backup_choice') != 'None':
                    st.info(f"**Backup:** {hr.get('backup_choice')}")
                
                st.download_button("📥 Download Comparison", txt, "comparison.md", use_container_width=True)
                
            except Exception as e:
                st.error(f"Parse error: {e}")
                st.text(st.session_state.comparison_result)
    
    # RESULTS VIEW
    elif step == 'results' and st.session_state.current_candidate:
        result = st.session_state.current_candidate
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← New Evaluation"):
                st.session_state.current_step = 'input'
                st.session_state.current_candidate = None
                st.session_state.candidates = []
                st.session_state.comparison_result = None
                st.rerun()
        with col2:
            if len(st.session_state.candidates) < 4:
                if st.button(f"➕ Add Candidate ({len(st.session_state.candidates)}/4)"):
                    st.session_state.current_step = 'input'
                    st.session_state.current_candidate = None
                    st.rerun()
        with col3:
            if len(st.session_state.candidates) >= 2:
                if st.button("📊 Compare All"):
                    st.session_state.working_on = "Comparing..."
                    comp_result, _ = compare_candidates(st.session_state.candidates)
                    st.session_state.working_on = None
                    st.session_state.comparison_result = comp_result
                    st.session_state.current_step = 'comparison'
                    st.rerun()
        
        st.markdown("---")
        display_candidate_result(result, result.get('candidate_name', 'Candidate'))
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            md_content = export_to_markdown(result, result.get('candidate_name', 'Evaluation'))
            st.download_button("📥 Download MD", md_content, f"{result.get('candidate_name', 'eval')}.md", use_container_width=True)
        with col2:
            docx_content = export_to_docx(result, result.get('candidate_name', 'Evaluation'))
            if docx_content:
                st.download_button("📥 Download DOCX", docx_content, f"{result.get('candidate_name', 'eval')}.docx", use_container_width=True)
        with col3:
            st.download_button("📥 Download JSON", json.dumps(result, indent=2), f"{result.get('candidate_name', 'eval')}.json", use_container_width=True)
    
    # INPUT VIEW
    else:
        st.markdown("### Evaluate Interview")
        
        candidate_num = len(st.session_state.candidates) + 1
        if candidate_num > 1:
            st.info(f"Adding Candidate #{candidate_num} of 4")
        
        candidate_name = st.text_input("👤 Candidate Name", placeholder="John Smith", key=f"name_{candidate_num}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown("**📄 Job Description**")
            jd_src = st.radio("Source:", ["📝 Paste", "📜 History", "📁 Upload"], horizontal=True, key=f"jd_src_{candidate_num}")
            
            jd_text = ""
            if jd_src == "📜 History":
                history = get_jd_history(20)
                if history:
                    opts = {f"{j['job_title']} ({j['created_at'][:10]})": j for j in history}
                    sel = st.selectbox("Select JD:", list(opts.keys()), key=f"jd_hist_{candidate_num}")
                    if sel:
                        jd_text = opts[sel].get('generated_jd', '')
                        st.success(f"Loaded: {opts[sel].get('job_title')}")
                else:
                    st.info("No saved JDs")
            elif jd_src == "📁 Upload":
                jd_file = st.file_uploader("Upload JD", type=['txt', 'pdf', 'docx'], key=f"jd_file_{candidate_num}")
                if jd_file:
                    jd_text = extract_text_from_file(jd_file)
                    if jd_text and not jd_text.startswith("["):
                        st.success(f"Loaded ({len(jd_text):,} chars)")
                    else:
                        st.warning(jd_text)
            else:
                jd_text = st.text_area("Paste JD:", height=150, key=f"jd_paste_{candidate_num}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown("**📋 Candidate CV**")
            cv_src = st.radio("Source:", ["📝 Paste", "📁 Upload"], horizontal=True, key=f"cv_src_{candidate_num}")
            
            cv_text = ""
            if cv_src == "📁 Upload":
                cv_file = st.file_uploader("Upload CV", type=['txt', 'pdf', 'docx'], key=f"cv_file_{candidate_num}")
                if cv_file:
                    cv_text = extract_text_from_file(cv_file)
                    if cv_text and not cv_text.startswith("["):
                        st.success(f"Loaded ({len(cv_text):,} chars)")
                    else:
                        st.warning(cv_text)
            else:
                cv_text = st.text_area("Paste CV:", height=150, key=f"cv_paste_{candidate_num}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown("**🎙️ Interview Transcript**")
            trans_src = st.radio("Source:", ["📝 Paste", "📁 Upload"], horizontal=True, key=f"trans_src_{candidate_num}")
            
            transcript = ""
            if trans_src == "📁 Upload":
                trans_file = st.file_uploader("Upload Transcript", type=['txt', 'pdf', 'docx', 'vtt', 'srt', 'mp3', 'wav', 'm4a'], key=f"trans_file_{candidate_num}")
                if trans_file:
                    with st.spinner("Processing..."):
                        transcript = extract_text_from_file(trans_file)
                    if transcript and not transcript.startswith("["):
                        st.success(f"Loaded ({len(transcript):,} chars)")
                        with st.expander("Preview"):
                            st.text(transcript[:1500] + ("..." if len(transcript) > 1500 else ""))
                    else:
                        st.warning(transcript)
            else:
                transcript = st.text_area("Paste Transcript:", height=200, placeholder="Interviewer: Thanks for joining...\nCandidate: Thank you...", key=f"trans_paste_{candidate_num}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown("**🎯 Focus Areas**")
            focus_areas = st.multiselect("Select:", FOCUS_AREAS, default=["Technical Skills", "Communication", "Problem Solving"], key=f"focus_{candidate_num}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🚀 Evaluate Candidate", type="primary", use_container_width=True):
            if not candidate_name:
                st.warning("Enter candidate name")
            elif not jd_text or len(jd_text) < 50:
                st.warning("Provide JD (min 50 chars)")
            elif not cv_text or len(cv_text) < 50:
                st.warning("Provide CV (min 50 chars)")
            elif not transcript or len(transcript) < 100:
                st.warning("Provide transcript (min 100 chars)")
            elif not focus_areas:
                st.warning("Select at least one focus area")
            else:
                st.session_state.working_on = f"Evaluating {candidate_name}..."
                result, _ = evaluate_candidate(candidate_name, cv_text, jd_text, transcript, focus_areas)
                st.session_state.working_on = None
                
                if not str(result).startswith("Error"):
                    try:
                        m = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                        parsed = json.loads(m.group(1) if m else result)
                        parsed['candidate_name'] = candidate_name
                        st.session_state.candidates.append(parsed)
                        st.session_state.current_candidate = parsed
                        st.session_state.current_step = 'results'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Parse error: {e}")
                        st.text(result)
                else:
                    st.error(result)

# ============================================
# TAB 2: GENERATE QUESTIONS
# ============================================
with tab_questions:
    st.markdown("### Generate Interview Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("**Job Details**")
        job_title = st.text_input("Job Title", placeholder="Senior Software Engineer", key="q_title")
        
        q_jd_src = st.radio("JD Source:", ["📝 Paste", "📜 History", "📁 Upload"], horizontal=True, key="q_jd_src")
        
        requirements = ""
        if q_jd_src == "📜 History":
            history = get_jd_history(20)
            if history:
                opts = {f"{j['job_title']} ({j['created_at'][:10]})": j for j in history}
                sel = st.selectbox("Select:", list(opts.keys()), key="q_jd_hist")
                if sel:
                    requirements = opts[sel].get('generated_jd', '')
                    st.success(f"Loaded: {opts[sel].get('job_title')}")
            else:
                st.info("No saved JDs")
        elif q_jd_src == "📁 Upload":
            q_jd_file = st.file_uploader("Upload JD", type=['txt', 'pdf', 'docx'], key="q_jd_file")
            if q_jd_file:
                requirements = extract_text_from_file(q_jd_file)
                if requirements and not requirements.startswith("["):
                    st.success("Loaded")
                else:
                    st.warning(requirements)
        else:
            requirements = st.text_area("Requirements:", height=150, key="q_requirements")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("**Interview Settings**")
        stage = st.selectbox("Stage", INTERVIEW_STAGES, key="q_stage")
        duration = st.slider("Duration (min)", 15, 90, 45, 5, key="q_duration")
        q_focus = st.multiselect("Focus Areas", FOCUS_AREAS, default=["Technical Skills", "Communication"], key="q_focus")
        exclude_illegal = st.checkbox("Exclude illegal questions", value=True, key="q_exclude")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("**Candidate CV (optional)**")
        q_cv_src = st.radio("Source:", ["None", "📝 Paste", "📁 Upload"], horizontal=True, key="q_cv_src")
        
        q_cv_text = ""
        if q_cv_src == "📝 Paste":
            q_cv_text = st.text_area("Paste CV:", height=100, key="q_cv_paste")
        elif q_cv_src == "📁 Upload":
            q_cv_file = st.file_uploader("Upload CV", type=['txt', 'pdf', 'docx'], key="q_cv_file")
            if q_cv_file:
                q_cv_text = extract_text_from_file(q_cv_file)
                if q_cv_text and not q_cv_text.startswith("["):
                    st.success("Loaded")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("❓ Generate Questions", type="primary", use_container_width=True):
        if not job_title:
            st.warning("Enter job title")
        elif not requirements or len(requirements) < 50:
            st.warning("Provide requirements (min 50 chars)")
        elif not q_focus:
            st.warning("Select focus areas")
        else:
            st.session_state.working_on = "Generating questions..."
            result, _ = generate_questions(job_title, requirements, stage, duration, q_focus, q_cv_text, exclude_illegal)
            st.session_state.working_on = None
            st.session_state.questions_result = result
    
    if st.session_state.get('questions_result'):
        result = st.session_state.questions_result
        
        if not str(result).startswith("Error"):
            try:
                m = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                data = json.loads(m.group(1) if m else result)
                
                st.markdown("---")
                st.markdown("### Interview Guide")
                
                # Opening
                opening = data.get('opening', {})
                st.markdown("#### Opening")
                st.info(f"**Icebreaker:** {opening.get('icebreaker', 'N/A')}")
                st.info(f"**Role Intro:** {opening.get('role_intro', 'N/A')}")
                
                # Questions
                st.markdown("#### Questions")
                for i, q in enumerate(data.get('questions', []), 1):
                    with st.expander(f"**Q{i}: {q.get('category', '')}** ({q.get('time_estimate', '')} min)"):
                        st.markdown(f"**Question:** {q.get('question', '')}")
                        
                        if q.get('follow_ups'):
                            st.markdown("**Follow-ups:**")
                            for f in q.get('follow_ups', []):
                                st.markdown(f"- {f}")
                        
                        st.markdown(f"**Look for:** {q.get('what_to_look_for', '')}")
                        st.markdown(f"**Red flags:** {q.get('red_flags', '')}")
                
                # Closing
                closing = data.get('closing', {})
                st.markdown("#### Closing")
                st.info(f"**Candidate Questions:** {closing.get('candidate_questions', 'N/A')}")
                st.info(f"**Next Steps:** {closing.get('next_steps', 'N/A')}")
                
                # Evaluation Criteria
                if data.get('evaluation_criteria'):
                    st.markdown("#### Evaluation Criteria")
                    for ec in data.get('evaluation_criteria', []):
                        st.markdown(f"- **{ec.get('criterion')}** ({ec.get('weight')})")
                
                st.download_button("📥 Download Guide", json.dumps(data, indent=2), "interview_guide.json", use_container_width=True)
                
            except Exception as e:
                st.error(f"Parse error: {e}")
                st.text(result)
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
                fb_type = ft.split()[1].lower() if ft else "general"
                if submit_feedback("interview", fb_type, fm):
                    st.success("Thanks!")
                else:
                    st.error("Failed")
