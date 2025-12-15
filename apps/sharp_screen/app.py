"""Sharp Screen - Advanced CV Screening with Cross-App Auth"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re
import io
import base64

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
                "device_hash": "screen",
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
        ('screening_results', None),
        ('current_status', None),
        ('uploaded_cvs', []),
        ('selected_jd', None),
        ('anonymized_cvs', []),
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
# JD HISTORY FUNCTIONS
# ============================================

def get_jd_history(limit=50):
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

def save_screen_history(jd_id, jd_text, candidates_input, result, candidates_count, tokens_used):
    user_id = st.session_state.user.get("id") if st.session_state.user else None
    if not user_id or user_id == "god":
        return None
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/screen_history",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json={
                "user_id": user_id,
                "jd_history_id": jd_id,
                "job_description": jd_text,
                "candidates_input": candidates_input[:5000],
                "screening_result": result,
                "candidates_count": candidates_count,
                "tokens_used": tokens_used
            },
            timeout=10
        )
        if r.status_code in [200, 201]:
            return r.json()[0] if r.json() else None
    except:
        pass
    return None

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
# FILE PROCESSING FUNCTIONS
# ============================================

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded files (PDF, DOCX, TXT)."""
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
            # Try to extract readable text
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
            # Handle ATS JSON formats
            if isinstance(data, list):
                return '\n---\n'.join([json.dumps(item, indent=2) for item in data])
            return json.dumps(data, indent=2)
        except:
            return content.decode('utf-8', errors='ignore')
    
    return content.decode('utf-8', errors='ignore')

def parse_json_candidates(json_text):
    """Parse JSON formatted candidate data from ATS systems."""
    try:
        data = json.loads(json_text)
        candidates = []
        
        if isinstance(data, list):
            for item in data:
                candidate = {
                    'name': item.get('name') or item.get('candidateName') or item.get('full_name', 'Unknown'),
                    'email': item.get('email') or item.get('emailAddress', ''),
                    'phone': item.get('phone') or item.get('phoneNumber', ''),
                    'experience': item.get('experience') or item.get('work_experience', []),
                    'education': item.get('education') or item.get('educationHistory', []),
                    'skills': item.get('skills') or item.get('skillSet', []),
                    'summary': item.get('summary') or item.get('professionalSummary', ''),
                }
                candidates.append(candidate)
        elif isinstance(data, dict):
            if 'candidates' in data:
                return parse_json_candidates(json.dumps(data['candidates']))
            candidates.append(data)
        
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
                          json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, 
                          timeout=180)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            tokens_used = (len(prompt) + len(text)) // 4
            if st.session_state.user:
                log_usage(
                    st.session_state.user.get("id"),
                    st.session_state.get("session_token"),
                    "screen",
                    action,
                    tokens_used
                )
            return text, tokens_used
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0

# ============================================
# SCREENING FUNCTIONS
# ============================================

def screen_candidates(jd_text, cvs_text, options):
    """Screen candidates against JD with advanced analysis."""
    
    prompt = f"""You are an expert technical recruiter and CV screening specialist. Analyze these candidates against the job description.

## JOB DESCRIPTION:
{jd_text}

## CANDIDATES (CVs separated by ---):
{cvs_text}

## SCREENING OPTIONS:
- Bias-Free Mode: {options.get('bias_free', True)} (if true, ignore names, gender, age, photos, universities for ranking)
- Include AI Detection: {options.get('ai_detection', True)}
- Include Salary Estimate: {options.get('salary_estimate', True)}

## REQUIRED OUTPUT FORMAT (JSON):
Return a JSON object with this exact structure:
```json
{{
    "screening_summary": {{
        "total_candidates": <number>,
        "recommended_for_interview": <number>,
        "maybe": <number>,
        "not_recommended": <number>,
        "time_saved_minutes": <estimated minutes saved by AI screening>
    }},
    "candidates": [
        {{
            "rank": <1-based ranking>,
            "identifier": "<Candidate A/B/C if bias-free, else name>",
            "match_score": <0-100>,
            "required_skills_match": "<X/Y matched>",
            "preferred_skills_match": "<X/Y matched>",
            "experience_years": <number or range>,
            "why_this_score": "<2-3 sentence summary of best fit areas and biggest gaps>",
            "strengths": ["<strength1>", "<strength2>", "<strength3>"],
            "concerns": ["<concern1>", "<concern2>"],
            "ai_written_probability": <0-100 if ai_detection enabled>,
            "ai_detection_flags": ["<flag1>", "<flag2>"] or [],
            "estimated_salary_range": "<$X-$Y>" or null,
            "salary_reasoning": "<brief explanation>",
            "recommended_action": "<Recommend for Phone Screen | Recommend for Technical Assessment | Recommend for Hiring Manager Review | Hold for Future | Reject - Template A (Overqualified) | Reject - Template B (Underqualified) | Reject - Template C (Skills Mismatch)>",
            "next_steps": "<specific recommended next steps>"
        }}
    ],
    "batch_insights": {{
        "strongest_candidate_summary": "<why the top candidate stands out>",
        "common_gaps": ["<gap1>", "<gap2>"],
        "hiring_recommendation": "<overall recommendation for this batch>"
    }}
}}
```

Be thorough, fair, and data-driven. Provide actionable insights."""

    return call_claude(prompt, max_tokens=4000, action="screen_batch")

