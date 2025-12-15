"""Sharp Screen - Advanced CV Screening with Cross-App Auth"""
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
        ('user_plan', 'free'), ('screening_results', None), ('working_on', None),
        ('anonymized_result', None), ('selected_candidates', []), ('candidate_statuses', {}),
        ('comparison_result', None), ('feedback_open', False), ('feedback_sent', False),
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

def get_jd_history(limit=50):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god": return []
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/jd_history?user_id=eq.{user_id}&order=created_at.desc&limit={limit}",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        return r.json() if r.status_code == 200 else []
    except: return []

def save_screen_history(jd_id, jd_text, candidates_input, result, candidates_count, tokens_used):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god": return None
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/screen_history",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=representation"},
            json={"user_id": user_id, "jd_history_id": jd_id, "job_description": jd_text[:5000] if jd_text else None,
                  "candidates_input": candidates_input[:5000] if candidates_input else None, "screening_result": result,
                  "candidates_count": candidates_count, "tokens_used": tokens_used}, timeout=10)
        return r.json()[0] if r.status_code in [200, 201] and r.json() else None
    except: return None

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
            if isinstance(data, list):
                return '\n---\n'.join([json.dumps(item, indent=2) for item in data])
            return json.dumps(data, indent=2)
        except:
            return content.decode('utf-8', errors='ignore')
    return content.decode('utf-8', errors='ignore')

def parse_json_candidates(json_text):
    try:
        data = json.loads(json_text)
        candidates = []
        items = data if isinstance(data, list) else data.get('candidates', [data])
        for item in items:
            candidates.append({
                'name': item.get('name') or item.get('candidateName') or item.get('full_name', 'Unknown'),
                'email': item.get('email') or item.get('emailAddress', ''),
                'skills': item.get('skills') or item.get('skillSet', []),
                'summary': item.get('summary') or item.get('professionalSummary', ''),
            })
        return candidates
    except:
        return None

# ============================================
# CLAUDE API
# ============================================

def call_claude(prompt, max_tokens=4000, action="screen"):
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
                log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "screen", action, tokens)
            return text, tokens
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0

# ============================================
# SCREENING FUNCTIONS
# ============================================

def screen_candidates(jd_text, cvs_text, options):
    prompt = f"""You are an expert technical recruiter. Analyze candidates against this JD with DETAILED categorized skill breakdowns.

## JOB DESCRIPTION:
{jd_text}

## CANDIDATES (separated by ---):
{cvs_text}

## OPTIONS:
- Bias-Free Mode: {options.get('bias_free', True)}
- AI Detection: {options.get('ai_detection', True)}
- Salary Estimate: {options.get('salary_estimate', True)}

## OUTPUT (JSON) - Include categorized skills breakdown:
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
            "identifier": "<name or Candidate A/B/C>",
            "match_score": <0-100>,
            "skills_breakdown": {{
                "technical": {{"matched": <n>, "total": <n>, "details": ["skill1"]}},
                "leadership": {{"matched": <n>, "total": <n>, "details": []}},
                "soft_skills": {{"matched": <n>, "total": <n>, "details": []}},
                "industry_experience": {{"matched": <n>, "total": <n>, "details": []}}
            }},
            "required_skills_match": "<X/Y>",
            "preferred_skills_match": "<X/Y>",
            "experience_years": <number>,
            "salary_alignment": "<Within Range | Above | Below | Unknown>",
            "why_this_score": "<2-3 sentences>",
            "strengths": ["<str1>", "<str2>"],
            "concerns": ["<concern1>"],
            "ai_written_probability": <0-100>,
            "recommended_action": "<Phone Screen | Assessment | Reject>",
            "rejection_reason": "<reason if rejected>",
            "next_steps": "<steps>",
            "hiring_manager_summary": "<3 bullet points>"
        }}
    ],
    "batch_insights": {{
        "strongest_candidate_summary": "<summary>",
        "common_gaps": ["<gap1>"],
        "hiring_recommendation": "<recommendation>"
    }}
}}
```"""
    return call_claude(prompt, max_tokens=6000, action="screen_batch")

def compare_candidates(candidates_data, jd_summary=""):
    prompt = f"""Create a side-by-side comparison:

## CANDIDATES:
{json.dumps(candidates_data, indent=2)}

## OUTPUT (JSON):
```json
{{
    "comparison_table": {{
        "headers": ["Metric", "Candidate 1", "Candidate 2", "Candidate 3"],
        "rows": [
            ["Experience", "<val>", "<val>", "<val>"],
            ["Match Score", "<val>%", "<val>%", "<val>%"],
            ["Technical", "<X/Y>", "<X/Y>", "<X/Y>"],
            ["Leadership", "<X/Y>", "<X/Y>", "<X/Y>"],
            ["Salary", "<status>", "<status>", "<status>"],
            ["AI Score", "<val>%", "<val>%", "<val>%"]
        ]
    }},
    "winner_recommendation": "<which and why>",
    "interview_strategy": "<how to differentiate>"
}}
```"""
    return call_claude(prompt, max_tokens=2000, action="compare")

