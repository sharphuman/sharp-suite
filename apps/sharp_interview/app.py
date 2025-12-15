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
    # Count alphabetic characters - real text should have words
    alpha_chars = sum(1 for c in text if c.isalpha())
    alpha_ratio = alpha_chars / len(text) if len(text) > 0 else 0
    # Real text should have at least 30% letters
    return alpha_ratio > 0.3

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
        
        # Try PyMuPDF first with multiple extraction methods
        try:
            import fitz
            pdf = fitz.open(stream=content, filetype="pdf")
            text_parts = []
            for page in pdf:
                # Try standard text extraction
                page_text = page.get_text("text")
                if not page_text or not page_text.strip():
                    # Try with different flags
                    page_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                if not page_text or not page_text.strip():
                    # Try blocks extraction
                    blocks = page.get_text("blocks")
                    page_text = "\n".join([b[4] for b in blocks if b[6] == 0])  # type 0 = text
                if page_text and page_text.strip():
                    text_parts.append(page_text)
            pdf.close()
            extracted_text = "\n".join(text_parts)
        except Exception as e:
            pass
        
        # If we got text, clean and validate it
        if extracted_text and extracted_text.strip():
            cleaned = clean_extracted_text(extracted_text)
            if is_readable_text(cleaned):
                return cleaned
        
        # Fallback: try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                extracted_text = "\n".join(text_parts)
                if extracted_text and extracted_text.strip():
                    cleaned = clean_extracted_text(extracted_text)
                    if is_readable_text(cleaned):
                        return cleaned
        except:
            pass
        
        # Fallback 3: Try PyPDF2 if available
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(content))
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            extracted_text = "\n".join(text_parts)
            if extracted_text and extracted_text.strip():
                cleaned = clean_extracted_text(extracted_text)
                if is_readable_text(cleaned):
                    return cleaned
        except:
            pass
        
        # Last resort: if we got ANY text from PyMuPDF, return it with a warning
        try:
            import fitz
            pdf = fitz.open(stream=content, filetype="pdf")
            text_parts = []
            for page in pdf:
                page_text = page.get_text()
                if page_text:
                    text_parts.append(page_text)
            pdf.close()
            if text_parts:
                result = clean_extracted_text("\n".join(text_parts))
                if len(result) > 50:  # If we got something substantial
                    return result
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
        elif r.status_code == 500:
            return "Error: 500 - Claude API server error. Please try again in a moment.", 0
        elif r.status_code == 529:
            return "Error: 529 - Claude API overloaded. Please wait a moment and try again.", 0
        elif r.status_code == 429:
            return "Error: 429 - Rate limited. Please wait a moment and try again.", 0
        else:
            try:
                err_detail = r.json().get("error", {}).get("message", r.text[:200])
            except:
                err_detail = r.text[:200]
            return f"Error: {r.status_code} - {err_detail}", 0
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The transcript may be too long - try shortening it.", 0
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

def clean_text(text):
    """Clean text for export - removes unprintable characters."""
    if not text:
        return ""
    return ''.join(c if c.isprintable() or c in '\n\r\t' else ' ' for c in str(text))

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

def export_comparison_to_markdown(comp_data, candidates):
    """Export comparison to Markdown format."""
    md = "# Candidate Comparison Report\n\n"
    md += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
    md += f"**Candidates Compared:** {len(candidates)}\n\n"
    
    # Executive Summary
    md += "## Executive Summary\n\n"
    md += f"{comp_data.get('executive_summary', 'No summary available.')}\n\n"
    
    # Comparison Table
    table = comp_data.get('comparison_table', {})
    if table.get('headers') and table.get('rows'):
        md += "## Comparison Matrix\n\n"
        headers = table['headers']
        md += "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        for row in table['rows']:
            md += "| " + " | ".join(str(cell) for cell in row) + " |\n"
        md += "\n"
    
    # Head to Head
    if comp_data.get('head_to_head'):
        md += "## Head-to-Head Analysis\n\n"
        for item in comp_data['head_to_head']:
            md += f"### {item.get('area', 'Unknown')}\n"
            md += f"**Winner:** {item.get('winner', 'N/A')}\n\n"
            md += f"{item.get('analysis', '')}\n\n"
    
    # Final Ranking
    md += "## Final Ranking\n\n"
    for r in comp_data.get('final_ranking', []):
        md += f"### #{r.get('rank', '?')} - {r.get('candidate', 'Unknown')}\n"
        md += f"{r.get('reasoning', '')}\n\n"
    
    # Hiring Recommendation
    hr = comp_data.get('hiring_recommendation', {})
    md += "## Hiring Recommendation\n\n"
    md += f"**Primary Choice:** {hr.get('primary_choice', 'N/A')}\n\n"
    md += f"{hr.get('primary_reasoning', '')}\n\n"
    
    if hr.get('backup_choice') and hr.get('backup_choice') != 'None':
        md += f"**Backup Choice:** {hr.get('backup_choice', 'N/A')}\n\n"
        md += f"{hr.get('backup_reasoning', '')}\n\n"
    
    if hr.get('proceed_to_next_round'):
        md += f"**Proceed to Next Round:** {', '.join(hr.get('proceed_to_next_round', []))}\n\n"
    
    if hr.get('do_not_proceed'):
        md += f"**Do Not Proceed:** {', '.join(hr.get('do_not_proceed', []))}\n\n"
    
    return md

