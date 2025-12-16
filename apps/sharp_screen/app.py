"""Sharp Screen - AI CV Screening with Elite Features"""
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

# ============================================
# AUTH FUNCTIONS
# ============================================

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "screen",
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
        return {"success": True, "message": "Check email!"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def validate_session_token(token):
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
        ('user_plan', 'free'), ('working_on', None), ('screening_results', None),
        ('selected_candidates', []), ('comparison_result', None), ('parsed_data', None),
        ('anonymized_result', None), ('salary_result', None),
    ]
    for k, v in defaults:
        if k not in st.session_state:
            st.session_state[k] = v

def check_url_auth():
    token = st.query_params.get("token")
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
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except:
            try:
                import fitz
                pdf = fitz.open(stream=content, filetype="pdf")
                return "".join([page.get_text() for page in pdf])
            except:
                return "[PDF extraction failed]"
    elif file_type in ['docx', 'doc']:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return '\n'.join([p.text for p in doc.paragraphs])
        except:
            return "[DOCX extraction failed]"
    elif file_type == 'json':
        try:
            data = json.loads(content.decode('utf-8'))
            return json.dumps(data, indent=2)
        except:
            return content.decode('utf-8', errors='ignore')
    return content.decode('utf-8', errors='ignore')

def parse_json_candidates(json_str):
    try:
        data = json.loads(json_str)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            for key in ['candidates', 'applicants', 'data', 'results']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            return [data]
        return []
    except:
        return []

# ============================================
# AI FUNCTIONS
# ============================================

def call_claude(prompt, max_tokens=6000, action="screen"):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens,
                  "messages": [{"role": "user", "content": prompt}]}, timeout=180)
        if r.status_code == 200:
            data = r.json()
            text = data.get("content", [{}])[0].get("text", "")
            tokens = data.get("usage", {}).get("output_tokens", 0)
            user_id = st.session_state.user.get("id") if st.session_state.user else None
            if user_id:
                log_usage(user_id, st.session_state.session_token, "screen", action, tokens)
            return text, tokens
        return f"Error: {r.status_code} - {r.text}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0

def screen_candidates(jd_text, cvs_text, options):
    prompt = f"""Analyze candidates against this JD with DETAILED categorized skill breakdowns.

## JOB DESCRIPTION:
{jd_text}

## CANDIDATES (separated by ---):
{cvs_text}

## OPTIONS:
- Bias-Free Mode: {options.get('bias_free', True)}
- AI Detection: {options.get('ai_detection', True)}
- Salary Estimate: {options.get('salary_estimate', True)}

## OUTPUT (JSON):
```json
{{
    "screening_summary": {{
        "total_candidates": <number>,
        "recommended_for_interview": <number>,
        "maybe": <number>,
        "not_recommended": <number>,
        "time_saved_minutes": <number>,
        "bias_mitigation_score": <0-100>
    }},
    "candidates": [
        {{
            "rank": <number>,
            "identifier": "<name or Candidate A/B/C if bias-free>",
            "match_score": <0-100>,
            "skills_breakdown": {{
                "technical": {{"matched": <n>, "total": <n>, "details": ["skill1", "skill2"]}},
                "leadership": {{"matched": <n>, "total": <n>, "details": []}},
                "soft_skills": {{"matched": <n>, "total": <n>, "details": []}},
                "industry_experience": {{"matched": <n>, "total": <n>, "details": []}}
            }},
            "experience_years": <number>,
            "salary_alignment": "<Within Range | Above | Below | Unknown>",
            "why_this_score": "<2-3 sentences>",
            "strengths": ["<str1>", "<str2>"],
            "concerns": ["<concern1>"],
            "ai_written_probability": <0-100>,
            "recommended_action": "<Phone Screen | Technical Assessment | Panel Interview | Reject>",
            "rejection_reason": "<reason if rejected, else null>",
            "next_steps": "<specific next steps>",
            "hiring_manager_summary": "<3 bullet point summary for HM>"
        }}
    ],
    "batch_insights": {{
        "strongest_candidate_summary": "<summary>",
        "common_gaps": ["<gap1>"],
        "hiring_recommendation": "<overall recommendation>"
    }}
}}
```"""
    return call_claude(prompt, max_tokens=8000, action="screen_batch")