def generate_email_template(candidate, template_type, job_title=""):
    templates = {
        "phone_screen": f"Draft phone screen invite for {candidate.get('identifier')} for {job_title}. Include: personalized line about their strengths ({', '.join(candidate.get('strengths', [])[:2])}), request for 20-30 min call, [CALENDAR_LINK] placeholder.",
        "skills_test": f"Draft skills assessment email for {candidate.get('identifier')}. Areas to validate: {', '.join(candidate.get('concerns', [])[:2])}. Professional, encouraging tone.",
        "rejection": f"Draft GDPR-compliant rejection for {candidate.get('identifier')}. Reason: {candidate.get('rejection_reason', 'skills mismatch')}. Kind, professional.",
        "linkedin": f"Draft SHORT LinkedIn message (<300 chars) for {candidate.get('identifier')}. Reference: {candidate.get('strengths', ['experience'])[0]}."
    }
    return call_claude(templates.get(template_type, templates["phone_screen"]), max_tokens=800, action=f"email_{template_type}")

def generate_hiring_manager_summary(candidates_data, bias_free=True):
    prompt = f"""Generate Hiring Manager briefing:

## CANDIDATES:
{json.dumps(candidates_data, indent=2)}

{"Remove all PII" if bias_free else "Include names"}

## OUTPUT (JSON):
```json
{{
    "executive_summary": "<1-2 sentences>",
    "candidates": [
        {{
            "identifier": "<name>",
            "fit": "<bullet>",
            "gaps": "<bullet>",
            "action": "<bullet>"
        }}
    ],
    "overall_recommendation": "<prioritize who>"
}}
```"""
    return call_claude(prompt, max_tokens=2000, action="hm_summary")

def anonymize_cv(cv_text, options):
    prompt = f"""Anonymize this CV:

{cv_text}

{"Convert dates to relative time" if options.get('time_based') else "Keep dates"}
Replace universities with tiers, companies with descriptors.

## OUTPUT (JSON):
```json
{{
    "anonymized_cv": "<text>",
    "items_removed": {{"names": [], "emails": [], "phones": [], "universities": [], "companies": []}},
    "anonymization_score": <0-100>
}}
```"""
    return call_claude(prompt, max_tokens=3000, action="anonymize")

def estimate_salary(cv_text, jd_text, location):
    prompt = f"""Estimate salary:

JOB: {jd_text[:2000]}
CV: {cv_text[:3000]}
LOCATION: {location}

## OUTPUT (JSON):
```json
{{
    "estimated_range": {{"low": <num>, "mid": <num>, "high": <num>}},
    "confidence": "<Low|Medium|High>",
    "factors_increasing": ["<factor>"],
    "factors_decreasing": ["<factor>"],
    "market_context": "<note>"
}}
```"""
    return call_claude(prompt, max_tokens=1500, action="salary")

# ============================================
# PDF GENERATION
# ============================================