def export_comparison_to_docx(comp_data, candidates):
    """Export comparison to DOCX format."""
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
        
        doc = Document()
        
        # Title
        title = doc.add_heading('Candidate Comparison Report', 0)
        
        # Metadata
        doc.add_paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        doc.add_paragraph(f"Candidates Compared: {len(candidates)}")
        doc.add_paragraph()
        
        # Executive Summary
        doc.add_heading('Executive Summary', level=1)
        summary = clean_text(comp_data.get('executive_summary', 'No summary available.'))
        p = doc.add_paragraph(summary)
        
        # Comparison Table
        table_data = comp_data.get('comparison_table', {})
        if table_data.get('headers') and table_data.get('rows'):
            doc.add_heading('Comparison Matrix', level=1)
            headers = table_data['headers']
            rows = table_data['rows']
            
            table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
            table.style = 'Table Grid'
            
            # Header row
            for i, header in enumerate(headers):
                cell = table.rows[0].cells[i]
                cell.text = str(header)
                cell.paragraphs[0].runs[0].bold = True
            
            # Data rows
            for row_idx, row in enumerate(rows):
                for col_idx, cell_val in enumerate(row):
                    table.rows[row_idx + 1].cells[col_idx].text = str(cell_val)
            
            doc.add_paragraph()
        
        # Head to Head
        if comp_data.get('head_to_head'):
            doc.add_heading('Head-to-Head Analysis', level=1)
            for item in comp_data['head_to_head']:
                doc.add_heading(clean_text(item.get('area', 'Unknown')), level=2)
                doc.add_paragraph(f"Winner: {clean_text(item.get('winner', 'N/A'))}")
                doc.add_paragraph(clean_text(item.get('analysis', '')))
        
        # Final Ranking
        doc.add_heading('Final Ranking', level=1)
        for r in comp_data.get('final_ranking', []):
            rank = r.get('rank', '?')
            candidate = clean_text(r.get('candidate', 'Unknown'))
            reasoning = clean_text(r.get('reasoning', ''))
            
            h = doc.add_heading(f"#{rank} - {candidate}", level=2)
            doc.add_paragraph(reasoning)
        
        # Hiring Recommendation
        hr = comp_data.get('hiring_recommendation', {})
        doc.add_heading('Hiring Recommendation', level=1)
        
        p = doc.add_paragraph()
        p.add_run('Primary Choice: ').bold = True
        p.add_run(clean_text(hr.get('primary_choice', 'N/A')))
        
        doc.add_paragraph(clean_text(hr.get('primary_reasoning', '')))
        
        if hr.get('backup_choice') and hr.get('backup_choice') != 'None':
            p = doc.add_paragraph()
            p.add_run('Backup Choice: ').bold = True
            p.add_run(clean_text(hr.get('backup_choice', 'N/A')))
            doc.add_paragraph(clean_text(hr.get('backup_reasoning', '')))
        
        if hr.get('proceed_to_next_round'):
            p = doc.add_paragraph()
            p.add_run('Proceed to Next Round: ').bold = True
            p.add_run(', '.join(hr.get('proceed_to_next_round', [])))
        
        if hr.get('do_not_proceed'):
            p = doc.add_paragraph()
            p.add_run('Do Not Proceed: ').bold = True
            p.add_run(', '.join(hr.get('do_not_proceed', [])))
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        st.warning("📦 python-docx not installed. DOCX export unavailable.")
        return None
    except Exception as e:
        st.error(f"DOCX export error: {e}")
        return None