def compare_candidates(candidates_data):
    prompt = f"""Create a detailed side-by-side comparison of these candidates:

## CANDIDATES:
{json.dumps(candidates_data, indent=2)}

## OUTPUT (JSON):
```json
{{
    "comparison_table": {{
        "headers": ["Metric", "Candidate 1", "Candidate 2", "Candidate 3"],
        "rows": [
            ["Match Score", "<val>%", "<val>%", "<val>%"],
            ["Experience (Years)", "<val>", "<val>", "<val>"],
            ["Technical Skills", "<X/Y>", "<X/Y>", "<X/Y>"],
            ["Leadership", "<X/Y>", "<X/Y>", "<X/Y>"],
            ["Salary Alignment", "<status>", "<status>", "<status>"],
            ["AI Detection", "<val>%", "<val>%", "<val>%"],
            ["Top Strength", "<str>", "<str>", "<str>"],
            ["Top Concern", "<concern>", "<concern>", "<concern>"]
        ]
    }},
    "head_to_head": [
        {{"area": "Technical Skills", "winner": "Candidate 1", "analysis": "<why>"}},
        {{"area": "Experience", "winner": "Candidate 2", "analysis": "<why>"}},
        {{"area": "Culture Fit", "winner": "Candidate 1", "analysis": "<why>"}}
    ],
    "final_ranking": [
        {{"rank": 1, "candidate": "Candidate 1", "reasoning": "<why>"}},
        {{"rank": 2, "candidate": "Candidate 2", "reasoning": "<why>"}}
    ],
    "hiring_recommendation": {{
        "primary_choice": "Candidate 1",
        "primary_reasoning": "<detailed reasoning>",
        "backup_choice": "Candidate 2",
        "backup_reasoning": "<reasoning>",
        "interview_strategy": "<how to differentiate in interviews>"
    }},
    "executive_summary": "<3-4 sentence summary for hiring manager>"
}}
```"""
    return call_claude(prompt, max_tokens=4000, action="compare")

def anonymize_cv(resume_text, options):
    prompt = f"""Anonymize this resume for blind screening.

RESUME:
{resume_text}

OPTIONS:
- Time-based dates: {options.get('time_based', False)}

REMOVE/REPLACE:
- Names → [CANDIDATE]
- Email → [EMAIL REDACTED]
- Phone → [PHONE REDACTED]
- Address → [LOCATION REDACTED]
- Photos/Links → [REMOVED]
- University names → [UNIVERSITY A], [UNIVERSITY B]
- Company names → [COMPANY A], [COMPANY B]
{"- Convert dates to relative (e.g., '2020-2023' → '1-4 years ago')" if options.get('time_based') else ""}

OUTPUT (JSON):
```json
{{
    "anonymized_resume": "<full anonymized text>",
    "redactions_made": {{
        "names": <count>,
        "contact_info": <count>,
        "companies": <count>,
        "universities": <count>,
        "dates_converted": <count>
    }},
    "bias_indicators_removed": ["<indicator1>", "<indicator2>"]
}}
```"""
    return call_claude(prompt, max_tokens=4000, action="anonymize")

def estimate_salary(job_title, location, experience, industry, company_size, skills):
    prompt = f"""Estimate salary range for this role.

JOB TITLE: {job_title}
LOCATION: {location}
EXPERIENCE: {experience} years
INDUSTRY: {industry}
COMPANY SIZE: {company_size}
KEY SKILLS: {', '.join(skills) if skills else 'Not specified'}

Provide salary estimates in JSON:
```json
{{
    "salary_range": {{
        "low": <number>,
        "median": <number>,
        "high": <number>,
        "currency": "USD"
    }},
    "percentiles": {{
        "25th": <number>,
        "50th": <number>,
        "75th": <number>,
        "90th": <number>
    }},
    "factors": {{
        "location_adjustment": "<+X% or -X% and why>",
        "experience_premium": "<explanation>",
        "skill_premiums": ["<skill: +X%>"],
        "industry_factor": "<explanation>"
    }},
    "market_insights": "<2-3 sentences about current market>",
    "negotiation_tips": ["<tip1>", "<tip2>"]
}}
```"""
    return call_claude(prompt, max_tokens=2000, action="salary_estimate")

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_jd_history(limit=20):
    """Get JD history from Supabase - FIXED to work properly"""
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god":
        return []
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/jd_history",
            params={
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
                "limit": str(limit)
            },
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"
            },
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return data if data else []
        return []
    except Exception as e:
        return []

def save_screen_history(jd_id, jd_text, cvs_text, results, candidates_count, tokens):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god":
        return None
    try:
        payload = {
            "user_id": user_id,
            "jd_id": jd_id,
            "job_description": jd_text[:5000],
            "candidates_count": candidates_count,
            "results": results[:10000],
            "tokens_used": tokens
        }
        r = requests.post(f"{SUPABASE_URL}/rest/v1/screen_history",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=representation"},
            json=payload, timeout=10)
        return r.json()[0] if r.status_code in [200, 201] and r.json() else None
    except:
        return None

# ============================================
# EXPORT FUNCTIONS
# ============================================

def clean_text(text):
    if not text:
        return ""
    return ''.join(c if c.isprintable() or c in '\n\r\t' else ' ' for c in str(text))