def anonymize_cv(cv_text, options):
    """Anonymize a CV removing identifying information."""
    
    time_based = options.get('time_based', False)
    
    prompt = f"""Anonymize this CV/resume by removing or redacting all identifying information.

## CV TO ANONYMIZE:
{cv_text}

## ANONYMIZATION REQUIREMENTS:
1. Remove/redact: Full names, email addresses, phone numbers, physical addresses, LinkedIn URLs, personal websites
2. Remove/redact: Photo references, age indicators, date of birth
3. {"Replace specific dates with relative time (e.g., '2020-2023' becomes '3 years ago - Present')" if time_based else "Keep dates but remove birth dates"}
4. Replace university names with "[University - Tier 1/2/3]" or "[Ivy League]", "[State University]", etc.
5. Replace company names with industry descriptors like "[Fortune 500 Tech Company]", "[Series B Startup]", "[Government Agency]"
6. Keep all skills, achievements, responsibilities, and metrics intact
7. Preserve the structure and readability

## OUTPUT FORMAT (JSON):
```json
{{
    "anonymized_cv": "<the fully anonymized CV text>",
    "items_removed": {{
        "names": ["<list of names found and removed>"],
        "emails": ["<list of emails removed>"],
        "phones": ["<list of phone numbers removed>"],
        "addresses": ["<list of addresses removed>"],
        "universities": ["<original> → <replacement>"],
        "companies": ["<original> → <replacement>"],
        "dates_modified": ["<list of date changes if time-based>"],
        "other": ["<any other PII removed>"]
    }},
    "anonymization_score": <0-100 confidence that CV is fully anonymized>
}}
```"""

    return call_claude(prompt, max_tokens=3000, action="anonymize")

def analyze_github(github_url):
    """Analyze a GitHub profile for recruiting purposes."""
    
    prompt = f"""Analyze this GitHub profile URL for technical recruiting purposes: {github_url}

Note: You cannot actually access the URL, but based on the username and common patterns, provide a framework for what a recruiter should look for when they visit this profile.

## PROVIDE ANALYSIS FRAMEWORK:
```json
{{
    "profile_url": "{github_url}",
    "analysis_checklist": {{
        "code_quality_indicators": [
            "Look for: consistent code style",
            "Look for: meaningful commit messages", 
            "Look for: documentation and README files",
            "Look for: test coverage",
            "Look for: code organization"
        ],
        "activity_metrics_to_check": [
            "Contribution frequency (daily/weekly/monthly)",
            "Commit streak patterns",
            "Recent activity (last 30/60/90 days)",
            "Peak coding times"
        ],
        "project_evaluation": [
            "Number of original repositories",
            "Stars and forks received",
            "Languages used",
            "Project complexity and scope"
        ],
        "collaboration_signals": [
            "Pull requests submitted to other projects",
            "Issues created and resolved",
            "Code review participation",
            "Open source contributions"
        ],
        "red_flags_to_watch": [
            "Empty or sparse profile",
            "Only forked repositories with no modifications",
            "No recent activity",
            "Copied code without attribution"
        ],
        "green_flags_to_watch": [
            "Active contributions to popular projects",
            "Well-documented personal projects",
            "Diverse technology stack",
            "Community engagement"
        ]
    }},
    "suggested_interview_questions": [
        "<question about their most starred project>",
        "<question about a specific technology they use>",
        "<question about their contribution workflow>"
    ],
    "overall_guidance": "<how to interpret what you find on this profile>"
}}
```

Provide actionable guidance for the recruiter reviewing this profile."""

    return call_claude(prompt, max_tokens=2000, action="github_analysis")