def export_comparison_to_pdf(comp_data, candidates):
    """Export comparison to PDF format."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, textColor=HexColor('#6366f1'), spaceAfter=20)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading1'], fontSize=16, textColor=HexColor('#374151'), spaceBefore=16, spaceAfter=8)
        subheading_style = ParagraphStyle('Subheading', parent=styles['Heading2'], fontSize=13, textColor=HexColor('#6366f1'), spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, textColor=HexColor('#4b5563'), spaceAfter=6)
        
        story = []
        
        # Title
        story.append(Paragraph("Candidate Comparison Report", title_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')} | Candidates: {len(candidates)}", body_style))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 12))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary = clean_text(comp_data.get('executive_summary', 'No summary available.'))
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 12))
        
        # Comparison Table
        table_data = comp_data.get('comparison_table', {})
        if table_data.get('headers') and table_data.get('rows'):
            story.append(Paragraph("Comparison Matrix", heading_style))
            
            headers = [clean_text(str(h)) for h in table_data['headers']]
            rows = [[clean_text(str(cell)) for cell in row] for row in table_data['rows']]
            
            all_data = [headers] + rows
            
            # Calculate column widths
            num_cols = len(headers)
            col_width = (7.5 * inch) / num_cols
            
            table = Table(all_data, colWidths=[col_width] * num_cols)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#374151')),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e5e7eb')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(table)
            story.append(Spacer(1, 12))
        
        # Final Ranking
        story.append(Paragraph("Final Ranking", heading_style))
        for r in comp_data.get('final_ranking', []):
            rank = r.get('rank', '?')
            candidate = clean_text(r.get('candidate', 'Unknown'))
            reasoning = clean_text(r.get('reasoning', ''))
            
            rank_color = '#10b981' if rank == 1 else '#eab308' if rank == 2 else '#6b7280'
            story.append(Paragraph(f"<b>#{rank} - {candidate}</b>", subheading_style))
            story.append(Paragraph(reasoning, body_style))
        
        # Hiring Recommendation
        hr = comp_data.get('hiring_recommendation', {})
        story.append(Paragraph("Hiring Recommendation", heading_style))
        story.append(Paragraph(f"<b>Primary Choice:</b> {clean_text(hr.get('primary_choice', 'N/A'))}", body_style))
        story.append(Paragraph(clean_text(hr.get('primary_reasoning', '')), body_style))
        
        if hr.get('backup_choice') and hr.get('backup_choice') != 'None':
            story.append(Paragraph(f"<b>Backup Choice:</b> {clean_text(hr.get('backup_choice', 'N/A'))}", body_style))
            story.append(Paragraph(clean_text(hr.get('backup_reasoning', '')), body_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        st.warning("📦 reportlab not installed. PDF export unavailable.")
        return None
    except Exception as e:
        st.error(f"PDF export error: {e}")
        return None

def export_to_docx(data, title="Evaluation"):
    """Export evaluation data to DOCX"""
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
            
            summary = data.get('overall_summary', '')
            if summary:
                # Clean summary text
                summary = ''.join(c if c.isprintable() or c in '\n\r\t' else ' ' for c in str(summary))
                doc.add_paragraph(summary)
            
            doc.add_heading("Strengths", level=1)
            for s in data.get('strengths', []):
                s_clean = ''.join(c if c.isprintable() else ' ' for c in str(s))
                doc.add_paragraph(s_clean, style='List Bullet')
            
            doc.add_heading("Concerns", level=1)
            for c in data.get('concerns', []):
                c_clean = ''.join(c if c.isprintable() else ' ' for c in str(c))
                doc.add_paragraph(c_clean, style='List Bullet')
            
            doc.add_heading("Focus Areas", level=1)
            for fa in data.get('focus_areas', []):
                area_name = ''.join(c if c.isprintable() else '' for c in str(fa.get('area', 'Unknown')))
                area_score = fa.get('score', 0)
                doc.add_heading(f"{area_name} - {area_score}/10", level=2)
                assessment = ''.join(c if c.isprintable() or c in '\n\r\t' else ' ' for c in str(fa.get('assessment', '')))
                doc.add_paragraph(assessment)
            
            # CV Verification
            cv_ver = data.get('cv_verification', {})
            if cv_ver:
                doc.add_heading("CV Verification", level=1)
                doc.add_paragraph(f"Trust Score: {cv_ver.get('trust_score', 0)}/10")
                
                if cv_ver.get('verified_claims'):
                    doc.add_paragraph("Verified Claims:")
                    for v in cv_ver.get('verified_claims', []):
                        v_clean = ''.join(c if c.isprintable() else ' ' for c in str(v))
                        doc.add_paragraph(v_clean, style='List Bullet')
            
            # Risk Assessment
            risk = data.get('risk_assessment', {})
            if risk:
                doc.add_heading("Risk Assessment", level=1)
                if risk.get('hiring_risk'):
                    doc.add_paragraph(f"Hiring Risk: {risk.get('hiring_risk')}")
                if risk.get('not_hiring_risk'):
                    doc.add_paragraph(f"Not Hiring Risk: {risk.get('not_hiring_risk')}")
            
            # Next Round Questions
            questions = data.get('questions_for_next_round', [])
            if questions:
                doc.add_heading("Suggested Questions for Next Round", level=1)
                for q in questions:
                    q_clean = ''.join(c if c.isprintable() else ' ' for c in str(q))
                    doc.add_paragraph(q_clean, style='List Bullet')
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        st.warning("📦 python-docx not installed. DOCX export unavailable.")
        return None
    except Exception as e:
        st.error(f"DOCX export error: {e}")
        return None

def export_to_pdf(data, title="Interview Evaluation"):
    """Export evaluation data to PDF using reportlab"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=24, textColor=HexColor('#6366f1'), spaceAfter=20)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading1'], fontSize=16, textColor=HexColor('#374151'), spaceBefore=16, spaceAfter=8)
        subheading_style = ParagraphStyle('CustomSubheading', parent=styles['Heading2'], fontSize=13, textColor=HexColor('#6366f1'), spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=10, textColor=HexColor('#4b5563'), spaceAfter=6)
        bullet_style = ParagraphStyle('CustomBullet', parent=styles['Normal'], fontSize=10, textColor=HexColor('#4b5563'), leftIndent=20, spaceAfter=4)
        
        story = []
        
        # Title
        story.append(Paragraph(title, title_style))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 12))
        
        if isinstance(data, dict):
            # Score and Recommendation
            score = data.get('overall_score', 0)
            rec = data.get('recommendation', 'N/A')
            score_color = '#10b981' if score >= 75 else '#eab308' if score >= 50 else '#ef4444'
            
            score_data = [
                ['Overall Score', 'Recommendation'],
                [f"{score}/100", rec]
            ]
            score_table = Table(score_data, colWidths=[2.5*inch, 4*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#374151')),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, 1), (0, 1), HexColor(score_color)),
                ('FONTSIZE', (0, 1), (-1, 1), 14),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e5e7eb')),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(score_table)
            story.append(Spacer(1, 12))
            
            # Summary
            summary = data.get('overall_summary', '')
            if summary:
                story.append(Paragraph(summary, body_style))
                story.append(Spacer(1, 12))
            
            # Strengths
            story.append(Paragraph("Strengths", heading_style))
            for s in data.get('strengths', []):
                s_clean = ''.join(c if c.isprintable() or c in '\n' else ' ' for c in str(s))
                story.append(Paragraph(f"• {s_clean}", bullet_style))
            
            # Concerns
            story.append(Paragraph("Concerns", heading_style))
            for c in data.get('concerns', []):
                c_clean = ''.join(c if c.isprintable() or c in '\n' else ' ' for c in str(c))
                story.append(Paragraph(f"• {c_clean}", bullet_style))
            
            # Focus Areas
            story.append(Paragraph("Focus Area Scores", heading_style))
            for fa in data.get('focus_areas', []):
                area_name = ''.join(c if c.isprintable() else '' for c in str(fa.get('area', 'Unknown')))
                area_score = fa.get('score', 0)
                story.append(Paragraph(f"{area_name} — {area_score}/10", subheading_style))
                assessment = ''.join(c if c.isprintable() or c in '\n' else ' ' for c in str(fa.get('assessment', '')))
                story.append(Paragraph(assessment, body_style))
            
            # CV Verification
            cv_ver = data.get('cv_verification', {})
            if cv_ver:
                story.append(Paragraph("CV Verification", heading_style))
                trust = cv_ver.get('trust_score', 0)
                story.append(Paragraph(f"Trust Score: {trust}/10", subheading_style))
                
                verified = cv_ver.get('verified_claims', [])
                if verified:
                    story.append(Paragraph("Verified Claims:", body_style))
                    for v in verified:
                        v_clean = ''.join(c if c.isprintable() else ' ' for c in str(v))
                        story.append(Paragraph(f"• {v_clean}", bullet_style))
                
                unverified = cv_ver.get('unverified_claims', [])
                if unverified:
                    story.append(Paragraph("Unverified Claims:", body_style))
                    for u in unverified:
                        u_clean = ''.join(c if c.isprintable() else ' ' for c in str(u))
                        story.append(Paragraph(f"• {u_clean}", bullet_style))
            
            # Risk Assessment
            risk = data.get('risk_assessment', {})
            if risk:
                story.append(Paragraph("Risk Assessment", heading_style))
                hire_risk = risk.get('hiring_risk', '')
                no_hire_risk = risk.get('not_hiring_risk', '')
                if hire_risk:
                    hire_risk_clean = ''.join(c if c.isprintable() or c in '\n' else ' ' for c in str(hire_risk))
                    story.append(Paragraph(f"<b>Hiring Risk:</b> {hire_risk_clean}", body_style))
                if no_hire_risk:
                    no_hire_clean = ''.join(c if c.isprintable() or c in '\n' else ' ' for c in str(no_hire_risk))
                    story.append(Paragraph(f"<b>Not Hiring Risk:</b> {no_hire_clean}", body_style))
            
            # Next Round Questions
            questions = data.get('questions_for_next_round', [])
            if questions:
                story.append(Paragraph("Suggested Questions for Next Round", heading_style))
                for q in questions:
                    q_clean = ''.join(c if c.isprintable() else ' ' for c in str(q))
                    story.append(Paragraph(f"• {q_clean}", bullet_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        st.warning("📦 reportlab not installed. PDF export unavailable.")
        return None
    except Exception as e:
        st.error(f"PDF export error: {e}")
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
    
    for idx, area in enumerate(result_data.get('focus_areas', [])):
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
        
        # Use custom accordion instead of st.expander to avoid Material Icon bug
        accordion_id = f"focus_area_{idx}"
        assessment = str(area.get('assessment', 'No assessment available'))
        assessment = ''.join(c if c.isprintable() or c in '\n' else ' ' for c in assessment)
        
        evidence_html = ""
        if area.get('evidence'):
            evidence_html = "<p style='color:#9ca3af;margin:12px 0 8px;font-weight:600;'>Evidence:</p>"
            for ev in area.get('evidence', []):
                ev_clean = ''.join(c if c.isprintable() or c in '\n' else ' ' for c in str(ev))
                evidence_html += f"<div style='background:#1a1a2e;border-left:3px solid #6366f1;padding:10px 14px;margin:6px 0;border-radius:0 8px 8px 0;font-style:italic;color:#a5b4fc;'>\"{ev_clean}\"</div>"
        
        st.markdown(f"""
        <details style="background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:10px;margin:8px 0;">
            <summary style="padding:14px 18px;cursor:pointer;display:flex;align-items:center;gap:12px;list-style:none;">
                <span style="color:{area_color};font-size:20px;">{'●' if area_score >= 6 else '○'}</span>
                <span style="color:#fff;font-weight:600;flex:1;">{area_name}</span>
                <span style="background:{area_color};color:#000;padding:4px 12px;border-radius:12px;font-weight:700;font-size:14px;">{area_score}/10</span>
            </summary>
            <div style="padding:0 18px 18px;border-top:1px solid rgba(99,102,241,0.1);">
                <p style="color:#e5e5e5;margin:12px 0;"><strong>Assessment:</strong> {assessment}</p>
                {evidence_html}
            </div>
        </details>
        """, unsafe_allow_html=True)
    
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
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
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

/* EXPANDER FIX - Hide broken Material Icon text */
.streamlit-expanderHeader { 
    background: #12121a !important; 
    border-radius: 10px !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    padding: 12px 16px !important;
}
.streamlit-expanderHeader:hover {
    border-color: rgba(99,102,241,0.5) !important;
}
/* Hide the broken icon text like keyboard_arrow_down */
.streamlit-expanderHeader svg { display: inline-block !important; }
.streamlit-expanderHeader span[data-testid="stMarkdownContainer"] p {
    display: inline !important;
}
/* Force hide any text that looks like icon names */
details summary span:not([data-testid]) {
    font-size: 0 !important;
}
details summary span:not([data-testid])::before {
    content: "▶";
    font-size: 14px;
    margin-right: 8px;
}
details[open] summary span:not([data-testid])::before {
    content: "▼";
}
/* Alternative: use CSS to replace with proper chevrons */
[data-testid="stExpander"] details summary div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    align-items: center !important;
}
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
        st.markdown("## 📊 Candidate Comparison Report")
        
        col_back, col_spacer = st.columns([1, 4])
        with col_back:
            if st.button("← Back to Results"):
                st.session_state.current_step = 'results'
                st.rerun()
        
        if st.session_state.comparison_result:
            try:
                txt = st.session_state.comparison_result
                m = re.search(r'```json\s*(.*?)\s*```', txt, re.DOTALL)
                comp = json.loads(m.group(1) if m else txt)
                
                # Executive Summary - prominent box
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15));border:1px solid rgba(99,102,241,0.3);border-radius:16px;padding:28px;margin:20px 0;">
                    <h3 style="margin:0 0 16px;color:#a5b4fc;font-size:14px;text-transform:uppercase;letter-spacing:1px;">📋 Executive Summary</h3>
                    <p style="color:#e5e5e5;margin:0;font-size:16px;line-height:1.6;">{comp.get('executive_summary', 'No summary available.')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Comparison Table
                table_data = comp.get('comparison_table', {})
                if table_data.get('headers') and table_data.get('rows'):
                    st.markdown("### 📈 Comparison Matrix")
                    
                    headers = table_data['headers']
                    rows = table_data['rows']
                    
                    # Build HTML table
                    table_html = '<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;background:#12121a;border-radius:12px;overflow:hidden;">'
                    
                    # Header row
                    table_html += '<tr>'
                    for h in headers:
                        table_html += f'<th style="background:#1a1a2e;padding:14px 16px;text-align:center;color:#a5b4fc;font-weight:600;border-bottom:1px solid rgba(99,102,241,0.2);">{h}</th>'
                    table_html += '</tr>'
                    
                    # Data rows
                    for row in rows:
                        table_html += '<tr>'
                        for i, cell in enumerate(row):
                            bg = 'background:#12121a;' if i > 0 else 'background:#1a1a2e;'
                            weight = 'font-weight:600;' if i == 0 else ''
                            table_html += f'<td style="{bg}padding:12px 16px;text-align:center;color:#e5e5e5;border-bottom:1px solid rgba(99,102,241,0.1);{weight}">{cell}</td>'
                        table_html += '</tr>'
                    
                    table_html += '</table></div>'
                    st.markdown(table_html, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Head to Head Analysis
                if comp.get('head_to_head'):
                    st.markdown("### ⚔️ Head-to-Head Analysis")
                    
                    cols = st.columns(min(3, len(comp['head_to_head'])))
                    for idx, item in enumerate(comp['head_to_head'][:6]):  # Max 6
                        with cols[idx % 3]:
                            st.markdown(f"""
                            <div style="background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:16px;margin:8px 0;min-height:120px;">
                                <p style="color:#9ca3af;margin:0 0 8px;font-size:12px;text-transform:uppercase;">{item.get('area', 'Area')}</p>
                                <p style="color:#10b981;margin:0 0 8px;font-weight:700;">🏆 {item.get('winner', 'N/A')}</p>
                                <p style="color:#e5e5e5;margin:0;font-size:13px;">{item.get('analysis', '')[:100]}{'...' if len(item.get('analysis', '')) > 100 else ''}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Final Ranking
                st.markdown("### 🏅 Final Ranking")
                
                for r in comp.get('final_ranking', []):
                    rank = r.get('rank', 0)
                    if rank == 1:
                        rank_color = "#10b981"
                        rank_bg = "rgba(16,185,129,0.1)"
                        medal = "🥇"
                    elif rank == 2:
                        rank_color = "#eab308"
                        rank_bg = "rgba(234,179,8,0.1)"
                        medal = "🥈"
                    elif rank == 3:
                        rank_color = "#f97316"
                        rank_bg = "rgba(249,115,22,0.1)"
                        medal = "🥉"
                    else:
                        rank_color = "#6b7280"
                        rank_bg = "rgba(107,114,128,0.1)"
                        medal = f"#{rank}"
                    
                    st.markdown(f"""
                    <div style="background:{rank_bg};border-left:4px solid {rank_color};padding:20px;margin:12px 0;border-radius:0 12px 12px 0;">
                        <div style="display:flex;align-items:center;gap:16px;margin-bottom:8px;">
                            <span style="font-size:32px;">{medal}</span>
                            <span style="color:#fff;font-size:20px;font-weight:700;">{r.get('candidate', 'Unknown')}</span>
                        </div>
                        <p style="color:#d1d5db;margin:0;font-size:14px;line-height:1.5;">{r.get('reasoning', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Hiring Recommendation
                hr = comp.get('hiring_recommendation', {})
                st.markdown("### ✅ Hiring Recommendation")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div style="background:rgba(16,185,129,0.1);border:1px solid #10b981;border-radius:12px;padding:20px;">
                        <p style="color:#9ca3af;margin:0 0 8px;font-size:12px;text-transform:uppercase;">Primary Choice</p>
                        <p style="color:#10b981;margin:0 0 12px;font-size:20px;font-weight:700;">{hr.get('primary_choice', 'N/A')}</p>
                        <p style="color:#e5e5e5;margin:0;font-size:14px;">{hr.get('primary_reasoning', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if hr.get('backup_choice') and hr.get('backup_choice') != 'None':
                        st.markdown(f"""
                        <div style="background:rgba(234,179,8,0.1);border:1px solid #eab308;border-radius:12px;padding:20px;">
                            <p style="color:#9ca3af;margin:0 0 8px;font-size:12px;text-transform:uppercase;">Backup Choice</p>
                            <p style="color:#eab308;margin:0 0 12px;font-size:20px;font-weight:700;">{hr.get('backup_choice', 'N/A')}</p>
                            <p style="color:#e5e5e5;margin:0;font-size:14px;">{hr.get('backup_reasoning', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background:rgba(107,114,128,0.1);border:1px solid #6b7280;border-radius:12px;padding:20px;">
                            <p style="color:#9ca3af;margin:0;font-size:14px;">No backup candidate recommended</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Proceed / Do Not Proceed
                if hr.get('proceed_to_next_round') or hr.get('do_not_proceed'):
                    st.markdown("")
                    col1, col2 = st.columns(2)
                    with col1:
                        if hr.get('proceed_to_next_round'):
                            st.success(f"**Proceed to Next Round:** {', '.join(hr.get('proceed_to_next_round', []))}")
                    with col2:
                        if hr.get('do_not_proceed'):
                            st.error(f"**Do Not Proceed:** {', '.join(hr.get('do_not_proceed', []))}")
                
                st.markdown("---")
                
                # Download Buttons
                st.markdown("### 📥 Export Comparison Report")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    md_content = export_comparison_to_markdown(comp, st.session_state.candidates)
                    st.download_button("📥 Markdown", md_content, "comparison_report.md", use_container_width=True)
                
                with col2:
                    docx_content = export_comparison_to_docx(comp, st.session_state.candidates)
                    if docx_content:
                        st.download_button("📥 DOCX", docx_content, "comparison_report.docx", 
                                          mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                          use_container_width=True)
                    else:
                        st.button("📥 DOCX", disabled=True, use_container_width=True, help="Export failed")
                
                with col3:
                    pdf_content = export_comparison_to_pdf(comp, st.session_state.candidates)
                    if pdf_content:
                        st.download_button("📥 PDF", pdf_content, "comparison_report.pdf",
                                          mime="application/pdf", use_container_width=True)
                    else:
                        st.button("📥 PDF", disabled=True, use_container_width=True, help="Export failed")
                
                with col4:
                    st.download_button("📥 JSON", json.dumps(comp, indent=2), "comparison_report.json", use_container_width=True)
                
            except Exception as e:
                st.error(f"Parse error: {e}")
                st.text(st.session_state.comparison_result)
    
    # RESULTS VIEW
    elif step == 'results' and st.session_state.current_candidate:
        result = st.session_state.current_candidate
        
        # Show evaluated candidates summary bar
        if len(st.session_state.candidates) > 0:
            st.markdown(f"""
            <div style="background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:16px;margin-bottom:20px;">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="color:#9ca3af;font-size:14px;">Candidates Evaluated:</span>
                        {' '.join([f'<span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;padding:4px 12px;border-radius:16px;font-size:13px;font-weight:600;">{c.get("candidate_name", "?")}</span>' for c in st.session_state.candidates])}
                    </div>
                    <span style="color:#6366f1;font-weight:600;">{len(st.session_state.candidates)}/4 candidates</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Start Fresh", use_container_width=True):
                st.session_state.current_step = 'input'
                st.session_state.current_candidate = None
                st.session_state.candidates = []
                st.session_state.comparison_result = None
                st.rerun()
        with col2:
            if len(st.session_state.candidates) < 4:
                if st.button(f"➕ Add Another Candidate", type="primary", use_container_width=True):
                    st.session_state.current_step = 'input'
                    st.session_state.current_candidate = None
                    st.rerun()
            else:
                st.button("✅ Max 4 Candidates", disabled=True, use_container_width=True)
        with col3:
            if len(st.session_state.candidates) >= 2:
                if st.button("📊 Compare All Candidates", use_container_width=True):
                    st.session_state.working_on = "Comparing candidates..."
                    comp_result, _ = compare_candidates(st.session_state.candidates)
                    st.session_state.working_on = None
                    st.session_state.comparison_result = comp_result
                    st.session_state.current_step = 'comparison'
                    st.rerun()
            else:
                st.button("📊 Compare (need 2+)", disabled=True, use_container_width=True)
        
        # Candidate selector if multiple candidates
        if len(st.session_state.candidates) > 1:
            st.markdown("---")
            selected_name = st.selectbox(
                "View Candidate:",
                [c.get('candidate_name', f'Candidate {i+1}') for i, c in enumerate(st.session_state.candidates)],
                index=[c.get('candidate_name') for c in st.session_state.candidates].index(result.get('candidate_name')) if result.get('candidate_name') in [c.get('candidate_name') for c in st.session_state.candidates] else 0,
                key="candidate_selector"
            )
            # Find and display selected candidate
            for c in st.session_state.candidates:
                if c.get('candidate_name') == selected_name:
                    result = c
                    break
        
        st.markdown("---")
        display_candidate_result(result, result.get('candidate_name', 'Candidate'))
        
        st.markdown("---")
        st.markdown("### 📥 Export This Evaluation")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            md_content = export_to_markdown(result, result.get('candidate_name', 'Evaluation'))
            st.download_button("📥 MD", md_content, f"{result.get('candidate_name', 'eval')}.md", use_container_width=True)
        with col2:
            docx_content = export_to_docx(result, result.get('candidate_name', 'Evaluation'))
            if docx_content:
                st.download_button("📥 DOCX", docx_content, f"{result.get('candidate_name', 'eval')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            else:
                st.button("📥 DOCX", disabled=True, use_container_width=True, help="DOCX export failed - check dependencies")
        with col3:
            pdf_content = export_to_pdf(result, result.get('candidate_name', 'Evaluation'))
            if pdf_content:
                st.download_button("📥 PDF", pdf_content, f"{result.get('candidate_name', 'eval')}.pdf", mime="application/pdf", use_container_width=True)
            else:
                st.button("📥 PDF", disabled=True, use_container_width=True, help="PDF export failed - check dependencies")
        with col4:
            st.download_button("📥 JSON", json.dumps(result, indent=2), f"{result.get('candidate_name', 'eval')}.json", use_container_width=True)
    
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
                        # Custom preview instead of st.expander
                        preview_text = transcript[:1500] + ("..." if len(transcript) > 1500 else "")
                        st.markdown(f"""
                        <details style="background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:8px;margin:8px 0;">
                            <summary style="padding:10px 14px;cursor:pointer;color:#9ca3af;font-size:14px;">▶ Preview transcript</summary>
                            <pre style="padding:12px;margin:0;color:#e5e5e5;font-size:12px;white-space:pre-wrap;max-height:300px;overflow:auto;">{preview_text}</pre>
                        </details>
                        """, unsafe_allow_html=True)
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
                    category = q.get('category', '')
                    time_est = q.get('time_estimate', '')
                    question = q.get('question', '')
                    look_for = q.get('what_to_look_for', '')
                    red_flags = q.get('red_flags', '')
                    
                    follow_ups_html = ""
                    if q.get('follow_ups'):
                        follow_ups_html = "<p style='color:#9ca3af;margin:10px 0 6px;font-weight:600;'>Follow-ups:</p><ul style='margin:0;padding-left:20px;'>"
                        for f in q.get('follow_ups', []):
                            follow_ups_html += f"<li style='color:#e5e5e5;margin:4px 0;'>{f}</li>"
                        follow_ups_html += "</ul>"
                    
                    st.markdown(f"""
                    <details style="background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:10px;margin:8px 0;">
                        <summary style="padding:14px 18px;cursor:pointer;display:flex;align-items:center;gap:8px;">
                            <span style="background:#6366f1;color:white;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;">Q{i}</span>
                            <span style="color:#fff;font-weight:600;flex:1;">{category}</span>
                            <span style="color:#9ca3af;font-size:13px;">⏱ {time_est} min</span>
                        </summary>
                        <div style="padding:0 18px 18px;border-top:1px solid rgba(99,102,241,0.1);">
                            <p style="color:#e5e5e5;margin:12px 0;"><strong style="color:#a5b4fc;">Question:</strong> {question}</p>
                            {follow_ups_html}
                            <p style="color:#e5e5e5;margin:10px 0;"><strong style="color:#10b981;">Look for:</strong> {look_for}</p>
                            <p style="color:#e5e5e5;margin:10px 0;"><strong style="color:#ef4444;">Red flags:</strong> {red_flags}</p>
                        </div>
                    </details>
                    """, unsafe_allow_html=True)
                
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