def export_to_pdf(data, title="CV Screening Report"):
    """Export screening results to PDF"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=22, textColor=HexColor('#6366f1'), spaceAfter=12)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading1'], fontSize=14, textColor=HexColor('#374151'), spaceBefore=16, spaceAfter=8)
        subheading_style = ParagraphStyle('Subheading', parent=styles['Heading2'], fontSize=12, textColor=HexColor('#6366f1'), spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, textColor=HexColor('#4b5563'), spaceAfter=6)
        bullet_style = ParagraphStyle('Bullet', parent=body_style, leftIndent=20, spaceAfter=4)
        
        story = []
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", body_style))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e5e7eb')))
        story.append(Spacer(1, 12))
        
        # Summary
        summary = data.get('screening_summary', {})
        story.append(Paragraph("Executive Summary", heading_style))
        
        summary_data = [
            ['Total', 'Recommended', 'Maybe', 'Not Recommended', 'Time Saved'],
            [
                str(summary.get('total_candidates', '?')),
                str(summary.get('recommended_for_interview', '?')),
                str(summary.get('maybe', '?')),
                str(summary.get('not_recommended', '?')),
                f"~{summary.get('time_saved_minutes', '?')} min"
            ]
        ]
        
        t = Table(summary_data, colWidths=[1.3*inch]*5)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e5e7eb')),
        ]))
        story.append(t)
        story.append(Spacer(1, 16))
        
        # Candidates
        candidates = data.get('candidates', [])
        story.append(Paragraph("Candidate Rankings", heading_style))
        
        for c in candidates:
            score = c.get('match_score', 0)
            score_color = '#10b981' if score >= 70 else '#f59e0b' if score >= 50 else '#ef4444'
            
            story.append(Paragraph(f"#{c.get('rank', '?')} - {clean_text(c.get('identifier', 'Unknown'))} ({score}%)", subheading_style))
            story.append(Paragraph(f"<b>Action:</b> {c.get('recommended_action', 'N/A')}", body_style))
            story.append(Paragraph(f"<b>Experience:</b> {c.get('experience_years', '?')} years | <b>Salary:</b> {c.get('salary_alignment', 'Unknown')}", body_style))
            story.append(Paragraph(clean_text(c.get('why_this_score', '')), body_style))
            
            story.append(Paragraph("<b>Strengths:</b>", body_style))
            for s in c.get('strengths', [])[:3]:
                story.append(Paragraph(f"• {clean_text(s)}", bullet_style))
            
            if c.get('concerns'):
                story.append(Paragraph("<b>Concerns:</b>", body_style))
                for concern in c.get('concerns', [])[:2]:
                    story.append(Paragraph(f"• {clean_text(concern)}", bullet_style))
            
            story.append(Spacer(1, 8))
        
        # Batch Insights
        insights = data.get('batch_insights', {})
        if insights:
            story.append(Paragraph("Batch Insights", heading_style))
            story.append(Paragraph(f"<b>Top Candidate:</b> {clean_text(insights.get('strongest_candidate_summary', ''))}", body_style))
            story.append(Paragraph(f"<b>Common Gaps:</b> {', '.join(insights.get('common_gaps', []))}", body_style))
            story.append(Paragraph(f"<b>Recommendation:</b> {clean_text(insights.get('hiring_recommendation', ''))}", body_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        return None

def export_to_docx(data, title="CV Screening Report"):
    """Export screening results to DOCX"""
    try:
        from docx import Document
        from docx.shared import Pt, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        
        # Title
        title_para = doc.add_heading(title, 0)
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        
        # Summary
        summary = data.get('screening_summary', {})
        doc.add_heading('Executive Summary', level=1)
        
        table = doc.add_table(rows=2, cols=5)
        table.style = 'Table Grid'
        headers = ['Total', 'Recommended', 'Maybe', 'Not Recommended', 'Time Saved']
        values = [
            str(summary.get('total_candidates', '?')),
            str(summary.get('recommended_for_interview', '?')),
            str(summary.get('maybe', '?')),
            str(summary.get('not_recommended', '?')),
            f"~{summary.get('time_saved_minutes', '?')} min"
        ]
        
        for i, header in enumerate(headers):
            table.rows[0].cells[i].text = header
        for i, value in enumerate(values):
            table.rows[1].cells[i].text = value
        
        doc.add_paragraph()
        
        # Candidates
        doc.add_heading('Candidate Rankings', level=1)
        
        for c in data.get('candidates', []):
            score = c.get('match_score', 0)
            doc.add_heading(f"#{c.get('rank', '?')} - {c.get('identifier', 'Unknown')} ({score}%)", level=2)
            
            p = doc.add_paragraph()
            p.add_run(f"Recommended Action: ").bold = True
            p.add_run(c.get('recommended_action', 'N/A'))
            
            p = doc.add_paragraph()
            p.add_run(f"Experience: ").bold = True
            p.add_run(f"{c.get('experience_years', '?')} years")
            p.add_run(f" | Salary: ").bold = True
            p.add_run(c.get('salary_alignment', 'Unknown'))
            
            doc.add_paragraph(c.get('why_this_score', ''))
            
            doc.add_paragraph("Strengths:", style='List Bullet')
            for s in c.get('strengths', [])[:3]:
                doc.add_paragraph(s, style='List Bullet')
            
            if c.get('concerns'):
                doc.add_paragraph("Concerns:", style='List Bullet')
                for concern in c.get('concerns', [])[:2]:
                    doc.add_paragraph(concern, style='List Bullet')
        
        # Insights
        insights = data.get('batch_insights', {})
        if insights:
            doc.add_heading('Batch Insights', level=1)
            p = doc.add_paragraph()
            p.add_run("Top Candidate: ").bold = True
            p.add_run(insights.get('strongest_candidate_summary', ''))
            
            p = doc.add_paragraph()
            p.add_run("Common Gaps: ").bold = True
            p.add_run(', '.join(insights.get('common_gaps', [])))
            
            p = doc.add_paragraph()
            p.add_run("Recommendation: ").bold = True
            p.add_run(insights.get('hiring_recommendation', ''))
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        return None

def export_to_json_ats(data):
    """Export to ATS-compatible JSON format"""
    return json.dumps({
        "export_type": "cv_screening_results",
        "generated_at": datetime.now().isoformat(),
        "source": "Sharp Screen",
        "summary": data.get('screening_summary', {}),
        "candidates": [
            {
                "id": f"candidate_{c.get('rank', i)}",
                "name": c.get('identifier', f'Candidate {i}'),
                "match_score": c.get('match_score', 0),
                "recommendation": c.get('recommended_action', 'Review'),
                "experience_years": c.get('experience_years', 0),
                "skills_match": c.get('skills_breakdown', {}),
                "strengths": c.get('strengths', []),
                "concerns": c.get('concerns', []),
                "notes": c.get('why_this_score', ''),
                "salary_alignment": c.get('salary_alignment', 'Unknown')
            }
            for i, c in enumerate(data.get('candidates', []))
        ],
        "insights": data.get('batch_insights', {})
    }, indent=2)

def generate_hm_email(candidate, job_title=""):
    """Generate hiring manager summary email"""
    prompt = f"""Write a brief email to the hiring manager summarizing this candidate:

CANDIDATE: {json.dumps(candidate, indent=2)}
JOB TITLE: {job_title}

Write a 3-4 sentence professional email recommending next steps. Include:
- Quick summary of fit
- Key strengths
- Any concerns to probe in interview
- Recommended next step"""
    result, _ = call_claude(prompt, max_tokens=500, action="hm_email")
    return result

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp Screen", page_icon="🔍", layout="wide")
init_session()
check_url_auth()

# Auth check
if not st.session_state.authenticated:
    st.title("🔍 Sharp Screen")
    st.markdown("*AI-Powered CV Screening*")
    
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
    
    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", type="primary", use_container_width=True):
            if password == GOD_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.is_god = True
                st.session_state.user = {"email": "GOD", "id": "god"}
                st.session_state.user_plan = "god"
                st.rerun()
            elif email and password:
                result = supabase_sign_in(email, password)
                if result["success"]:
                    st.session_state.authenticated = True
                    st.session_state.user = result["user"]
                    st.session_state.session_token = result["session_token"]
                    st.rerun()
                else:
                    st.error(result["message"])
    
    with tab_signup:
        new_email = st.text_input("Email", key="signup_email")
        new_pass = st.text_input("Password", type="password", key="signup_pass")
        confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        if st.button("Create Account", type="primary", use_container_width=True):
            if new_pass != confirm:
                st.error("Passwords don't match")
            elif len(new_pass) < 6:
                st.error("Password must be 6+ characters")
            elif new_email and new_pass:
                result = supabase_sign_up(new_email, new_pass)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])
    
    st.stop()

# ============================================
# AUTHENTICATED UI
# ============================================

# Sidebar
with st.sidebar:
    st.image("https://sharphuman.com/logo1-3.png", width=50)
    st.markdown(f"**{get_user_email()}**")
    st.caption(f"{st.session_state.user_plan} plan")
    
    st.markdown("---")
    st.markdown("**Apps**")
    
    apps = [
        ("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"),
        ("interview", "🎯 Interview"), ("outreach", "🎣 Outreach"), ("content", "✍️ Content"),
        ("sales", "💰 Sales"),
    ]
    
    for key, label in apps:
        if key == "screen":
            st.button(f"{label} ◀", disabled=True, use_container_width=True)
        else:
            st.link_button(label, build_app_url(key), use_container_width=True)
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# Header
st.title("🔍 Sharp Screen")
st.caption("AI-Powered CV Screening")

# Tabs
tab_screen, tab_blind, tab_salary = st.tabs(["🔍 Screen & Rank", "👤 Blind Resume", "💰 Salary Estimator"])

# ============================================
# SCREEN & RANK TAB
# ============================================
with tab_screen:
    st.subheader("Job Description")
    jd_src = st.radio("Source:", ["📝 Paste", "📜 History", "📄 Upload"], horizontal=True, key="jd_src")
    
    jd_text = ""
    jd_id = None
    
    if jd_src == "📜 History":
        history = get_jd_history(20)
        if history and len(history) > 0:
            # Build options dict
            opts = {}
            for j in history:
                title = j.get('job_title', 'Untitled')
                date = j.get('created_at', '')[:10] if j.get('created_at') else ''
                key = f"{title} ({date})"
                opts[key] = j
            
            if opts:
                sel = st.selectbox("Select from your JD history:", list(opts.keys()))
                if sel and sel in opts:
                    selected_jd = opts[sel]
                    jd_text = selected_jd.get('generated_jd', '')
                    jd_id = selected_jd.get('id')
                    if jd_text:
                        st.success(f"✅ Loaded: {selected_jd.get('job_title', 'JD')}")
                        with st.expander("Preview JD"):
                            st.text(jd_text[:1000] + "..." if len(jd_text) > 1000 else jd_text)
                    else:
                        st.warning("Selected JD has no content")
            else:
                st.info("No JDs found in history")
        else:
            st.info("No saved JDs found. Create one in Sharp JD first!")
            jd_text = st.text_area("Or paste JD here:", height=120, key="jd_fallback")
    elif jd_src == "📄 Upload":
        f = st.file_uploader("Upload JD", type=['pdf', 'docx', 'txt'])
        if f:
            jd_text = extract_text_from_file(f)
            st.success(f"✅ Loaded {f.name}")
    else:
        jd_text = st.text_area("Paste Job Description:", height=150,
            placeholder="Paste the full job description here including:\n- Required qualifications & skills\n- Responsibilities\n- Experience level\n- Salary range (if available)")
    
    st.markdown("---")
    
    st.subheader("Candidate CVs")
    cv_src = st.radio("Source:", ["📝 Paste", "📁 Upload", "🔗 JSON/ATS"], horizontal=True, key="cv_src")
    
    cvs_text = ""
    if cv_src == "📁 Upload":
        files = st.file_uploader("Upload CVs", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
        if files:
            st.success(f"📎 {len(files)} files uploaded")
            cvs_text = "\n\n---\n\n".join([f"=== {f.name} ===\n{extract_text_from_file(f)}" for f in files])
    elif cv_src == "🔗 JSON/ATS":
        json_in = st.text_area("Paste JSON:", height=120)
        if json_in:
            cands = parse_json_candidates(json_in)
            if cands:
                st.success(f"✅ {len(cands)} candidates parsed")
                cvs_text = "\n\n---\n\n".join([json.dumps(c, indent=2) for c in cands])
    else:
        cvs_text = st.text_area("Paste CVs (separate with ---):", height=180,
            placeholder="Paste candidate resumes here, separated by ---\n\nExample:\nJohn Smith - Software Engineer\n5 years Python, AWS...\n\n---\n\nJane Doe - Backend Developer\n3 years Node.js, PostgreSQL...")
    
    st.markdown("---")
    
    st.subheader("Options")
    c1, c2, c3, c4 = st.columns(4)
    with c1: bias_free = st.checkbox("🔒 Bias-Free Mode", value=True)
    with c2: ai_detect = st.checkbox("🤖 AI Detection", value=True)
    with c3: salary_est = st.checkbox("💰 Salary Alignment", value=True)
    with c4: save_hist = st.checkbox("💾 Save Results", value=True)
    
    if st.button("🔍 Screen Candidates", type="primary", use_container_width=True):
        if not jd_text:
            st.warning("Please provide a job description")
        elif not cvs_text:
            st.warning("Please provide candidate CVs")
        else:
            with st.spinner("Analyzing candidates..."):
                result, tokens = screen_candidates(jd_text, cvs_text, {
                    'bias_free': bias_free, 'ai_detection': ai_detect, 'salary_estimate': salary_est
                })
                
                if not result.startswith("Error"):
                    st.session_state.screening_results = result
                    st.session_state.selected_candidates = []
                    if save_hist:
                        save_screen_history(jd_id, jd_text, cvs_text, result, cvs_text.count('---')+1, tokens)
                    st.rerun()
                else:
                    st.error(result)
    
    # Results Display
    if st.session_state.screening_results:
        st.markdown("---")
        
        try:
            match = re.search(r'```json\s*(.*?)\s*```', st.session_state.screening_results, re.DOTALL)
            data = json.loads(match.group(1) if match else st.session_state.screening_results)
            st.session_state.parsed_data = data
            
            summary = data.get('screening_summary', {})
            candidates = data.get('candidates', [])
            insights = data.get('batch_insights', {})
            
            # Summary metrics
            st.subheader("Results Summary")
            cols = st.columns(5)
            metrics = [
                ("Total", summary.get('total_candidates', '?')),
                ("Recommended", summary.get('recommended_for_interview', '?')),
                ("Maybe", summary.get('maybe', '?')),
                ("Not Recommended", summary.get('not_recommended', '?')),
                ("Time Saved", f"~{summary.get('time_saved_minutes', '?')} min"),
            ]
            for col, (label, val) in zip(cols, metrics):
                with col:
                    st.metric(label, val)
            
            # Export Options
            st.markdown("---")
            st.subheader("📥 Export Results")
            exp1, exp2, exp3, exp4 = st.columns(4)
            
            with exp1:
                pdf_data = export_to_pdf(data)
                if pdf_data:
                    st.download_button("📑 PDF Report", pdf_data, "screening_report.pdf", "application/pdf", use_container_width=True)
                else:
                    st.button("📑 PDF (unavailable)", disabled=True, use_container_width=True)
            
            with exp2:
                docx_data = export_to_docx(data)
                if docx_data:
                    st.download_button("📄 DOCX Report", docx_data, "screening_report.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                else:
                    st.button("📄 DOCX (unavailable)", disabled=True, use_container_width=True)
            
            with exp3:
                json_data = export_to_json_ats(data)
                st.download_button("🔗 JSON (ATS)", json_data, "screening_results.json", "application/json", use_container_width=True)
            
            with exp4:
                if st.button("📧 Email to HM", use_container_width=True):
                    if candidates:
                        top_candidate = candidates[0]
                        email = generate_hm_email(top_candidate)
                        st.session_state.hm_email = email
            
            if st.session_state.get('hm_email'):
                st.text_area("Hiring Manager Email", st.session_state.hm_email, height=150)
                st.download_button("📋 Copy Email", st.session_state.hm_email, "hm_email.txt")
            
            # Filters
            st.markdown("---")
            st.subheader("Filter & Compare")
            f1, f2, f3, f4 = st.columns(4)
            with f1: min_score = st.slider("Min Score", 0, 100, 0)
            with f2: filter_action = st.selectbox("Action", ["All", "Phone Screen", "Technical Assessment", "Panel Interview", "Reject"])
            with f3: sort_by = st.selectbox("Sort", ["Rank", "Score", "Experience"])
            with f4: compare_mode = st.checkbox("Compare Mode")
            
            # Filter candidates
            filtered = [c for c in candidates if c.get('match_score', 0) >= min_score]
            if filter_action != "All":
                filtered = [c for c in filtered if filter_action.lower() in c.get('recommended_action', '').lower()]
            
            if sort_by == "Score":
                filtered = sorted(filtered, key=lambda x: x.get('match_score', 0), reverse=True)
            elif sort_by == "Experience":
                filtered = sorted(filtered, key=lambda x: x.get('experience_years', 0), reverse=True)
            
            # Compare functionality
            if compare_mode:
                selected = st.multiselect("Select candidates to compare:",
                    [c.get('identifier', f"Candidate {i}") for i, c in enumerate(filtered)],
                    key="compare_select")
                
                if len(selected) >= 2:
                    if st.button(f"📊 Compare {len(selected)} Candidates", type="primary"):
                        with st.spinner("Comparing..."):
                            selected_data = [c for c in filtered if c.get('identifier') in selected]
                            result, _ = compare_candidates(selected_data)
                            st.session_state.comparison_result = result
                            st.rerun()
            
            # Show comparison results
            if st.session_state.get('comparison_result'):
                st.markdown("---")
                st.subheader("📊 Comparison Results")
                
                try:
                    comp_match = re.search(r'```json\s*(.*?)\s*```', st.session_state.comparison_result, re.DOTALL)
                    comp_data = json.loads(comp_match.group(1) if comp_match else st.session_state.comparison_result)
                    
                    # Executive Summary
                    st.info(comp_data.get('executive_summary', ''))
                    
                    # Comparison Table
                    table = comp_data.get('comparison_table', {})
                    if table.get('headers') and table.get('rows'):
                        import pandas as pd
                        df = pd.DataFrame(table['rows'], columns=table['headers'])
                        st.dataframe(df, use_container_width=True)
                    
                    # Hiring Recommendation
                    hr = comp_data.get('hiring_recommendation', {})
                    if hr:
                        st.success(f"**Primary Choice:** {hr.get('primary_choice', 'N/A')} - {hr.get('primary_reasoning', '')}")
                        if hr.get('backup_choice'):
                            st.info(f"**Backup:** {hr.get('backup_choice', 'N/A')} - {hr.get('backup_reasoning', '')}")
                    
                    # Export comparison
                    st.download_button("📥 Download Comparison", json.dumps(comp_data, indent=2), "comparison.json")
                    
                except Exception as e:
                    st.error(f"Error parsing comparison: {e}")
                
                if st.button("🔄 Clear Comparison"):
                    st.session_state.comparison_result = None
                    st.rerun()
            
            # Candidate Cards
            st.markdown("---")
            st.subheader(f"Candidates ({len(filtered)})")
            
            for c in filtered:
                score = c.get('match_score', 0)
                score_color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                
                with st.expander(f"{score_color} #{c.get('rank', '?')} - {c.get('identifier', 'Unknown')} ({score}%) - {c.get('recommended_action', 'Review')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Why this score:** {c.get('why_this_score', '')}")
                        
                        st.markdown("**Strengths:**")
                        for s in c.get('strengths', []):
                            st.markdown(f"- ✅ {s}")
                        
                        if c.get('concerns'):
                            st.markdown("**Concerns:**")
                            for concern in c.get('concerns', []):
                                st.markdown(f"- ⚠️ {concern}")
                    
                    with col2:
                        st.metric("Experience", f"{c.get('experience_years', '?')} years")
                        st.metric("Salary", c.get('salary_alignment', 'Unknown'))
                        if ai_detect:
                            st.metric("AI Written", f"{c.get('ai_written_probability', '?')}%")
                    
                    # Skills breakdown
                    skills = c.get('skills_breakdown', {})
                    if skills:
                        st.markdown("**Skills Breakdown:**")
                        skill_cols = st.columns(4)
                        for i, (skill_type, skill_data) in enumerate(skills.items()):
                            with skill_cols[i % 4]:
                                if isinstance(skill_data, dict):
                                    matched = skill_data.get('matched', 0)
                                    total = skill_data.get('total', 0)
                                    st.metric(skill_type.replace('_', ' ').title(), f"{matched}/{total}")
                    
                    # Actions
                    st.markdown("---")
                    act1, act2, act3 = st.columns(3)
                    with act1:
                        if st.button("📧 Generate Email", key=f"email_{c.get('rank')}"):
                            email = generate_hm_email(c)
                            st.text_area("Email", email, key=f"email_text_{c.get('rank')}")
                    with act2:
                        if st.button("➡️ Send to Interview", key=f"interview_{c.get('rank')}"):
                            st.markdown(f"[Open Interview App →]({build_app_url('interview')})")
                    with act3:
                        st.download_button("📥 Export", json.dumps(c, indent=2), f"{c.get('identifier', 'candidate')}.json", key=f"export_{c.get('rank')}")
            
            # Batch Insights
            if insights:
                st.markdown("---")
                st.subheader("💡 Batch Insights")
                st.info(f"**🏆 Top Candidate:** {insights.get('strongest_candidate_summary', '')}")
                st.warning(f"**📋 Common Gaps:** {', '.join(insights.get('common_gaps', []))}")
                st.success(f"**✅ Recommendation:** {insights.get('hiring_recommendation', '')}")
            
            # Clear results
            if st.button("🔄 New Screening"):
                st.session_state.screening_results = None
                st.session_state.parsed_data = None
                st.session_state.comparison_result = None
                st.session_state.hm_email = None
                st.rerun()
        
        except Exception as e:
            st.error(f"Error parsing results: {e}")
            st.text_area("Raw Results", st.session_state.screening_results, height=300)

# ============================================
# BLIND RESUME TAB
# ============================================
with tab_blind:
    st.subheader("Blind Resume Anonymization")
    st.caption("Remove identifying information for unbiased screening")
    
    src = st.radio("Source:", ["📝 Paste", "📄 Upload"], horizontal=True, key="anon_src")
    
    if src == "📄 Upload":
        f = st.file_uploader("Upload CV", type=['pdf', 'docx', 'txt'], key="anon_file")
        resume = extract_text_from_file(f) if f else ""
    else:
        resume = st.text_area("Paste resume:", height=250, placeholder="Paste the full resume text here...")
    
    time_based = st.checkbox("⏱️ Convert dates to relative time (e.g., '2 years ago')")
    
    if st.button("👤 Anonymize Resume", type="primary", use_container_width=True):
        if resume:
            with st.spinner("Anonymizing..."):
                result, _ = anonymize_cv(resume, {'time_based': time_based})
                
                if not result.startswith("Error"):
                    st.session_state.anonymized_result = result
                    st.rerun()
                else:
                    st.error(result)
        else:
            st.warning("Please provide a resume")
    
    if st.session_state.get('anonymized_result'):
        st.markdown("---")
        
        try:
            match = re.search(r'```json\s*(.*?)\s*```', st.session_state.anonymized_result, re.DOTALL)
            data = json.loads(match.group(1) if match else st.session_state.anonymized_result)
            
            st.subheader("✅ Anonymized Resume")
            st.text_area("Result:", data.get('anonymized_resume', ''), height=300)
            
            # Redaction stats
            redactions = data.get('redactions_made', {})
            if redactions:
                st.subheader("📊 Redaction Summary")
                cols = st.columns(5)
                for i, (key, val) in enumerate(redactions.items()):
                    with cols[i % 5]:
                        st.metric(key.replace('_', ' ').title(), val)
            
            # Export
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📥 Download Anonymized", data.get('anonymized_resume', ''), "anonymized_resume.txt", use_container_width=True)
            with c2:
                if st.button("🔄 Clear", use_container_width=True):
                    st.session_state.anonymized_result = None
                    st.rerun()
        
        except Exception as e:
            st.error(f"Error: {e}")
            st.text(st.session_state.anonymized_result)

# ============================================
# SALARY ESTIMATOR TAB
# ============================================
with tab_salary:
    st.subheader("Salary Estimator")
    st.caption("Get market-based salary estimates")
    
    c1, c2 = st.columns(2)
    with c1:
        sal_title = st.text_input("Job Title", placeholder="e.g., Senior Software Engineer")
        sal_location = st.text_input("Location", placeholder="e.g., San Francisco, CA")
        sal_experience = st.slider("Years of Experience", 0, 30, 5)
    
    with c2:
        sal_industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Consulting", "Other"])
        sal_company_size = st.selectbox("Company Size", ["Startup (1-50)", "Small (51-200)", "Mid-size (201-1000)", "Large (1001-5000)", "Enterprise (5000+)"])
        sal_skills = st.text_input("Key Skills (comma-separated)", placeholder="Python, AWS, Machine Learning")
    
    if st.button("💰 Estimate Salary", type="primary", use_container_width=True):
        if sal_title:
            with st.spinner("Analyzing market data..."):
                skills_list = [s.strip() for s in sal_skills.split(',')] if sal_skills else []
                result, _ = estimate_salary(sal_title, sal_location, sal_experience, sal_industry, sal_company_size, skills_list)
                
                if not result.startswith("Error"):
                    st.session_state.salary_result = result
                    st.rerun()
                else:
                    st.error(result)
        else:
            st.warning("Please enter a job title")
    
    if st.session_state.get('salary_result'):
        st.markdown("---")
        
        try:
            match = re.search(r'```json\s*(.*?)\s*```', st.session_state.salary_result, re.DOTALL)
            data = json.loads(match.group(1) if match else st.session_state.salary_result)
            
            st.subheader("💰 Salary Estimate")
            
            # Main range
            sal_range = data.get('salary_range', {})
            cols = st.columns(3)
            with cols[0]:
                st.metric("Low", f"${sal_range.get('low', 0):,}")
            with cols[1]:
                st.metric("Median", f"${sal_range.get('median', 0):,}")
            with cols[2]:
                st.metric("High", f"${sal_range.get('high', 0):,}")
            
            # Percentiles
            percentiles = data.get('percentiles', {})
            if percentiles:
                st.subheader("📊 Percentile Distribution")
                perc_cols = st.columns(4)
                for i, (perc, val) in enumerate(percentiles.items()):
                    with perc_cols[i]:
                        st.metric(perc, f"${val:,}")
            
            # Factors
            factors = data.get('factors', {})
            if factors:
                st.subheader("📈 Adjustment Factors")
                for key, val in factors.items():
                    if val:
                        st.markdown(f"- **{key.replace('_', ' ').title()}:** {val}")
            
            # Insights
            if data.get('market_insights'):
                st.subheader("💡 Market Insights")
                st.info(data.get('market_insights', ''))
            
            if data.get('negotiation_tips'):
                st.subheader("🎯 Negotiation Tips")
                for tip in data.get('negotiation_tips', []):
                    st.markdown(f"- {tip}")
            
            # Export
            st.download_button("📥 Download Report", json.dumps(data, indent=2), "salary_estimate.json")
            
            if st.button("🔄 New Estimate"):
                st.session_state.salary_result = None
                st.rerun()
        
        except Exception as e:
            st.error(f"Error: {e}")
            st.text(st.session_state.salary_result)