def estimate_salary(cv_text, jd_text, location="US"):
    """Estimate salary range for a candidate based on their CV and the JD."""
    
    prompt = f"""Based on this candidate's CV and the job description, estimate an appropriate salary range.

## JOB DESCRIPTION:
{jd_text[:2000]}

## CANDIDATE CV:
{cv_text[:3000]}

## LOCATION CONTEXT: {location}

## PROVIDE SALARY ANALYSIS:
```json
{{
    "estimated_range": {{
        "low": <number>,
        "mid": <number>,
        "high": <number>,
        "currency": "USD"
    }},
    "confidence": "<Low | Medium | High>",
    "factors_increasing_salary": [
        "<factor1>",
        "<factor2>"
    ],
    "factors_decreasing_salary": [
        "<factor1>",
        "<factor2>"
    ],
    "market_context": "<brief note on current market for this role>",
    "negotiation_advice": "<advice for the hiring team>"
}}
```"""

    return call_claude(prompt, max_tokens=1500, action="salary_estimate")

# ============================================
# REPORT GENERATION
# ============================================

def generate_csv_report(screening_data):
    """Generate a CSV report from screening results."""
    try:
        data = json.loads(screening_data) if isinstance(screening_data, str) else screening_data
        candidates = data.get('candidates', [])
        
        csv_lines = ["Rank,Identifier,Match Score,Required Skills,Preferred Skills,Experience,AI Probability,Salary Estimate,Recommended Action,Why This Score"]
        
        for c in candidates:
            line = f"{c.get('rank', '')},{c.get('identifier', '')},{c.get('match_score', '')},{c.get('required_skills_match', '')},{c.get('preferred_skills_match', '')},{c.get('experience_years', '')},{c.get('ai_written_probability', 'N/A')},{c.get('estimated_salary_range', 'N/A')},{c.get('recommended_action', '')},\"{c.get('why_this_score', '')}\""
            csv_lines.append(line)
        
        return '\n'.join(csv_lines)
    except:
        return "Error generating CSV report"

def generate_detailed_report(screening_data, jd_title=""):
    """Generate a detailed text report."""
    try:
        data = json.loads(screening_data) if isinstance(screening_data, str) else screening_data
        summary = data.get('screening_summary', {})
        candidates = data.get('candidates', [])
        insights = data.get('batch_insights', {})
        
        report = f"""
═══════════════════════════════════════════════════════════════
                    CV SCREENING REPORT
                    {jd_title or 'Candidate Analysis'}
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
═══════════════════════════════════════════════════════════════

SUMMARY
───────────────────────────────────────────────────────────────
Total Candidates Screened: {summary.get('total_candidates', 'N/A')}
Recommended for Interview: {summary.get('recommended_for_interview', 'N/A')}
Maybe/Further Review:      {summary.get('maybe', 'N/A')}
Not Recommended:           {summary.get('not_recommended', 'N/A')}
Time Saved:                ~{summary.get('time_saved_minutes', 'N/A')} minutes

CANDIDATE RANKINGS
───────────────────────────────────────────────────────────────
"""
        for c in candidates:
            report += f"""
#{c.get('rank', '?')} - {c.get('identifier', 'Unknown')}
   Match Score: {c.get('match_score', 'N/A')}%
   Required Skills: {c.get('required_skills_match', 'N/A')}
   Preferred Skills: {c.get('preferred_skills_match', 'N/A')}
   Experience: {c.get('experience_years', 'N/A')} years
   
   Why This Score: {c.get('why_this_score', 'N/A')}
   
   Strengths: {', '.join(c.get('strengths', []))}
   Concerns: {', '.join(c.get('concerns', []))}
   
   AI Detection: {c.get('ai_written_probability', 'N/A')}% probability
   Salary Estimate: {c.get('estimated_salary_range', 'N/A')}
   
   ➤ RECOMMENDATION: {c.get('recommended_action', 'N/A')}
   ➤ Next Steps: {c.get('next_steps', 'N/A')}
───────────────────────────────────────────────────────────────
"""
        
        report += f"""
BATCH INSIGHTS
───────────────────────────────────────────────────────────────
Top Candidate: {insights.get('strongest_candidate_summary', 'N/A')}

Common Gaps in Candidate Pool:
{chr(10).join(['  • ' + gap for gap in insights.get('common_gaps', [])])}

Overall Recommendation:
{insights.get('hiring_recommendation', 'N/A')}

═══════════════════════════════════════════════════════════════
                    END OF REPORT
═══════════════════════════════════════════════════════════════
"""
        return report
    except Exception as e:
        return f"Error generating report: {str(e)}"