def generate_pdf_report(data, title=""):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        summary = data.get('screening_summary', {})
        candidates = data.get('candidates', [])
        insights = data.get('batch_insights', {})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CV Screening Report</title>
    <style>
        @page {{ margin: 0.75in; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #1f2937; max-width: 8.5in; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; margin: -20px -20px 30px -20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24pt; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
        .summary-card {{ background: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card .number {{ font-size: 28pt; font-weight: bold; color: #6366f1; }}
        .summary-card .label {{ font-size: 10pt; color: #6b7280; text-transform: uppercase; }}
        .candidate {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; margin-bottom: 20px; page-break-inside: avoid; }}
        .candidate-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #e5e7eb; }}
        .candidate-rank {{ background: #6366f1; color: white; padding: 6px 16px; border-radius: 20px; font-weight: bold; }}
        .score {{ font-size: 24pt; font-weight: bold; }}
        .score-high {{ color: #10b981; }}
        .score-med {{ color: #f59e0b; }}
        .score-low {{ color: #ef4444; }}
        .skills-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0; }}
        .skill-box {{ background: #f9fafb; padding: 12px; border-radius: 6px; text-align: center; }}
        .skill-box .name {{ font-size: 9pt; color: #6b7280; text-transform: uppercase; }}
        .skill-box .value {{ font-size: 14pt; font-weight: bold; color: #1f2937; }}
        .tag {{ display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 9pt; margin: 2px; }}
        .tag-green {{ background: #d1fae5; color: #059669; }}
        .tag-red {{ background: #fee2e2; color: #dc2626; }}
        .recommendation {{ background: #eff6ff; border-left: 4px solid #6366f1; padding: 16px; margin: 16px 0; }}
        .insights {{ background: #fef3c7; border-radius: 12px; padding: 24px; margin-top: 30px; }}
        .insights h3 {{ color: #92400e; margin-top: 0; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #9ca3af; font-size: 9pt; }}
        @media print {{ body {{ padding: 0; }} .header {{ margin: 0 0 30px 0; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CV Screening Report</h1>
        <p>{title} | {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
    
    <div class="summary-grid">
        <div class="summary-card"><div class="number">{summary.get('total_candidates', '?')}</div><div class="label">Candidates</div></div>
        <div class="summary-card"><div class="number" style="color:#10b981">{summary.get('recommended_for_interview', '?')}</div><div class="label">Recommended</div></div>
        <div class="summary-card"><div class="number" style="color:#f59e0b">{summary.get('maybe', '?')}</div><div class="label">Maybe</div></div>
        <div class="summary-card"><div class="number">~{summary.get('time_saved_minutes', '?')}m</div><div class="label">Time Saved</div></div>
    </div>
    
    <h2>Candidate Rankings</h2>
"""
        
        for c in candidates:
            score = c.get('match_score', 0)
            sc = "score-high" if score >= 70 else "score-med" if score >= 50 else "score-low"
            skills = c.get('skills_breakdown', {})
            
            html += f"""
    <div class="candidate">
        <div class="candidate-header">
            <div><span class="candidate-rank">#{c.get('rank', '?')}</span> <strong style="font-size:14pt;margin-left:12px;">{c.get('identifier', 'Unknown')}</strong></div>
            <span class="score {sc}">{score}%</span>
        </div>
        <div class="skills-grid">
            <div class="skill-box"><div class="name">Technical</div><div class="value">{skills.get('technical', {}).get('matched', '?')}/{skills.get('technical', {}).get('total', '?')}</div></div>
            <div class="skill-box"><div class="name">Leadership</div><div class="value">{skills.get('leadership', {}).get('matched', '?')}/{skills.get('leadership', {}).get('total', '?')}</div></div>
            <div class="skill-box"><div class="name">Soft Skills</div><div class="value">{skills.get('soft_skills', {}).get('matched', '?')}/{skills.get('soft_skills', {}).get('total', '?')}</div></div>
            <div class="skill-box"><div class="name">Experience</div><div class="value">{c.get('experience_years', '?')} yrs</div></div>
        </div>
        <p><strong>Assessment:</strong> {c.get('why_this_score', '')}</p>
        <p><strong>Strengths:</strong> {''.join([f'<span class="tag tag-green">{s}</span>' for s in c.get('strengths', [])])}</p>
        <p><strong>Concerns:</strong> {''.join([f'<span class="tag tag-red">{s}</span>' for s in c.get('concerns', [])])}</p>
        <div class="recommendation"><strong>Recommendation:</strong> {c.get('recommended_action', '')} | <strong>Next:</strong> {c.get('next_steps', '')}</div>
    </div>
"""
        
        html += f"""
    <div class="insights">
        <h3>Batch Insights</h3>
        <p><strong>Top Candidate:</strong> {insights.get('strongest_candidate_summary', '')}</p>
        <p><strong>Common Gaps:</strong> {', '.join(insights.get('common_gaps', []))}</p>
        <p><strong>Recommendation:</strong> {insights.get('hiring_recommendation', '')}</p>
    </div>
    <div class="footer">Generated by Sharp Screen | Sharp Human AI Suite</div>
</body>
</html>"""
        return html
    except Exception as e:
        return f"<html><body>Error: {e}</body></html>"

def generate_csv_report(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        candidates = data.get('candidates', [])
        lines = ["Rank,Identifier,Score,Technical,Leadership,Soft Skills,Experience,Salary,AI Score,Action"]
        for c in candidates:
            sk = c.get('skills_breakdown', {})
            lines.append(f"{c.get('rank','')},{c.get('identifier','')},{c.get('match_score','')},{sk.get('technical',{}).get('matched','?')}/{sk.get('technical',{}).get('total','?')},{sk.get('leadership',{}).get('matched','?')}/{sk.get('leadership',{}).get('total','?')},{sk.get('soft_skills',{}).get('matched','?')}/{sk.get('soft_skills',{}).get('total','?')},{c.get('experience_years','')},{c.get('salary_alignment','')},{c.get('ai_written_probability','')},{c.get('recommended_action','')}")
        return '\n'.join(lines)
    except:
        return "Error"

# ============================================
# MAIN APP CONFIG
# ============================================

st.set_page_config(page_title="Sharp Screen", page_icon="🔍", layout="wide")
init_session()
check_url_auth()

# COMPREHENSIVE STYLES - Fixed all icon issues
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

/* Base reset */
*, *::before, *::after { font-family: 'Nunito', sans-serif !important; box-sizing: border-box; }

/* App background */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stApp"] { background: #0a0a0f !important; }
[data-testid="stHeader"] { background: transparent !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0d0d14 !important; border-right: 1px solid rgba(99,102,241,0.2); }
section[data-testid="stSidebar"] > div { background: #0d0d14 !important; }
section[data-testid="stSidebar"] * { color: #e5e5e5 !important; }

/* CRITICAL: Hide ALL Material Icons text */
[data-testid="stSidebar"] span[class*="material"],
[class*="material-icons"],
[class*="material-symbols"],
.material-icons,
span:contains("keyboard"),
*[class*="icon"] { font-family: 'Nunito', sans-serif !important; }

/* Hide any orphaned icon text */
.st-emotion-cache-1whx7iy, .st-emotion-cache-r421ms, .st-emotion-cache-10trblm { display: none !important; }

/* Force hide keyboard text specifically */
p:empty, span:empty { display: none !important; }

/* Text colors */
h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
p, span, label, div, li { color: #e5e5e5; }

/* Form inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
[data-baseweb="select"] > div { background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: #ffffff !important; border-radius: 8px !important; }

/* Buttons */
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 0.5rem 1rem !important; }
.stButton > button:hover { opacity: 0.9; transform: translateY(-1px); }
.stDownloadButton > button { background: #1a1a2e !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; }

/* Tabs - completely restyle to avoid icons */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 8px; border-bottom: 1px solid rgba(99,102,241,0.2); }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #9ca3af !important; border: none !important; border-bottom: 2px solid transparent; padding: 12px 20px !important; }
.stTabs [aria-selected="true"] { background: transparent !important; color: #fff !important; border-bottom: 2px solid #6366f1 !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 20px; }

/* Radio buttons */
.stRadio > div { flex-direction: row !important; gap: 12px; flex-wrap: wrap; }
.stRadio > div > label { background: #12121a !important; padding: 10px 16px !important; border-radius: 8px !important; border: 1px solid rgba(99,102,241,0.2) !important; cursor: pointer; }
.stRadio > div > label:hover { border-color: rgba(99,102,241,0.5) !important; }
div[data-baseweb="radio"] > div { background: transparent !important; }

/* Checkbox */
.stCheckbox > label { color: #e5e5e5 !important; }
.stCheckbox > label > span { color: #e5e5e5 !important; }

/* File uploader */
[data-testid="stFileUploader"] { background: #12121a !important; border: 1px dashed rgba(99,102,241,0.3) !important; border-radius: 8px !important; padding: 20px !important; }
[data-testid="stFileUploader"] label { color: white !important; }
[data-testid="stFileUploader"] small { color: #9ca3af !important; }

/* Selectbox dropdown */
[data-baseweb="popover"] { background: #12121a !important; }
[data-baseweb="menu"] { background: #12121a !important; }
[role="option"] { color: #e5e5e5 !important; }
[role="option"]:hover { background: rgba(99,102,241,0.2) !important; }

/* Slider */
.stSlider > div > div { background: rgba(99,102,241,0.3) !important; }
.stSlider [data-baseweb="slider"] div { background: #6366f1 !important; }

/* Metrics */
[data-testid="stMetricValue"] { color: #fff !important; }
[data-testid="stMetricLabel"] { color: #9ca3af !important; }

/* Hide expander arrows completely */
.streamlit-expanderHeader { display: none !important; }
details summary { list-style: none !important; }
details summary::-webkit-details-marker { display: none !important; }
summary::marker { display: none !important; }

/* Success/Error/Warning/Info */
.stSuccess { background: rgba(16,185,129,0.1) !important; border: 1px solid #10b981 !important; }
.stError { background: rgba(239,68,68,0.1) !important; border: 1px solid #ef4444 !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid #f59e0b !important; }
.stInfo { background: rgba(99,102,241,0.1) !important; border: 1px solid #6366f1 !important; }

/* Custom components */
.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.metric-card { background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)); border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; text-align: center; }
.candidate-card { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 24px; margin: 16px 0; }
.output-box { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 20px; margin: 16px 0; white-space: pre-wrap; color: #e5e5e5; }

/* Status badge */
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; z-index: 999; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }

/* Floating feedback widget */
.feedback-widget { position: fixed; bottom: 20px; right: 20px; z-index: 1000; }
.feedback-btn { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border: none; border-radius: 50px; padding: 12px 24px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 15px rgba(99,102,241,0.4); display: flex; align-items: center; gap: 8px; }
.feedback-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(99,102,241,0.5); }
.feedback-panel { position: fixed; bottom: 80px; right: 20px; width: 320px; background: #12121a; border: 1px solid rgba(99,102,241,0.3); border-radius: 16px; padding: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); z-index: 1001; }
.feedback-panel h4 { color: white; margin: 0 0 16px 0; }
.feedback-close { position: absolute; top: 12px; right: 12px; background: none; border: none; color: #9ca3af; cursor: pointer; font-size: 18px; }

/* Compare table */
.compare-table { width: 100%; border-collapse: collapse; margin: 16px 0; }
.compare-table th, .compare-table td { border: 1px solid rgba(99,102,241,0.2); padding: 12px; text-align: center; color: #e5e5e5; }
.compare-table th { background: rgba(99,102,241,0.2); }
.compare-table tr:hover { background: rgba(99,102,241,0.1); }

/* Filter bar */
.filter-bar { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 8px; padding: 16px; margin-bottom: 20px; }
</style>""", unsafe_allow_html=True)

# Auth screen
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;">
            <h1 style="margin:0;">Sharp Screen</h1>
            <p style="color:#9ca3af;">AI CV Screening & Analysis</p>
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

# Sidebar - CLEAN, no feedback here
with st.sidebar:
    st.markdown(f"""<div class="user-card">
        <p style="color:#9ca3af;margin:0;font-size:12px;">Logged in as</p>
        <p style="color:#fff;margin:4px 0;font-weight:600;">{get_user_email()}</p>
        <p style="color:#6366f1;margin:0;font-size:12px;text-transform:uppercase;">{st.session_state.get('user_plan','free')} plan</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("**Apps**")
    for key, label in [("portal","Portal"),("jd","JD Writer"),("screen","CV Screener"),("interview","Interview"),("source","Sourcing"),("content","Content"),("sales","Sales"),("reach","Reach"),("assistant","Assistant")]:
        if key == "screen":
            st.markdown(f"<div style='background:rgba(99,102,241,0.3);padding:10px;border-radius:8px;text-align:center;margin:4px 0;'><strong>{label}</strong></div>", unsafe_allow_html=True)
        else:
            st.link_button(label, build_app_url(key), use_container_width=True)
    
    if st.session_state.get("is_god"):
        st.markdown("---")
        st.link_button("Admin", build_app_url("admin"), use_container_width=True)
    
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# FLOATING FEEDBACK WIDGET (bottom right)
feedback_html = """
<div class="feedback-widget">
    <button class="feedback-btn" onclick="document.getElementById('feedback-panel').style.display = document.getElementById('feedback-panel').style.display === 'none' ? 'block' : 'none';">
        💬 Feedback
    </button>
</div>
"""
st.markdown(feedback_html, unsafe_allow_html=True)

# Feedback form in main area (positioned at bottom)
with st.container():
    fb_col1, fb_col2, fb_col3 = st.columns([2, 1, 1])
    with fb_col3:
        if st.checkbox("Send Feedback", key="show_fb"):
            fb_type = st.selectbox("Type", ["Bug", "Feature", "General"], key="fb_type", label_visibility="collapsed")
            fb_msg = st.text_area("Message", height=100, key="fb_msg", placeholder="Your feedback...", label_visibility="collapsed")
            if st.button("Submit Feedback", key="fb_submit"):
                if fb_msg:
                    submit_feedback("screen", fb_type.lower(), fb_msg)
                    st.success("Thanks!")

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:30px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:50px;">
    <div><h1 style="margin:0;font-size:28px;">Sharp Screen</h1><p style="color:#9ca3af;margin:0;">AI-Powered CV Screening</p></div>
</div>""", unsafe_allow_html=True)

# Tabs
tab_screen, tab_blind, tab_salary = st.tabs(["Screen & Rank", "Blind Resume", "Salary Estimator"])

with tab_screen:
    # JD Input
    st.markdown("### Job Description")
    jd_src = st.radio("Source:", ["Paste JD", "From History", "Upload File"], horizontal=True, key="jd_src", label_visibility="collapsed")
    
    jd_text = ""
    jd_id = None
    
    if jd_src == "From History":
        history = get_jd_history(20)
        if history:
            opts = {f"{j['job_title']} ({j['created_at'][:10]})": j for j in history}
            sel = st.selectbox("Select:", list(opts.keys()), label_visibility="collapsed")
            if sel:
                jd_text = opts[sel].get('generated_jd', '')
                jd_id = opts[sel].get('id')
                st.success(f"Loaded: {opts[sel].get('job_title')}")
        else:
            st.info("No saved JDs")
            jd_text = st.text_area("Paste JD:", height=120, label_visibility="collapsed")
    elif jd_src == "Upload File":
        f = st.file_uploader("Upload JD", type=['pdf', 'docx', 'txt'], label_visibility="collapsed")
        if f:
            jd_text = extract_text_from_file(f)
            st.success(f"Loaded {f.name}")
    else:
        jd_text = st.text_area("Paste Job Description:", height=150, placeholder="Paste job description here...")
    
    st.markdown("---")
    
    # CV Input
    st.markdown("### Candidate CVs")
    cv_src = st.radio("Source:", ["Paste CVs", "Upload Files", "JSON/ATS"], horizontal=True, key="cv_src", label_visibility="collapsed")
    
    cvs_text = ""
    if cv_src == "Upload Files":
        files = st.file_uploader("Upload CVs", type=['pdf', 'docx', 'txt'], accept_multiple_files=True, label_visibility="collapsed")
        if files:
            st.success(f"{len(files)} files uploaded")
            cvs_text = "\n\n---\n\n".join([f"=== {f.name} ===\n{extract_text_from_file(f)}" for f in files])
    elif cv_src == "JSON/ATS":
        json_in = st.text_area("Paste JSON:", height=120, label_visibility="collapsed")
        if json_in:
            cands = parse_json_candidates(json_in)
            if cands:
                st.success(f"{len(cands)} candidates parsed")
                cvs_text = "\n\n---\n\n".join([json.dumps(c, indent=2) for c in cands])
    else:
        cvs_text = st.text_area("Paste CVs (separate with ---):", height=180, placeholder="CV 1...\n\n---\n\nCV 2...")
    
    st.markdown("---")
    
    # Options
    st.markdown("### Options")
    c1, c2, c3, c4 = st.columns(4)
    with c1: bias_free = st.checkbox("Bias-Free", value=True)
    with c2: ai_detect = st.checkbox("AI Detection", value=True)
    with c3: salary_est = st.checkbox("Salary Est.", value=True)
    with c4: save_hist = st.checkbox("Save Results", value=True)
    
    if st.button("Screen Candidates", type="primary", use_container_width=True):
        if not jd_text: st.warning("Provide JD")
        elif not cvs_text: st.warning("Provide CVs")
        else:
            st.session_state.working_on = "Analyzing..."
            with st.spinner("Screening candidates..."):
                result, tokens = screen_candidates(jd_text, cvs_text, {'bias_free': bias_free, 'ai_detection': ai_detect, 'salary_estimate': salary_est})
                st.session_state.working_on = None
                if not result.startswith("Error"):
                    st.session_state.screening_results = result
                    st.session_state.selected_candidates = []
                    if save_hist:
                        save_screen_history(jd_id, jd_text, cvs_text, result, cvs_text.count('---')+1, tokens)
                    st.rerun()
                else:
                    st.error(result)
    
    # Results
    if st.session_state.screening_results:
        st.markdown("---")
        
        try:
            match = re.search(r'```json\s*(.*?)\s*```', st.session_state.screening_results, re.DOTALL)
            data = json.loads(match.group(1) if match else st.session_state.screening_results)
            
            summary = data.get('screening_summary', {})
            candidates = data.get('candidates', [])
            insights = data.get('batch_insights', {})
            
            # Summary
            st.markdown("### Results")
            cols = st.columns(5)
            for col, (label, val, color) in zip(cols, [
                ("Candidates", summary.get('total_candidates', '?'), "#fff"),
                ("Recommended", summary.get('recommended_for_interview', '?'), "#10b981"),
                ("Maybe", summary.get('maybe', '?'), "#f59e0b"),
                ("Time Saved", f"~{summary.get('time_saved_minutes', '?')}m", "#6366f1"),
                ("Bias Score", f"{summary.get('bias_mitigation_score', '?')}", "#8b5cf6")
            ]):
                with col:
                    st.markdown(f'<div class="metric-card"><p style="color:#9ca3af;margin:0;font-size:11px;">{label}</p><p style="color:{color};font-size:24px;font-weight:bold;margin:0;">{val}</p></div>', unsafe_allow_html=True)
            
            # Filters
            st.markdown("### Filter & Sort")
            f1, f2, f3, f4 = st.columns(4)
            with f1: min_score = st.slider("Min Score", 0, 100, 0)
            with f2: salary_filter = st.selectbox("Salary", ["All", "Within Range", "Above", "Below"])
            with f3: sort_by = st.selectbox("Sort", ["Rank", "Score", "Experience", "AI Score"])
            with f4: compare_mode = st.checkbox("Compare Mode")
            
            # Apply filters
            filtered = [c for c in candidates if c.get('match_score', 0) >= min_score]
            if salary_filter != "All":
                filtered = [c for c in filtered if salary_filter.lower() in c.get('salary_alignment', '').lower()]
            
            if sort_by == "Score": filtered = sorted(filtered, key=lambda x: x.get('match_score', 0), reverse=True)
            elif sort_by == "Experience": filtered = sorted(filtered, key=lambda x: x.get('experience_years', 0), reverse=True)
            elif sort_by == "AI Score": filtered = sorted(filtered, key=lambda x: x.get('ai_written_probability', 0))
            
            # Compare
            if compare_mode and len(st.session_state.selected_candidates) >= 2:
                if st.button(f"Compare {len(st.session_state.selected_candidates)} Selected"):
                    st.session_state.working_on = "Comparing..."
                    selected_data = [c for c in candidates if c.get('identifier') in st.session_state.selected_candidates]
                    result, _ = compare_candidates(selected_data)
                    st.session_state.working_on = None
                    st.session_state.comparison_result = result
            
            if st.session_state.get('comparison_result'):
                st.markdown("### Comparison")
                try:
                    comp_match = re.search(r'```json\s*(.*?)\s*```', st.session_state.comparison_result, re.DOTALL)
                    comp_data = json.loads(comp_match.group(1) if comp_match else st.session_state.comparison_result)
                    table = comp_data.get('comparison_table', {})
                    if table.get('rows'):
                        html_table = "<table class='compare-table'><tr>" + "".join([f"<th>{h}</th>" for h in table.get('headers', [])]) + "</tr>"
                        for row in table.get('rows', []):
                            html_table += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"
                        html_table += "</table>"
                        st.markdown(html_table, unsafe_allow_html=True)
                    st.info(f"**Winner:** {comp_data.get('winner_recommendation', '')}")
                except:
                    st.markdown(f'<div class="output-box">{st.session_state.comparison_result}</div>', unsafe_allow_html=True)
                if st.button("Clear Comparison"):
                    st.session_state.comparison_result = None
                    st.session_state.selected_candidates = []
                    st.rerun()
            
            # Candidates
            st.markdown(f"### Candidates ({len(filtered)})")
            for c in filtered:
                score = c.get('match_score', 0)
                color = "#10b981" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
                identifier = c.get('identifier', 'Unknown')
                skills = c.get('skills_breakdown', {})
                
                if compare_mode:
                    is_sel = identifier in st.session_state.selected_candidates
                    if st.checkbox(f"Select {identifier}", value=is_sel, key=f"sel_{identifier}"):
                        if identifier not in st.session_state.selected_candidates:
                            st.session_state.selected_candidates.append(identifier)
                    else:
                        if identifier in st.session_state.selected_candidates:
                            st.session_state.selected_candidates.remove(identifier)
                
                st.markdown(f"""<div class="candidate-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div><span style="background:#6366f1;color:#fff;padding:4px 12px;border-radius:20px;">#{c.get('rank')}</span> <strong style="margin-left:12px;">{identifier}</strong></div>
                        <span style="font-size:28px;font-weight:bold;color:{color};">{score}%</span>
                    </div>
                </div>""", unsafe_allow_html=True)
                
                # Skills
                sk1, sk2, sk3, sk4 = st.columns(4)
                with sk1: st.metric("Technical", f"{skills.get('technical',{}).get('matched','?')}/{skills.get('technical',{}).get('total','?')}")
                with sk2: st.metric("Leadership", f"{skills.get('leadership',{}).get('matched','?')}/{skills.get('leadership',{}).get('total','?')}")
                with sk3: st.metric("Soft Skills", f"{skills.get('soft_skills',{}).get('matched','?')}/{skills.get('soft_skills',{}).get('total','?')}")
                with sk4: st.metric("Experience", f"{c.get('experience_years','?')} yrs")
                
                st.markdown(f"**Why:** {c.get('why_this_score', '')}")
                st.markdown(f"**Strengths:** {', '.join(c.get('strengths', []))}")
                st.markdown(f"**Concerns:** {', '.join(c.get('concerns', []))}")
                
                # Status & Actions
                current_status = st.session_state.candidate_statuses.get(identifier, "Reviewing")
                col_st, col_act = st.columns([1, 3])
                with col_st:
                    new_status = st.selectbox("Status", ["Reviewing", "Contacted", "Phone Screen", "Assessment", "Rejected", "Hired"], 
                        index=["Reviewing", "Contacted", "Phone Screen", "Assessment", "Rejected", "Hired"].index(current_status), key=f"st_{identifier}")
                    if new_status != current_status:
                        st.session_state.candidate_statuses[identifier] = new_status
                
                with col_act:
                    action = c.get('recommended_action', '')
                    bc1, bc2, bc3, bc4 = st.columns(4)
                    if score >= 70:
                        with bc1:
                            if st.button("Phone Screen", key=f"ps_{identifier}"):
                                st.session_state.working_on = "Drafting..."
                                email, _ = generate_email_template(c, "phone_screen", jd_text[:100])
                                st.session_state.working_on = None
                                st.session_state[f"email_{identifier}"] = email
                    if 50 <= score < 70:
                        with bc2:
                            if st.button("Skills Test", key=f"sk_{identifier}"):
                                st.session_state.working_on = "Drafting..."
                                email, _ = generate_email_template(c, "skills_test", jd_text[:100])
                                st.session_state.working_on = None
                                st.session_state[f"email_{identifier}"] = email
                    if score < 50:
                        with bc3:
                            if st.button("Rejection", key=f"rej_{identifier}"):
                                st.session_state.working_on = "Drafting..."
                                email, _ = generate_email_template(c, "rejection", jd_text[:100])
                                st.session_state.working_on = None
                                st.session_state[f"email_{identifier}"] = email
                    with bc4:
                        if st.button("LinkedIn", key=f"li_{identifier}"):
                            st.session_state.working_on = "Drafting..."
                            msg, _ = generate_email_template(c, "linkedin", jd_text[:100])
                            st.session_state.working_on = None
                            st.session_state[f"email_{identifier}"] = msg
                
                if st.session_state.get(f"email_{identifier}"):
                    st.text_area("Generated:", st.session_state[f"email_{identifier}"], height=120, key=f"em_{identifier}")
                    if st.button("Clear", key=f"cl_{identifier}"):
                        del st.session_state[f"email_{identifier}"]
                        st.rerun()
                
                st.markdown("---")
            
            # Batch Actions
            st.markdown("### Batch Actions")
            ba1, ba2 = st.columns(2)
            with ba1:
                if st.button("Generate HM Summary", use_container_width=True):
                    st.session_state.working_on = "Generating..."
                    result, _ = generate_hiring_manager_summary(candidates, bias_free)
                    st.session_state.working_on = None
                    st.session_state['hm_summary'] = result
            
            if st.session_state.get('hm_summary'):
                st.markdown("#### Hiring Manager Summary")
                st.markdown(f'<div class="output-box">{st.session_state.hm_summary}</div>', unsafe_allow_html=True)
            
            # Export
            st.markdown("### Export")
            e1, e2, e3, e4 = st.columns(4)
            with e1:
                pdf_html = generate_pdf_report(data, jd_text[:50] if jd_text else "Report")
                st.download_button("PDF Report", pdf_html, "screening_report.html", "text/html", use_container_width=True)
            with e2:
                st.download_button("CSV", generate_csv_report(data), "report.csv", "text/csv", use_container_width=True)
            with e3:
                st.download_button("JSON", json.dumps(data, indent=2), "data.json", "application/json", use_container_width=True)
            with e4:
                if st.button("New Screening", use_container_width=True):
                    st.session_state.screening_results = None
                    st.session_state.selected_candidates = []
                    st.session_state.comparison_result = None
                    st.rerun()
            
            # Insights
            if insights:
                st.markdown("### Insights")
                st.info(f"**Top:** {insights.get('strongest_candidate_summary', '')}")
                st.warning(f"**Gaps:** {', '.join(insights.get('common_gaps', []))}")
                st.success(f"**Recommendation:** {insights.get('hiring_recommendation', '')}")
        
        except Exception as e:
            st.markdown(f'<div class="output-box">{st.session_state.screening_results}</div>', unsafe_allow_html=True)

with tab_blind:
    st.markdown("### Blind Resume Anonymization")
    c1, c2 = st.columns([2, 1])
    with c1:
        src = st.radio("Source:", ["Paste", "Upload"], horizontal=True, key="anon_src")
        if src == "Upload":
            f = st.file_uploader("Upload CV", type=['pdf', 'docx', 'txt'], key="anon_file")
            resume = extract_text_from_file(f) if f else ""
        else:
            resume = st.text_area("Paste resume:", height=250)
    with c2:
        time_based = st.checkbox("Time-based dates")
        st.caption("Removes: names, emails, phones, addresses, universities, companies")
    
    if st.button("Anonymize", type="primary", use_container_width=True):
        if resume:
            st.session_state.working_on = "Anonymizing..."
            result, _ = anonymize_cv(resume, {'time_based': time_based})
            st.session_state.working_on = None
            if not result.startswith("Error"):
                st.session_state.anonymized_result = result
                st.rerun()
            else:
                st.error(result)
    
    if st.session_state.get('anonymized_result'):
        try:
            match = re.search(r'```json\s*(.*?)\s*```', st.session_state.anonymized_result, re.DOTALL)
            data = json.loads(match.group(1) if match else st.session_state.anonymized_result)
            st.metric("Confidence", f"{data.get('anonymization_score', 0)}%")
            st.markdown(f'<div class="output-box">{data.get("anonymized_cv", "")}</div>', unsafe_allow_html=True)
            st.download_button("Download", data.get("anonymized_cv", ""), "anonymized.txt", use_container_width=True)
        except:
            st.markdown(f'<div class="output-box">{st.session_state.anonymized_result}</div>', unsafe_allow_html=True)

with tab_salary:
    st.markdown("### Salary Estimator")
    c1, c2 = st.columns(2)
    with c1: sal_jd = st.text_area("Job Description:", height=150, key="sal_jd")
    with c2: sal_cv = st.text_area("Candidate CV:", height=150, key="sal_cv")
    location = st.selectbox("Market:", ["US - National", "US - SF Bay Area", "US - NYC", "US - Remote", "UK - London", "EU", "Canada"])
    
    if st.button("Estimate Salary", type="primary", use_container_width=True):
        if sal_jd and sal_cv:
            st.session_state.working_on = "Estimating..."
            result, _ = estimate_salary(sal_cv, sal_jd, location)
            st.session_state.working_on = None
            if not result.startswith("Error"):
                st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
            else:
                st.error(result)