# ============================================
# UI COMPONENTS
# ============================================

def render_auth():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%); }
    * { font-family: 'Nunito', sans-serif !important; }
    .stTextInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; }
    .stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; }
    .stTabs [data-baseweb="tab-list"] { background: #12121a; }
    .stTabs [aria-selected="true"] { background: rgba(99,102,241,0.3) !important; color: white !important; }
    </style>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:40px 0;"><img src="https://sharphuman.com/logo1-3.png" style="width:70px;margin-bottom:16px;"><h1 style="color:white;">Sharp Screen</h1><p style="color:#9ca3af;">AI CV Screening & Analysis</p></div>""", unsafe_allow_html=True)
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
            if app_key == "screen":
                st.button(f"{label} ◀", disabled=True, use_container_width=True)
            else:
                st.link_button(label, build_app_url(app_key), use_container_width=True)
        
        if st.session_state.get("is_god") or st.session_state.get("user_plan") == "god":
            st.markdown("---")
            st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
        
        st.markdown("---")
        with st.expander("💬 Feedback", expanded=False):
            fb_type = st.selectbox("Type", ["General", "Bug", "Feature Request"], key="fb_type")
            fb_msg = st.text_area("Message", key="fb_msg", height=80)
            if st.button("Send", key="fb_send"):
                if fb_msg:
                    submit_feedback("screen", fb_type.lower(), 4, fb_msg)
                    st.success("Thanks! 🙏")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp Screen", page_icon="🔍", layout="wide")
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
.score-high { color: #10b981 !important; font-weight: bold; }
.score-med { color: #f59e0b !important; font-weight: bold; }
.score-low { color: #ef4444 !important; font-weight: bold; }
.status-badge { background: rgba(99,102,241,0.2); border: 1px solid rgba(99,102,241,0.4); border-radius: 8px; padding: 8px 16px; }
.metric-card { background: rgba(99,102,241,0.1); border-radius: 8px; padding: 16px; text-align: center; }
</style>""", unsafe_allow_html=True)

render_sidebar()

# Header
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;">
        <img src="https://sharphuman.com/logo1-3.png" style="width:45px;">
        <div><h1 style="margin:0;">Sharp Screen</h1><p style="color:#9ca3af;margin:0;">AI-Powered CV Screening & Analysis</p></div>
    </div>""", unsafe_allow_html=True)
with header_col2:
    if st.session_state.current_status:
        st.markdown(f'<div class="status-badge">✨ {st.session_state.current_status}</div>', unsafe_allow_html=True)

# Main tabs
tab_screen, tab_blind, tab_github, tab_salary = st.tabs(["🔍 Screen & Rank", "👤 Blind Resume", "💻 GitHub Analysis", "💰 Salary Estimator"])

with tab_screen:
    st.markdown("### 📋 Job Description")
    
    # JD Source selection
    jd_source = st.radio("JD Source:", ["📝 Paste JD", "📜 From JD History", "📄 Upload JD File"], horizontal=True)
    
    jd_text = ""
    selected_jd_id = None
    
    if jd_source == "📜 From JD History":
        jd_history = get_jd_history(20)
        if jd_history:
            jd_options = {f"{jd['job_title']} - {jd.get('company', 'N/A')} ({jd['created_at'][:10]})": jd for jd in jd_history}
            selected_jd_label = st.selectbox("Select a saved JD:", list(jd_options.keys()))
            if selected_jd_label:
                selected_jd = jd_options[selected_jd_label]
                jd_text = selected_jd.get('generated_jd', '')
                selected_jd_id = selected_jd.get('id')
                with st.expander("Preview JD"):
                    st.text(jd_text[:1000] + "..." if len(jd_text) > 1000 else jd_text)
        else:
            st.info("No saved JDs found. Create some in Sharp JD first!")
            jd_text = st.text_area("Or paste JD here:", height=150)
    
    elif jd_source == "📄 Upload JD File":
        jd_file = st.file_uploader("Upload JD (PDF, DOCX, TXT)", type=['pdf', 'docx', 'doc', 'txt'], key="jd_upload")
        if jd_file:
            jd_text = extract_text_from_file(jd_file)
            with st.expander("Preview extracted JD"):
                st.text(jd_text[:1000] + "..." if len(jd_text) > 1000 else jd_text)
    else:
        jd_text = st.text_area("Paste Job Description:", height=150, placeholder="Paste the full job description here...")
    
    st.markdown("---")
    st.markdown("### 📄 Candidate CVs")
    
    cv_source = st.radio("CV Source:", ["📝 Paste CVs", "📁 Upload Files", "🔗 JSON (ATS Export)"], horizontal=True)
    
    cvs_text = ""
    
    if cv_source == "📁 Upload Files":
        cv_files = st.file_uploader(
            "Upload CVs (PDF, DOCX, TXT) - Multiple files supported",
            type=['pdf', 'docx', 'doc', 'txt'],
            accept_multiple_files=True,
            key="cv_upload"
        )
        if cv_files:
            st.success(f"📎 {len(cv_files)} files uploaded")
            extracted_cvs = []
            for f in cv_files:
                text = extract_text_from_file(f)
                extracted_cvs.append(f"=== {f.name} ===\n{text}")
            cvs_text = "\n\n---\n\n".join(extracted_cvs)
            with st.expander(f"Preview {len(cv_files)} CVs"):
                st.text(cvs_text[:2000] + "..." if len(cvs_text) > 2000 else cvs_text)
    
    elif cv_source == "🔗 JSON (ATS Export)":
        json_input = st.text_area("Paste JSON from ATS:", height=150, placeholder='[{"name": "John Doe", "skills": [...], ...}]')
        if json_input:
            candidates = parse_json_candidates(json_input)
            if candidates:
                st.success(f"✅ Parsed {len(candidates)} candidates from JSON")
                cvs_text = "\n\n---\n\n".join([json.dumps(c, indent=2) for c in candidates])
            else:
                st.error("Could not parse JSON. Check format.")
    else:
        cvs_text = st.text_area("Paste CVs (separate with ---):", height=200, placeholder="Paste CV 1 here...\n\n---\n\nPaste CV 2 here...\n\n---\n\nPaste CV 3 here...")
    
    st.markdown("---")
    st.markdown("### ⚙️ Screening Options")
    
    opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)
    with opt_col1:
        bias_free = st.checkbox("🔒 Bias-Free Ranking", value=True, help="Ignore names, gender, age, universities")
    with opt_col2:
        ai_detection = st.checkbox("🤖 AI Detection", value=True, help="Flag potentially AI-written resumes")
    with opt_col3:
        salary_estimate = st.checkbox("💰 Salary Estimates", value=True, help="Estimate salary ranges")
    with opt_col4:
        save_to_history = st.checkbox("💾 Save Results", value=True, help="Save to screening history")
    
    if st.button("🔍 Screen Candidates", type="primary", use_container_width=True):
        if not jd_text:
            st.warning("Please provide a job description")
        elif not cvs_text:
            st.warning("Please provide candidate CVs")
        else:
            st.session_state.current_status = "Analyzing candidates..."
            
            options = {
                'bias_free': bias_free,
                'ai_detection': ai_detection,
                'salary_estimate': salary_estimate
            }
            
            with st.spinner("🔍 Analyzing candidates... Comparing qualifications against requirements."):
                result, tokens = screen_candidates(jd_text, cvs_text, options)
                
                if not result.startswith("Error"):
                    st.session_state.screening_results = result
                    st.session_state.current_status = None
                    
                    # Try to save
                    if save_to_history:
                        candidate_count = cvs_text.count('---') + 1
                        save_screen_history(selected_jd_id, jd_text[:2000], cvs_text[:5000], result, candidate_count, tokens)
                    
                    st.rerun()
                else:
                    st.error(result)
                    st.session_state.current_status = None
    
    # Display results
    if st.session_state.screening_results:
        st.markdown("---")
        st.markdown("### 📊 Screening Results")
        
        try:
            # Try to parse as JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', st.session_state.screening_results, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                data = json.loads(st.session_state.screening_results)
            
            summary = data.get('screening_summary', {})
            candidates = data.get('candidates', [])
            insights = data.get('batch_insights', {})
            
            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""<div class="metric-card">
                    <p style="color:#9ca3af;margin:0;font-size:0.75rem;">Candidates</p>
                    <p style="color:white;font-size:2rem;margin:0;">{summary.get('total_candidates', 'N/A')}</p>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card">
                    <p style="color:#9ca3af;margin:0;font-size:0.75rem;">Recommended</p>
                    <p style="color:#10b981;font-size:2rem;margin:0;">{summary.get('recommended_for_interview', 'N/A')}</p>
                </div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-card">
                    <p style="color:#9ca3af;margin:0;font-size:0.75rem;">Maybe</p>
                    <p style="color:#f59e0b;font-size:2rem;margin:0;">{summary.get('maybe', 'N/A')}</p>
                </div>""", unsafe_allow_html=True)
            with m4:
                st.markdown(f"""<div class="metric-card">
                    <p style="color:#9ca3af;margin:0;font-size:0.75rem;">⏱️ Time Saved</p>
                    <p style="color:#6366f1;font-size:2rem;margin:0;">~{summary.get('time_saved_minutes', 'N/A')}m</p>
                </div>""", unsafe_allow_html=True)
            
            st.markdown("")
            
            # Candidate cards
            for c in candidates:
                score = c.get('match_score', 0)
                score_class = "score-high" if score >= 70 else "score-med" if score >= 50 else "score-low"
                
                with st.expander(f"#{c.get('rank', '?')} {c.get('identifier', 'Unknown')} - {score}% Match", expanded=(c.get('rank', 99) <= 3)):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Match Score:** <span class='{score_class}'>{score}%</span>", unsafe_allow_html=True)
                        st.markdown(f"**Required Skills:** {c.get('required_skills_match', 'N/A')}")
                        st.markdown(f"**Preferred Skills:** {c.get('preferred_skills_match', 'N/A')}")
                        st.markdown(f"**Experience:** {c.get('experience_years', 'N/A')} years")
                        
                        st.markdown("---")
                        st.markdown(f"**Why this score:** {c.get('why_this_score', 'N/A')}")
                        
                        st.markdown("**Strengths:**")
                        for s in c.get('strengths', []):
                            st.markdown(f"  ✅ {s}")
                        
                        st.markdown("**Concerns:**")
                        for concern in c.get('concerns', []):
                            st.markdown(f"  ⚠️ {concern}")
                    
                    with col2:
                        if c.get('ai_written_probability') is not None:
                            ai_prob = c.get('ai_written_probability', 0)
                            ai_color = "#ef4444" if ai_prob > 70 else "#f59e0b" if ai_prob > 40 else "#10b981"
                            st.markdown(f"""<div style="background:rgba(0,0,0,0.3);padding:12px;border-radius:8px;margin-bottom:12px;">
                                <p style="color:#9ca3af;margin:0;font-size:0.7rem;">🤖 AI Detection</p>
                                <p style="color:{ai_color};font-size:1.5rem;margin:0;">{ai_prob}%</p>
                            </div>""", unsafe_allow_html=True)
                        
                        if c.get('estimated_salary_range'):
                            st.markdown(f"""<div style="background:rgba(0,0,0,0.3);padding:12px;border-radius:8px;margin-bottom:12px;">
                                <p style="color:#9ca3af;margin:0;font-size:0.7rem;">💰 Salary Estimate</p>
                                <p style="color:white;font-size:1rem;margin:0;">{c.get('estimated_salary_range')}</p>
                            </div>""", unsafe_allow_html=True)
                        
                        st.markdown(f"""<div style="background:rgba(99,102,241,0.2);padding:12px;border-radius:8px;">
                            <p style="color:#9ca3af;margin:0;font-size:0.7rem;">➤ Recommendation</p>
                            <p style="color:white;font-size:0.85rem;margin:0;">{c.get('recommended_action', 'N/A')}</p>
                        </div>""", unsafe_allow_html=True)
            
            # Batch insights
            if insights:
                st.markdown("---")
                st.markdown("### 💡 Batch Insights")
                st.info(f"**Top Candidate:** {insights.get('strongest_candidate_summary', 'N/A')}")
                
                if insights.get('common_gaps'):
                    st.warning(f"**Common Gaps:** {', '.join(insights.get('common_gaps', []))}")
                
                st.success(f"**Hiring Recommendation:** {insights.get('hiring_recommendation', 'N/A')}")
            
            # Download buttons
            st.markdown("---")
            dl_col1, dl_col2, dl_col3 = st.columns(3)
            
            with dl_col1:
                csv_report = generate_csv_report(data)
                st.download_button("📥 Download CSV", csv_report, "screening_report.csv", "text/csv", use_container_width=True)
            
            with dl_col2:
                detailed_report = generate_detailed_report(data, jd_text[:50] if jd_text else "")
                st.download_button("📥 Download Report", detailed_report, "screening_report.txt", "text/plain", use_container_width=True)
            
            with dl_col3:
                if st.button("🔄 New Screening", use_container_width=True):
                    st.session_state.screening_results = None
                    st.rerun()
        
        except Exception as e:
            st.markdown(f'<div class="output-box">{st.session_state.screening_results}</div>', unsafe_allow_html=True)

with tab_blind:
    st.markdown("### 👤 Blind Resume / CV Anonymization")
    st.markdown("Remove identifying information to reduce unconscious bias in hiring.")
    
    anon_col1, anon_col2 = st.columns([2, 1])
    
    with anon_col1:
        anon_source = st.radio("Source:", ["📝 Paste", "📄 Upload"], horizontal=True, key="anon_source")
        
        if anon_source == "📄 Upload":
            anon_file = st.file_uploader("Upload CV", type=['pdf', 'docx', 'doc', 'txt'], key="anon_upload")
            if anon_file:
                resume_to_anon = extract_text_from_file(anon_file)
            else:
                resume_to_anon = ""
        else:
            resume_to_anon = st.text_area("Paste resume to anonymize:", height=300, key="anon_text")
    
    with anon_col2:
        st.markdown("#### Options")
        time_based_anon = st.checkbox("⏱️ Time-Based Dates", value=False, help="Convert dates to relative time (e.g., '3 years ago')")
        redact_universities = st.checkbox("🎓 Anonymize Universities", value=True)
        redact_companies = st.checkbox("🏢 Anonymize Companies", value=True)
        
        st.markdown("#### What Gets Removed:")
        st.markdown("""
        - ✓ Names
        - ✓ Email addresses
        - ✓ Phone numbers
        - ✓ Physical addresses
        - ✓ LinkedIn/Social URLs
        - ✓ Age indicators
        - ✓ Photos references
        """)
    
    if st.button("👤 Anonymize Resume", type="primary", use_container_width=True):
        if resume_to_anon:
            with st.spinner("🔬 Anonymizing... Removing identifying information."):
                options = {'time_based': time_based_anon}
                result, _ = anonymize_cv(resume_to_anon, options)
                
                if not result.startswith("Error"):
                    st.session_state.anonymized_result = result
                    st.rerun()
                else:
                    st.error(result)
        else:
            st.warning("Please provide a resume to anonymize")
    
    if st.session_state.get('anonymized_result'):
        st.markdown("---")
        st.markdown("### ✅ Anonymized Result")
        
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', st.session_state.anonymized_result, re.DOTALL)
            if json_match:
                anon_data = json.loads(json_match.group(1))
            else:
                anon_data = json.loads(st.session_state.anonymized_result)
            
            # Show what was removed
            items_removed = anon_data.get('items_removed', {})
            if items_removed:
                with st.expander("🔍 Items Removed/Redacted", expanded=True):
                    for category, items in items_removed.items():
                        if items:
                            st.markdown(f"**{category.replace('_', ' ').title()}:** {', '.join(items) if isinstance(items, list) else items}")
            
            # Anonymization score
            score = anon_data.get('anonymization_score', 0)
            score_color = "#10b981" if score >= 90 else "#f59e0b" if score >= 70 else "#ef4444"
            st.markdown(f"**Anonymization Confidence:** <span style='color:{score_color};font-weight:bold;'>{score}%</span>", unsafe_allow_html=True)
            
            # Anonymized CV
            st.markdown("#### Anonymized CV:")
            st.markdown(f'<div class="output-box">{anon_data.get("anonymized_cv", "")}</div>', unsafe_allow_html=True)
            
            # Download
            st.download_button(
                "📥 Download Anonymized CV",
                anon_data.get("anonymized_cv", ""),
                "anonymized_cv.txt",
                "text/plain",
                use_container_width=True
            )
        except:
            st.markdown(f'<div class="output-box">{st.session_state.anonymized_result}</div>', unsafe_allow_html=True)

with tab_github:
    st.markdown("### 💻 GitHub Profile Analysis")
    st.markdown("Evaluate a candidate's GitHub profile for technical recruiting.")
    
    github_url = st.text_input("GitHub Profile URL", placeholder="https://github.com/username")
    
    gh_col1, gh_col2 = st.columns(2)
    with gh_col1:
        st.markdown("#### What We Analyze:")
        st.markdown("""
        - 📊 Code quality indicators
        - 📈 Commit activity trends
        - 🔧 Technology stack
        - 🤝 Collaboration signals
        - ⭐ Project impact (stars/forks)
        """)
    
    with gh_col2:
        st.markdown("#### Output Includes:")
        st.markdown("""
        - ✅ Green flags to look for
        - 🚩 Red flags to watch
        - ❓ Interview questions
        - 📋 Evaluation checklist
        """)
    
    if st.button("💻 Analyze GitHub Profile", type="primary", use_container_width=True):
        if github_url and "github.com" in github_url:
            with st.spinner("💻 Analyzing GitHub profile... Evaluating technical indicators."):
                result, _ = analyze_github(github_url)
                
                if not result.startswith("Error"):
                    st.markdown("---")
                    st.markdown("### 📊 Analysis Framework")
                    
                    try:
                        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                        if json_match:
                            gh_data = json.loads(json_match.group(1))
                        else:
                            gh_data = json.loads(result)
                        
                        checklist = gh_data.get('analysis_checklist', {})
                        
                        for section, items in checklist.items():
                            with st.expander(f"📋 {section.replace('_', ' ').title()}", expanded=True):
                                for item in items:
                                    st.markdown(f"• {item}")
                        
                        if gh_data.get('suggested_interview_questions'):
                            st.markdown("#### 💬 Suggested Interview Questions:")
                            for q in gh_data.get('suggested_interview_questions', []):
                                st.markdown(f"• {q}")
                        
                        if gh_data.get('overall_guidance'):
                            st.info(f"**Guidance:** {gh_data.get('overall_guidance')}")
                    
                    except:
                        st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
                else:
                    st.error(result)
        else:
            st.warning("Please enter a valid GitHub URL")

with tab_salary:
    st.markdown("### 💰 Salary Estimator")
    st.markdown("Estimate appropriate salary ranges based on candidate profile and job requirements.")
    
    sal_col1, sal_col2 = st.columns(2)
    
    with sal_col1:
        st.markdown("#### Job Description")
        sal_jd = st.text_area("Paste JD:", height=150, key="sal_jd", placeholder="Paste the job description...")
    
    with sal_col2:
        st.markdown("#### Candidate CV")
        sal_cv = st.text_area("Paste CV:", height=150, key="sal_cv", placeholder="Paste the candidate's CV...")
    
    sal_location = st.selectbox("Location/Market", [
        "US - National Average",
        "US - San Francisco/Bay Area",
        "US - New York City",
        "US - Seattle",
        "US - Austin",
        "US - Remote",
        "UK - London",
        "UK - National",
        "EU - Western Europe",
        "Canada",
        "Australia"
    ])
    
    if st.button("💰 Estimate Salary", type="primary", use_container_width=True):
        if sal_jd and sal_cv:
            with st.spinner("💰 Analyzing compensation factors..."):
                result, _ = estimate_salary(sal_cv, sal_jd, sal_location)
                
                if not result.startswith("Error"):
                    st.markdown("---")
                    
                    try:
                        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                        if json_match:
                            sal_data = json.loads(json_match.group(1))
                        else:
                            sal_data = json.loads(result)
                        
                        est = sal_data.get('estimated_range', {})
                        
                        st.markdown("### 💵 Estimated Salary Range")
                        
                        range_col1, range_col2, range_col3 = st.columns(3)
                        with range_col1:
                            st.markdown(f"""<div class="metric-card">
                                <p style="color:#9ca3af;margin:0;">Low</p>
                                <p style="color:#f59e0b;font-size:1.5rem;margin:0;">${est.get('low', 0):,}</p>
                            </div>""", unsafe_allow_html=True)
                        with range_col2:
                            st.markdown(f"""<div class="metric-card">
                                <p style="color:#9ca3af;margin:0;">Mid</p>
                                <p style="color:#10b981;font-size:1.5rem;margin:0;">${est.get('mid', 0):,}</p>
                            </div>""", unsafe_allow_html=True)
                        with range_col3:
                            st.markdown(f"""<div class="metric-card">
                                <p style="color:#9ca3af;margin:0;">High</p>
                                <p style="color:#6366f1;font-size:1.5rem;margin:0;">${est.get('high', 0):,}</p>
                            </div>""", unsafe_allow_html=True)
                        
                        st.markdown(f"**Confidence:** {sal_data.get('confidence', 'N/A')}")
                        
                        factor_col1, factor_col2 = st.columns(2)
                        with factor_col1:
                            st.markdown("**📈 Factors Increasing Salary:**")
                            for f in sal_data.get('factors_increasing_salary', []):
                                st.markdown(f"  ✅ {f}")
                        with factor_col2:
                            st.markdown("**📉 Factors Decreasing Salary:**")
                            for f in sal_data.get('factors_decreasing_salary', []):
                                st.markdown(f"  ⚠️ {f}")
                        
                        if sal_data.get('market_context'):
                            st.info(f"**Market Context:** {sal_data.get('market_context')}")
                        
                        if sal_data.get('negotiation_advice'):
                            st.success(f"**Negotiation Advice:** {sal_data.get('negotiation_advice')}")
                    
                    except:
                        st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
                else:
                    st.error(result)
        else:
            st.warning("Please provide both JD and CV")
