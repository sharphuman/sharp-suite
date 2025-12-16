"""Sharp Sales - AI Sales Call Analysis T(Enhanced v2)"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta, date
import secrets
import json
import re
import io
import tempfile
import sys

# Add parent directory for shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# ============================================
# SHARED MODULE IMPORTS
# ============================================
try:
    from shared_config import (
        SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY,
        ANTHROPIC_API_KEY, GOD_PASSWORD, APP_URLS, CLAUDE_MODEL
    )
    from shared_ui import (
        apply_global_styles,
        render_top_banner,
        render_header,
        render_sidebar,
        render_feedback_widget,
        COLORS
    )
    USING_SHARED = True
except ImportError:
    USING_SHARED = False
    SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
    GOD_PASSWORD = os.environ.get("GOD_PASSWORD", "G0DHum@n101!!!")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    APP_URLS = {"portal": "https://demo.sharphuman.com", "jd": "https://jd.sharphuman.com", "screen": "https://screen.sharphuman.com", "interview": "https://interview.sharphuman.com", "outreach": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com", "sales": "https://sales.sharphuman.com", "admin": "https://admin.sharphuman.com"}

# Try to import few-shot examples
try:
    from sales_examples import get_sales_few_shot_examples
    HAS_EXAMPLES = True
except ImportError:
    HAS_EXAMPLES = False
    def get_sales_few_shot_examples():
        return ""

# ============================================
# COACH PERSONAS
# ============================================
COACH_PERSONAS = {
    "supportive": {
        "name": "🤝 Supportive Coach",
        "description": "Encouraging, focuses on wins first (good for new reps)",
        "system_prompt": "You are a supportive, encouraging sales coach. Lead with what went well before discussing improvements. Frame all feedback constructively. Your goal is to build confidence while guiding growth."
    },
    "balanced": {
        "name": "⚖️ Balanced Coach",
        "description": "Equal focus on strengths and improvements",
        "system_prompt": "You are a balanced sales coach providing fair, thorough analysis. Cover both strengths and areas for improvement equally. Be direct but constructive."
    },
    "savage": {
        "name": "🔥 Savage Sales Manager",
        "description": "No sugarcoating - brutal honesty (for experienced reps)",
        "system_prompt": "You are a savage Sales Manager with over 20 years experience. You don't sugarcoat - you tell it like it is. Every weakness is a revenue leak. Be brutally honest because mediocrity costs deals."
    },
    "deal_closer": {
        "name": "💰 Deal Closer",
        "description": "Focuses on what killed/saved the deal",
        "system_prompt": "You are a deal-obsessed sales coach. Your ONLY focus is: did this call move the deal forward or backward? Analyze every moment through the lens of 'did this help close or hurt the close?' Ignore nice-to-haves."
    },
    "vp_sales": {
        "name": "👔 VP of Sales",
        "description": "Strategic view - patterns, process, scalability",
        "system_prompt": "You are a VP of Sales reviewing this call. Focus on strategic patterns: Is this rep following process? Are they coachable? What systemic issues need addressing? Think about how this rep's patterns affect the whole team."
    }
}

# ============================================
# RIGOR LEVELS
# ============================================
RIGOR_LEVELS = {
    "coaching": {
        "name": "🌱 Coaching Mode",
        "description": "Focus on 2-3 key improvements (less overwhelming)",
        "prompt_modifier": "Focus on the TOP 2-3 most impactful improvements. Don't overwhelm with minor issues. This is for coaching, not comprehensive audit."
    },
    "balanced": {
        "name": "⚖️ Full Analysis",
        "description": "Complete analysis of all areas",
        "prompt_modifier": "Provide a complete, thorough analysis of all areas. Be comprehensive but prioritize the most important findings."
    },
    "brutal": {
        "name": "🔥 Brutal Audit",
        "description": "Find EVERY weakness (for top performers)",
        "prompt_modifier": "This is a BRUTAL audit. Find EVERY weakness, missed opportunity, and suboptimal moment. Nothing is too small to mention. The rep wants to hear it ALL so they can fix it. Be ruthless."
    }
}

# ============================================
# FEEDBACK REASONS
# ============================================
FEEDBACK_REASONS = {
    "thumbs_down": [
        ("missed_moment", "Missed key moment in the call"),
        ("wrong_score", "Score doesn't match performance"),
        ("bad_advice", "Coaching advice was off"),
        ("missed_objection", "Missed an objection"),
        ("generic", "Too generic, not specific enough"),
        ("hallucination", "Made up something not in transcript"),
        ("other", "Other")
    ],
    "thumbs_up": [
        ("accurate", "Spot-on analysis"),
        ("actionable", "Great actionable advice"),
        ("caught_issue", "Caught something I missed"),
        ("good_scripts", "Helpful fix scripts"),
        ("other", "Other")
    ]
}

# ============================================
# CALL FRAMEWORKS - Added Interview Call
# ============================================
CALL_FRAMEWORKS = {
    "discovery": {"name": "🔍 Discovery Call", "stages": {
        "opening": {"name": "Opening", "weight": 15, "skills": ["Rapport Building", "Setting the Frame", "Permission to Proceed"]},
        "discovery": {"name": "Discovery", "weight": 40, "skills": ["Uncovering Pain & Goals", "Probing Questions", "Cost of Inaction", "Timeline & Urgency", "Budget Discovery"]},
        "qualify": {"name": "Qualification", "weight": 20, "skills": ["Decision Authority", "Buying Process", "Competitive Landscape"]},
        "close": {"name": "Close", "weight": 25, "skills": ["Summary & Recap", "Clear Next Steps", "Getting Commitment", "Multi-threading"]}
    }},
    "interview_call": {"name": "🎯 Interview Call (Cold Outreach)", "stages": {
        "hook": {"name": "Hook & Permission", "weight": 20, "skills": ["Pattern Interrupt", "Value-First Hook", "Permission to Continue", "Credibility Statement"]},
        "interview": {"name": "Interview/Research Phase", "weight": 35, "skills": ["Industry Questions", "Challenge Discovery", "Active Listening", "Building Curiosity", "Seeding Pain"]},
        "transition": {"name": "Transition to Discovery", "weight": 25, "skills": ["Bridge Statement", "Value Teaser", "Creating Urgency", "Permission to Go Deeper"]},
        "close": {"name": "Close to Meeting", "weight": 20, "skills": ["Direct Ask", "Handling Brush-offs", "Calendar Commitment", "Confirming Next Steps"]}
    }},
    "demo": {"name": "🖥️ Demo/Presentation", "stages": {
        "setup": {"name": "Setup", "weight": 15, "skills": ["Discovery Recap", "Demo Agenda", "Attendee Check"]},
        "demo": {"name": "Demonstration", "weight": 40, "skills": ["Tailored Demo", "Storytelling", "Audience Engagement", "Objection Handling"]},
        "value": {"name": "Value", "weight": 20, "skills": ["ROI Discussion", "Differentiation", "Social Proof"]},
        "close": {"name": "Close", "weight": 25, "skills": ["Temperature Check", "Surfacing Concerns", "Next Steps"]}
    }},
    "proposal": {"name": "📋 Proposal Call", "stages": {
        "review": {"name": "Proposal Review", "weight": 30, "skills": ["Proposal Walkthrough", "Pricing Presentation", "Value Justification", "Addressing Questions"]},
        "concerns": {"name": "Concerns", "weight": 35, "skills": ["Objection Handling", "Risk Mitigation", "Competitor Comparison", "Stakeholder Concerns"]},
        "close": {"name": "Close", "weight": 35, "skills": ["Decision Timeline", "Next Steps", "Verbal Commitment", "Contract Process"]}
    }},
    "negotiation": {"name": "🤝 Negotiation Call", "stages": {
        "review": {"name": "Review", "weight": 20, "skills": ["Proposal Recap", "Value Reinforcement"]},
        "negotiate": {"name": "Negotiation", "weight": 50, "skills": ["Listening to Concerns", "Trading Value", "Anchoring", "Creative Solutions"]},
        "close": {"name": "Close", "weight": 30, "skills": ["Asking for Close", "Final Objections", "Paperwork Process"]}
    }},
    "customer_interview": {"name": "📞 Customer Interview", "stages": {
        "intro": {"name": "Introduction", "weight": 15, "skills": ["Rapport Building", "Setting Context", "Permission & Recording"]},
        "discovery": {"name": "Discovery", "weight": 50, "skills": ["Open-Ended Questions", "Active Listening", "Follow-up Probes", "Capturing Insights", "Pain Point Exploration"]},
        "close": {"name": "Wrap-Up", "weight": 35, "skills": ["Summary of Key Points", "Additional Questions", "Next Steps", "Thank You & Follow-up"]}
    }},
    "follow_up": {"name": "🔄 Follow-Up Call", "stages": {
        "reconnect": {"name": "Reconnect", "weight": 25, "skills": ["Context Reset", "Situation Changes", "Value Reminder"]},
        "advance": {"name": "Advance", "weight": 50, "skills": ["Address Objections", "New Information", "Creating Urgency"]},
        "commit": {"name": "Commitment", "weight": 25, "skills": ["Micro-Commitment", "Book Next Meeting", "Action Items"]}
    }}
}

# ============================================
# EMAIL TONE OPTIONS
# ============================================
EMAIL_TONES = {
    "friendly": {
        "name": "😊 Friendly",
        "description": "Warm, personable, relationship-focused",
        "prompt": "Write in a warm, friendly tone. Focus on building relationship. Use casual but professional language."
    },
    "professional": {
        "name": "💼 Professional",
        "description": "Balanced, business-appropriate",
        "prompt": "Write in a professional, balanced tone. Direct but courteous. Standard business communication."
    },
    "assertive": {
        "name": "🎯 Assertive",
        "description": "Direct, confident, action-oriented",
        "prompt": "Write in an assertive, confident tone. Be direct about value and next steps. Create urgency without being pushy."
    }
}

TRIAL_LIMITS = {"sales": 5}


def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try: requests.post(f"{SUPABASE_URL}/rest/v1/sessions", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "sales", "is_active": True, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()}, timeout=10)
    except: pass
    return token


def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            user = data.get("user", {})
            return {"success": True, "user": user, "session_token": create_session(user.get("id"), email)}
        return {"success": False, "message": data.get("error_description") or "Invalid"}
    except Exception as e: return {"success": False, "message": str(e)}


def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        return {"success": True, "message": "Check email!"} if r.status_code == 200 and data.get("user") else {"success": False, "message": data.get("error_description") or "Failed"}
    except Exception as e: return {"success": False, "message": str(e)}


def validate_session_token(token):
    if not token: return None
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        if r.status_code == 200 and r.json():
            session = r.json()[0]
            expires = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
            if expires.replace(tzinfo=None) > datetime.utcnow():
                ur = requests.get(f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
                if ur.status_code == 200 and ur.json():
                    p = ur.json()[0]
                    return {"user_id": session["user_id"], "email": p.get("email"), "plan": p.get("plan", "free"), "token": token}
    except: pass
    return None


def log_usage(user_id, session_id, app, action, tokens_used=0):
    try: requests.post(f"{SUPABASE_URL}/rest/v1/usage_logs", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": user_id, "session_id": session_id, "app": app, "action": action, "tokens_used": tokens_used}, timeout=5)
    except: pass


def check_trial_limit(app_name, limit=5):
    user_id = st.session_state.get("user", {}).get("id")
    plan = st.session_state.get("user_plan", "free")
    if plan not in ["trial", "7_day_trial", "7-day-trial", "free_trial"]: return True, 0, limit
    if not user_id: return True, 0, limit
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/usage_logs?user_id=eq.{user_id}&app=eq.{app_name}&action=eq.analyze", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        usage = len(r.json()) if r.status_code == 200 else 0
        return usage < limit, usage, limit
    except: return True, 0, limit


def submit_feedback(app, ft, message):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/feedback", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"app": app, "feedback_type": ft, "message": message, "user_id": st.session_state.get("user", {}).get("id")}, timeout=10)
        return True
    except: return False


def submit_analysis_feedback(analysis_result, feedback_type, reason=None, comment=None):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/analysis_feedback", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={
            "app": "sales", "feedback_type": feedback_type, "reason": reason, "comment": comment,
            "analysis_score": analysis_result.get("overall_score"), "user_id": st.session_state.get("user", {}).get("id")
        }, timeout=10)
        return True
    except: return False


def get_user_email():
    user = st.session_state.get("user", {})
    return user.get("email", "User") if isinstance(user, dict) else "User"


def build_app_url(app_key):
    base = APP_URLS.get(app_key, f"https://{app_key}.sharphuman.com")
    token = st.session_state.get("session_token", "")
    return f"{base}?token={token}" if token else base


def init_session():
    defaults = [
        ('authenticated', False), ('user', None), ('session_token', ''), ('is_god', False),
        ('user_plan', 'free'), ('working_on', None), ('analysis_result', None), 
        ('feedback_given', False), ('show_feedback_reason', False),
        ('bd_result', None), ('followup_email', None)
    ]
    for k, v in defaults:
        if k not in st.session_state: st.session_state[k] = v


def check_url_auth():
    if st.session_state.authenticated: return
    token = st.query_params.get("token")
    if token:
        result = validate_session_token(token)
        if result:
            st.session_state.authenticated = True
            st.session_state.user = {"id": result["user_id"], "email": result["email"]}
            st.session_state.session_token = result["token"]
            st.session_state.user_plan = result.get("plan", "free")


def extract_text_from_file(uploaded_file):
    """Extract text from various file formats."""
    try:
        name = uploaded_file.name.lower()
        content = uploaded_file.read()
        
        if name.endswith('.txt'):
            return content.decode('utf-8', errors='ignore')
        
        elif name.endswith('.vtt') or name.endswith('.srt'):
            text = content.decode('utf-8', errors='ignore')
            lines = []
            for line in text.split('\n'):
                line = line.strip()
                if not line: continue
                if '-->' in line: continue
                if line.isdigit(): continue
                if line.startswith('WEBVTT'): continue
                if line.startswith('NOTE'): continue
                lines.append(re.sub(r'<[^>]+>', '', line))
            return ' '.join(lines)
        
        elif name.endswith('.pdf'):
            try:
                import fitz
                pdf = fitz.open(stream=content, filetype="pdf")
                return "\n".join([page.get_text() for page in pdf])
            except: return "[PDF extraction failed - install PyMuPDF]"
        
        elif name.endswith(('.docx', '.doc')):
            try:
                from docx import Document
                doc = Document(io.BytesIO(content))
                return "\n".join([p.text for p in doc.paragraphs])
            except: return "[DOCX extraction failed - install python-docx]"
        
        elif name.endswith(('.mp3', '.wav', '.m4a', '.mp4', '.webm')):
            return "[Audio/video transcription not yet implemented - paste transcript instead]"
        
        return content.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"[Error extracting text: {e}]"


def export_to_pdf(analysis, title="Sales Call Analysis"):
    """Generate a PDF report from analysis results."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=20)
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Score
        score = analysis.get('overall_score', 0)
        story.append(Paragraph(f"<b>Overall Score: {score}/100</b>", styles['Heading2']))
        story.append(Paragraph(analysis.get('overall_summary', ''), styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Key Wins
        story.append(Paragraph("<b>Key Wins</b>", styles['Heading3']))
        for w in analysis.get('key_wins', []):
            story.append(Paragraph(f"• {w}", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Improvements
        story.append(Paragraph("<b>Critical Improvements</b>", styles['Heading3']))
        for i in analysis.get('critical_improvements', []):
            story.append(Paragraph(f"• {i}", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Coaching Summary
        story.append(Paragraph("<b>Coaching Summary</b>", styles['Heading3']))
        story.append(Paragraph(analysis.get('coaching_summary', ''), styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        return None


def call_claude(prompt, max_tokens=4000, action="analyze"):
    """Call Claude API for analysis."""
    try:
        api_key = ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "Error: No API key configured", 0
        
        model = CLAUDE_MODEL if USING_SHARED else "claude-sonnet-4-20250514"
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("content", [{}])[0].get("text", "")
            tokens = data.get("usage", {}).get("output_tokens", 0)
            log_usage(st.session_state.get("user", {}).get("id"), st.session_state.get("session_token"), "sales", action, tokens)
            return result, tokens
        else:
            return f"Error: API returned {response.status_code}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0


def analyze_call(transcript, call_type, prospect_name, company, deal_size, stage, notes, persona, rigor, concerns, your_website="", lead_website="", lead_linkedin=""):
    """Analyze a sales call with all context."""
    framework = CALL_FRAMEWORKS.get(call_type, CALL_FRAMEWORKS["discovery"])
    persona_config = COACH_PERSONAS.get(persona, COACH_PERSONAS["balanced"])
    rigor_config = RIGOR_LEVELS.get(rigor, RIGOR_LEVELS["balanced"])
    
    few_shot = get_sales_few_shot_examples() if HAS_EXAMPLES else ""
    
    # Build context section
    context_parts = []
    if your_website:
        context_parts.append(f"Seller's Website: {your_website} (use this to understand their value proposition)")
    if lead_website:
        context_parts.append(f"Lead's Website: {lead_website}")
    if lead_linkedin:
        context_parts.append(f"Lead's LinkedIn: {lead_linkedin}")
    
    context_section = "\n".join(context_parts) if context_parts else ""
    
    prompt = f"""{persona_config['system_prompt']}

{rigor_config['prompt_modifier']}

You are analyzing a {framework['name']} for {prospect_name or 'the prospect'} at {company or 'their company'}.
Deal Size: {deal_size or 'Unknown'}
Current Stage: {stage}
{f"Additional Context: {notes}" if notes else ""}
{context_section}

{f"## SPECIFIC CONCERNS TO ADDRESS:{chr(10)}The user specifically wants you to analyze: {concerns}{chr(10)}Make sure to directly address these concerns in your analysis." if concerns else ""}

## FRAMEWORK: {framework['name']}
Stages and weights:
{json.dumps(framework['stages'], indent=2)}

{few_shot}

## TRANSCRIPT TO ANALYZE:
{transcript[:20000]}

---

Analyze this call and return JSON:
```json
{{
    "overall_score": <0-100>,
    "overall_summary": "<2-3 sentence executive summary>",
    "persona": "{persona}",
    "rigor": "{rigor}",
    "stages": [
        {{
            "stage_name": "<stage>",
            "stage_score": <0-10>,
            "skills": [
                {{
                    "skill_name": "<skill>",
                    "score": <0-10>,
                    "what_worked": ["<specific example with timestamp>"],
                    "what_needed_improvement": ["<specific issue with timestamp>"],
                    "transcript_evidence": ["<exact quote>"],
                    "improvement": "<specific actionable fix>"
                }}
            ]
        }}
    ],
    "objections_breakdown": [
        {{
            "objection": "<what prospect said>",
            "timestamp": "<[MM:SS] or approximate location>",
            "pre_handled": <true if rep anticipated it>,
            "post_handled": <true if rep addressed it after>,
            "effectiveness_score": <0-10>,
            "what_worked": "<what the rep did well>",
            "what_needed_improvement": "<what could be better>",
            "fix_for_next_call": "<exact script to use next time>"
        }}
    ],
    {f'"concerns_addressed": [{{"concern": "{concerns}", "finding": "<direct answer to their concern>", "evidence": "<quote or observation from transcript>"}}],' if concerns else ''}
    "key_wins": ["<something done well with timestamp>", "<another strength>"],
    "critical_improvements": ["<most important fix>", "<second priority>"],
    "deal_insights": {{
        "buying_signals": ["<signal identified with quote>"],
        "red_flags": ["<concern with evidence>"],
        "next_steps_suggested": ["<recommended action>"],
        "deal_probability": "<High|Medium|Low>",
        "deal_probability_reasoning": "<why>"
    }},
    "final_takeaways": {{
        "biggest_strength": "<the rep's best quality on this call>",
        "biggest_weakness": "<the most impactful thing to fix>",
        "game_changer_for_next_call": "<the ONE thing that would most improve results>"
    }},
    "coaching_summary": "<paragraph of personalized coaching advice>"
}}
```

Be specific. Use exact quotes with timestamps. Be constructive but honest."""

    return call_claude(prompt, 8000, f"analyze_{call_type}")


def analyze_recruiting_bd_call(transcript, call_type="cold_outreach", company="", title="", services=None, concerns="", your_website="", lead_website="", lead_linkedin=""):
    """Analyze a recruiting BD call - selling recruiting services to clients."""
    services = services or ["Permanent"]
    
    # Build context section
    context_parts = []
    if your_website:
        context_parts.append(f"Your Agency Website: {your_website} (use this to understand your value proposition and differentiators)")
    if lead_website:
        context_parts.append(f"Prospect's Company Website: {lead_website}")
    if lead_linkedin:
        context_parts.append(f"Prospect's LinkedIn: {lead_linkedin}")
    
    context_section = "\n".join(context_parts) if context_parts else ""
    
    prompt = f"""You are an expert recruiting sales trainer analyzing a business development call.

CALL: {call_type.replace('_',' ').title()} | Prospect: {title} at {company} | Services: {', '.join(services)}
{context_section}

{f"## SPECIFIC CONCERNS TO ADDRESS:{chr(10)}The user specifically wants you to analyze: {concerns}{chr(10)}Make sure to directly address these concerns in your analysis with specific evidence." if concerns else ""}

EVALUATE THESE BD SKILLS:
1. Opening & Permission (10%) - Earned right to continue? Value hook? Research shown?
2. Hiring Pain Discovery (25%) - Open roles? Time-to-fill? Cost of vacancy? Current methods failing?
3. Value Proposition (20%) - vs internal TA? vs other agencies? Success stories? Unique approach?
4. Objection Handling (20%) - WATCH FOR: "fees too high", "use internal recruiters", "already have agency", "send candidates first", "not hiring now"
5. Fee Discussion (15%) - Held fee or caved? Justified with value? Contingent/retained/exclusive positioning?
6. Close & Next Steps (10%) - Got commitment? Job order taken? Meeting scheduled? Clear follow-up?

TRANSCRIPT:
{transcript[:18000]}

Return JSON:
```json
{{
    "overall_score": <0-100>,
    "overall_summary": "<2-3 sentences>",
    "skills": [
        {{
            "skill_name": "<skill name>",
            "score": <0-10>,
            "what_worked": ["<specific example>"],
            "what_needed_improvement": ["<specific issue>"],
            "transcript_evidence": ["<exact quote>"],
            "fix_for_next_call": "<exact script to use>"
        }}
    ],
    "objections_breakdown": [
        {{
            "objection": "<what they said>",
            "timestamp": "<[MM:SS] or location>",
            "pre_handled": <bool>,
            "post_handled": <bool>,
            "effectiveness_score": <0-10>,
            "what_worked": "<text>",
            "what_needed_improvement": "<text>",
            "fix_for_next_call": "<script>"
        }}
    ],
    {f'"concerns_addressed": [{{"concern": "{concerns}", "finding": "<direct answer>", "evidence": "<quote from transcript>"}}],' if concerns else ''}
    "strengths": ["<strength with evidence>"],
    "priority_improvements": ["<improvement needed>"],
    "deal_outcome": {{
        "likely_outcome": "<Won|Pending|Lost|Unknown>",
        "fee_discussed": "<what was agreed or discussed>",
        "exclusivity": "<Exclusive|Contingent|Retained|Not discussed>",
        "next_steps_agreed": ["<specific next step>"]
    }},
    "coaching_summary": "<paragraph of specific coaching advice>"
}}
```"""
    return call_claude(prompt, 6000, "recruiting_bd")


def generate_followup_email(analysis, tone="professional", custom_prompt="", mode="general"):
    """Generate a follow-up email based on call analysis."""
    tone_config = EMAIL_TONES.get(tone, EMAIL_TONES["professional"])
    
    # Extract key info from analysis
    if mode == "bd":
        deal_outcome = analysis.get("deal_outcome", {})
        next_steps = deal_outcome.get("next_steps_agreed", [])
        context = f"""
Call Outcome: {deal_outcome.get('likely_outcome', 'Unknown')}
Fee Discussed: {deal_outcome.get('fee_discussed', 'Not discussed')}
Next Steps Agreed: {', '.join(next_steps) if next_steps else 'None specified'}
"""
    else:
        insights = analysis.get("deal_insights", {})
        next_steps = insights.get("next_steps_suggested", [])
        context = f"""
Deal Probability: {insights.get('deal_probability', 'Unknown')}
Buying Signals: {', '.join(insights.get('buying_signals', [])[:3])}
Next Steps: {', '.join(next_steps[:3]) if next_steps else 'None specified'}
"""

    prompt = f"""Write a follow-up email based on this sales call analysis.

TONE: {tone_config['prompt']}

CALL SUMMARY:
Overall Score: {analysis.get('overall_score', 'N/A')}/100
{analysis.get('overall_summary', '')}

{context}

Key Wins from Call: {', '.join(analysis.get('key_wins', analysis.get('strengths', []))[:3])}

{f"SPECIFIC REQUEST: {custom_prompt}" if custom_prompt else ""}

Write a concise, effective follow-up email that:
1. References something specific from the conversation
2. Reinforces the value discussed
3. Proposes clear next steps
4. Matches the requested tone

Return ONLY the email (no explanation):
Subject: <subject line>

<email body>"""

    result, _ = call_claude(prompt, 1500, "followup_email")
    return result


# ============================================
# STREAMLIT APP
# ============================================
st.set_page_config(page_title="Sharp Sales", page_icon="💰", layout="wide")
init_session()
check_url_auth()

# CSS with Material Icons fix
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
*, *::before, *::after { font-family: 'Nunito', sans-serif !important; }
.stApp, [data-testid="stAppViewContainer"] { background: #1a1a1a !important; }
[data-testid="stHeader"] { background: transparent !important; }
section[data-testid="stSidebar"] { background: #1a1a1a !important; border-right: 1px solid rgba(255,255,255,0.1); }
section[data-testid="stSidebar"] > div { background: #1a1a1a !important; }
section[data-testid="stSidebar"] * { color: #e5e5e5 !important; }
section[data-testid="stSidebar"] > div > div:first-child > div:first-child { display: none !important; }
h1,h2,h3,h4,h5,h6 { color: #fff !important; }
p,span,label,div,li { color: #e5e5e5; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div, [data-baseweb="select"] > div { background: #2a2a2a !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #fff !important; border-radius: 8px !important; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stDownloadButton > button { background: #2a2a2a !important; border: 1px solid rgba(255,255,255,0.1) !important; }
.stRadio > div { flex-direction: row !important; gap: 8px; flex-wrap: wrap; }
.stRadio > div > label { background: #2a2a2a !important; padding: 10px 16px !important; border-radius: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
[data-testid="stFileUploader"] { background: #2a2a2a !important; border: 1px dashed rgba(255,255,255,0.2) !important; border-radius: 8px !important; }
.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.input-section { background: #2a2a2a; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; margin: 12px 0; }
.transcript-quote { background: #333; border-left: 3px solid #6366f1; padding: 12px 16px; margin: 8px 0; border-radius: 0 8px 8px 0; font-style: italic; color: #a5b4fc; }
.improvement-box { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 16px; margin-top: 12px; }
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 12px 24px 12px 50px; border-radius: 25px; font-weight: 600; z-index: 9999; box-shadow: 0 4px 15px rgba(99,102,241,0.4); }
.status-badge::before { content: ''; position: absolute; left: 12px; top: 50%; transform: translateY(-50%); width: 28px; height: 28px; background: url('https://assets.sharphuman.com/logo_spinner_small.gif') center/contain no-repeat; }
div[data-testid="stPopover"] button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 25px !important; }
/* Fix Material Icons in expanders */
.material-icons { font-family: 'Material Icons' !important; }
[data-testid="stExpander"] summary span { font-family: 'Nunito', sans-serif !important; }
</style>""", unsafe_allow_html=True)

# Auth
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="margin:0;">Sharp Sales</h1><p style="color:#9ca3af;">AI Sales Call Analysis</p></div>""", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Log In", "Sign Up"])
        with t1:
            email, pwd = st.text_input("Email", key="l_email"), st.text_input("Password", type="password", key="l_pwd")
            if st.button("Log In", use_container_width=True):
                if pwd == GOD_PASSWORD:
                    st.session_state.authenticated, st.session_state.is_god, st.session_state.user = True, True, {"email": "GOD", "id": "god"}
                    st.session_state.session_token = secrets.token_urlsafe(32)
                    st.rerun()
                elif email and pwd:
                    r = supabase_sign_in(email, pwd)
                    if r["success"]: st.session_state.authenticated, st.session_state.user, st.session_state.session_token = True, r["user"], r.get("session_token"); st.rerun()
                    else: st.error(r["message"])
        with t2:
            s_email, s_pwd, s_conf = st.text_input("Email", key="s_email"), st.text_input("Password", type="password", key="s_pwd"), st.text_input("Confirm", type="password", key="s_conf")
            if st.button("Create Account", use_container_width=True):
                if s_pwd != s_conf: st.error("Passwords don't match")
                elif len(s_pwd) < 6: st.warning("6+ characters")
                elif s_email and s_pwd:
                    r = supabase_sign_up(s_email, s_pwd)
                    st.success(r["message"]) if r["success"] else st.error(r["message"])
    st.stop()

if st.session_state.working_on: st.markdown(f'<div class="status-badge">{st.session_state.working_on}</div>', unsafe_allow_html=True)

# Use shared_ui sidebar and top banner
if USING_SHARED:
    render_top_banner(show_cta=True, cta_text="Book a Demo")
    render_sidebar(
        current_app="sales",
        user_email=get_user_email(),
        user_plan=st.session_state.get('user_plan', 'free'),
        session_token=st.session_state.get('session_token', '')
    )
else:
    # Fallback sidebar
    with st.sidebar:
        st.markdown(f"""<div class="user-card"><p style="color:#9ca3af;margin:0;font-size:12px;">Logged in as</p><p style="color:#fff;margin:4px 0;font-weight:600;">{get_user_email()}</p><p style="color:#6366f1;margin:0;font-size:12px;text-transform:uppercase;">{st.session_state.get('user_plan','free')} plan</p></div>""", unsafe_allow_html=True)
        st.markdown("**Apps**")
        for key, label in [("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"), ("interview", "🎯 Interview"), ("outreach", "🚀 Outreach"), ("content", "✍️ Content"), ("sales", "💰 Sales")]:
            if key == "sales": st.markdown(f"<div style='background:#db2777;padding:10px 16px;border-radius:8px;text-align:center;margin:4px 0;color:white;font-weight:600;'>{label} ◀</div>", unsafe_allow_html=True)
            else: st.link_button(label, build_app_url(key), use_container_width=True)
        if st.session_state.get("is_god"): st.markdown("---"); st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:20px;"><img src="https://sharphuman.com/logo1-3.png" style="width:50px;"><div><h1 style="margin:0;font-size:28px;">Sharp Sales</h1><p style="color:#9ca3af;margin:0;">AI-Powered Sales Call Analysis</p></div></div>""", unsafe_allow_html=True)

# Mode Selector - Updated name
mode_cols = st.columns([1, 2, 1])
with mode_cols[1]:
    sales_mode = st.segmented_control("Mode", ["💼 General Sales", "👔 Recruiting Business Development"], default="💼 General Sales", label_visibility="collapsed")

st.markdown("---")

# Initialize states
if 'bd_result' not in st.session_state:
    st.session_state.bd_result = None
if 'followup_email' not in st.session_state:
    st.session_state.followup_email = None

# ===== RECRUITING BUSINESS DEVELOPMENT MODE =====
if sales_mode == "👔 Recruiting Business Development":
    st.markdown("### 👔 Recruiting Business Development")
    st.caption("Analyze your client acquisition calls - selling recruiting services to prospects")
    
    if st.session_state.bd_result:
        if st.button("← Analyze Another Call"):
            st.session_state.bd_result = None
            st.session_state.followup_email = None
            st.rerun()
        try:
            m = re.search(r'```json\s*(.*?)\s*```', st.session_state.bd_result, re.DOTALL)
            a = json.loads(m.group(1) if m else st.session_state.bd_result)
            score = a.get('overall_score', 0)
            color = "#10b981" if score >= 70 else "#eab308" if score >= 50 else "#ef4444"
            st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border-radius:16px;padding:30px;text-align:center;margin:20px 0;">
                <span style="background:rgba(219,39,119,0.2);color:#f472b6;padding:4px 12px;border-radius:12px;font-size:12px;">Recruiting BD</span>
                <p style="color:#9ca3af;margin:12px 0 0;">YOUR PERFORMANCE</p>
                <p style="color:{color};font-size:64px;font-weight:bold;margin:10px 0;">{score}<span style="font-size:24px;color:#6b7280;">/100</span></p>
                <p style="color:#e5e5e5;">{a.get('overall_summary', '')}</p>
            </div>""", unsafe_allow_html=True)
            
            # Concerns Addressed Section
            concerns_addressed = a.get('concerns_addressed', [])
            if concerns_addressed:
                st.markdown("### 🎯 Your Concerns Addressed")
                for c in concerns_addressed:
                    st.markdown(f"""<div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);border-radius:12px;padding:16px;margin:12px 0;">
                        <p style="color:#a5b4fc;font-weight:600;margin:0 0 8px;">❓ {c.get('concern', '')}</p>
                        <p style="color:#e5e5e5;margin:0 0 8px;">💡 {c.get('finding', '')}</p>
                        <p style="color:#9ca3af;font-style:italic;margin:0;">📍 "{c.get('evidence', '')}"</p>
                    </div>""", unsafe_allow_html=True)
                st.markdown("---")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 💪 Strengths")
                for s in a.get('strengths', []): st.success(s)
            with c2:
                st.markdown("#### 🎯 Improvements")
                for i in a.get('priority_improvements', []): st.warning(i)
            
            st.markdown("---")
            st.markdown("### 📊 Skills Breakdown")
            for skill in a.get('skills', []):
                with st.expander(f"**{skill.get('skill_name')}** — {skill.get('score', 0)}/10"):
                    for w in skill.get('what_worked', []): st.markdown(f"✅ {w}")
                    for w in skill.get('what_needed_improvement', []): st.markdown(f"❌ {w}")
                    if skill.get('fix_for_next_call'): st.info(f"⚡ {skill.get('fix_for_next_call')}")
            
            objections = a.get('objections_breakdown', [])
            if objections:
                st.markdown("---")
                st.markdown("### 🛡️ Objection Handling")
                for i, obj in enumerate(objections, 1):
                    with st.expander(f"Objection {i}: {obj.get('objection', '')[:50]}... ({obj.get('effectiveness_score', 0)}/10)"):
                        st.markdown(f"Pre: {'✅' if obj.get('pre_handled') else '❌'} | Post: {'✅' if obj.get('post_handled') else '❌'}")
                        if obj.get('fix_for_next_call'): st.info(f"⚡ {obj.get('fix_for_next_call')}")
            
            deal = a.get('deal_outcome', {})
            if deal:
                st.markdown("---")
                st.markdown("### 🎯 Deal Outcome")
                dc1, dc2, dc3 = st.columns(3)
                with dc1: st.metric("Outcome", deal.get('likely_outcome', '?'))
                with dc2: st.metric("Fee", str(deal.get('fee_discussed', 'N/A'))[:15])
                with dc3: st.metric("Exclusivity", deal.get('exclusivity', 'N/A'))
            
            st.markdown("---")
            st.markdown(f"### 🎓 Coaching Summary\n{a.get('coaching_summary', '')}")
            
            # Follow-up Email Generator
            st.markdown("---")
            st.markdown("### 📧 Follow-up Email Generator")
            
            fe_col1, fe_col2 = st.columns([2, 1])
            with fe_col1:
                email_prompt = st.text_area("What do you want to achieve with this email?", placeholder="e.g., 'Confirm the job order details and fee agreement' or 'Re-engage after they went quiet'", height=80)
            with fe_col2:
                email_tone = st.selectbox("Tone:", options=list(EMAIL_TONES.keys()), format_func=lambda x: EMAIL_TONES[x]['name'])
            
            if st.button("✉️ Generate Follow-up Email", use_container_width=True):
                with st.spinner("Generating email..."):
                    st.session_state.followup_email = generate_followup_email(a, email_tone, email_prompt, mode="bd")
            
            if st.session_state.followup_email:
                st.markdown("#### Generated Email:")
                st.code(st.session_state.followup_email, language=None)
                st.download_button("📥 Copy Email", st.session_state.followup_email, "followup_email.txt", use_container_width=True)
            
            st.markdown("---")
            st.download_button("📥 Download Full Analysis", st.session_state.bd_result, "bd_analysis.json", use_container_width=True)
        
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        # BD Input Form - Upload as default
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown("**Call Details**")
            bd_type = st.selectbox("Call Type", ["cold_outreach", "warm_intro", "inbound_lead", "referral", "follow_up"],
                format_func=lambda x: {"cold_outreach": "❄️ Cold Outreach", "warm_intro": "🤝 Warm Introduction", "inbound_lead": "📥 Inbound Lead", "referral": "🔗 Referral", "follow_up": "🔄 Follow-up"}.get(x, x))
            
            bd_co = st.text_input("Prospect Company", placeholder="Acme Corp")
            bd_title = st.text_input("Prospect Title", placeholder="VP of Engineering")
            bd_svc = st.multiselect("Services Discussed", ["Permanent Placement", "Contract Staffing", "Executive Search", "RPO"], default=["Permanent Placement"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown("**Context (Optional)**")
            bd_your_website = st.text_input("Your Agency Website", placeholder="https://yourrecruiting.com - we'll analyze your value prop")
            bd_lead_website = st.text_input("Prospect's Website", placeholder="https://acmecorp.com")
            bd_lead_linkedin = st.text_input("Prospect's LinkedIn", placeholder="https://linkedin.com/in/prospect")
            bd_concerns = st.text_area("Specific concerns to analyze", height=68, placeholder="e.g., 'Did I handle the fee objection well?' or 'Was my value prop clear?'")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown("**Call Recording / Transcript**")
            # Upload as default
            bd_in = st.radio("Input Method", ["📁 Upload File", "📝 Paste Transcript"], horizontal=True)
            bd_txt = ""
            if bd_in == "📁 Upload File":
                f = st.file_uploader("Upload recording or transcript", type=['txt', 'pdf', 'docx', 'vtt', 'srt'], key="bd_f", help="Supports: TXT, PDF, DOCX, VTT, SRT")
                if f:
                    bd_txt = extract_text_from_file(f)
                    if bd_txt and not bd_txt.startswith("["): st.success(f"✅ {len(bd_txt):,} characters loaded")
            else:
                bd_txt = st.text_area("Paste transcript", height=280, placeholder="You: Hi Sarah, thanks for taking my call...", key="bd_t")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("👔 Analyze BD Call", type="primary", use_container_width=True):
            if len(bd_txt.strip()) < 100: st.warning("Transcript too short (min 100 characters)")
            else:
                st.session_state.working_on = "Analyzing BD call..."
                st.rerun()
    
    # Handle BD analysis (after rerun with working_on set)
    if st.session_state.working_on == "Analyzing BD call...":
        # Get form values from session or re-collect
        with st.spinner("🔄 Analyzing your call... 20-40 seconds"):
            bd_txt = st.session_state.get('_bd_txt', '')
            if not bd_txt:
                st.session_state.working_on = None
                st.rerun()
            r, _ = analyze_recruiting_bd_call(
                bd_txt, 
                st.session_state.get('_bd_type', 'cold_outreach'),
                st.session_state.get('_bd_co', ''),
                st.session_state.get('_bd_title', ''),
                st.session_state.get('_bd_svc', ['Permanent']),
                st.session_state.get('_bd_concerns', ''),
                st.session_state.get('_bd_your_website', ''),
                st.session_state.get('_bd_lead_website', ''),
                st.session_state.get('_bd_lead_linkedin', '')
            )
        st.session_state.working_on = None
        if not str(r).startswith("Error"):
            st.session_state.bd_result = r
            st.rerun()
        else: 
            st.error(r)

# ===== GENERAL SALES MODE =====
elif st.session_state.get('analysis_result'):
    # Results View
    if st.button("← New Analysis", type="secondary"):
        st.session_state.analysis_result = None
        st.session_state.followup_email = None
        st.rerun()
    
    try:
        txt = st.session_state.analysis_result
        m = re.search(r'```json\s*(.*?)\s*```', txt, re.DOTALL)
        a = json.loads(m.group(1) if m else txt)
        
        score = a.get('overall_score', 0)
        color = "#10b981" if score >= 70 else "#eab308" if score >= 50 else "#ef4444"
        
        # Show persona/rigor badges
        persona_name = COACH_PERSONAS.get(a.get('persona', 'balanced'), {}).get('name', '')
        rigor_name = RIGOR_LEVELS.get(a.get('rigor', 'balanced'), {}).get('name', '')
        
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border-radius:16px;padding:30px;text-align:center;margin-bottom:24px;">
            <div style="margin-bottom:12px;">
                <span style="background:rgba(99,102,241,0.2);color:#a5b4fc;padding:4px 12px;border-radius:12px;font-size:12px;margin:4px;">{persona_name}</span>
                <span style="background:rgba(139,92,246,0.2);color:#c4b5fd;padding:4px 12px;border-radius:12px;font-size:12px;margin:4px;">{rigor_name}</span>
            </div>
            <p style="color:#9ca3af;margin:0;">OVERALL SCORE</p>
            <p style="color:{color};font-size:64px;font-weight:bold;margin:10px 0;">{score}<span style="font-size:24px;color:#6b7280;">/100</span></p>
            <p style="color:#e5e5e5;">{a.get('overall_summary', '')}</p>
        </div>""", unsafe_allow_html=True)
        
        # Concerns Addressed Section
        concerns_addressed = a.get('concerns_addressed', [])
        if concerns_addressed:
            st.markdown("### 🎯 Your Concerns Addressed")
            for c in concerns_addressed:
                st.markdown(f"""<div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);border-radius:12px;padding:16px;margin:12px 0;">
                    <p style="color:#a5b4fc;font-weight:600;margin:0 0 8px;">❓ {c.get('concern', '')}</p>
                    <p style="color:#e5e5e5;margin:0 0 8px;">💡 {c.get('finding', '')}</p>
                    <p style="color:#9ca3af;font-style:italic;margin:0;">📍 "{c.get('evidence', '')}"</p>
                </div>""", unsafe_allow_html=True)
            st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ✅ Key Wins")
            for w in a.get('key_wins', []): st.markdown(f"<div style='background:rgba(16,185,129,0.1);border-left:3px solid #10b981;padding:12px;margin:8px 0;border-radius:0 8px 8px 0;'>{w}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("#### 🎯 Critical Improvements")
            for i in a.get('critical_improvements', []): st.markdown(f"<div style='background:rgba(239,68,68,0.1);border-left:3px solid #ef4444;padding:12px;margin:8px 0;border-radius:0 8px 8px 0;'>{i}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("## 📈 Stage Analysis")
        
        for stg in a.get('stages', []):
            with st.expander(f"**{stg.get('stage_name')}** — {stg.get('stage_score', 0)}/10"):
                for sk in stg.get('skills', []):
                    sc = sk.get('score', 0)
                    bc = "#10b981" if sc >= 8 else "#eab308" if sc >= 6 else "#f97316" if sc >= 4 else "#ef4444"
                    sym = "✓" if sc >= 6 else "−" if sc >= 4 else "✗"
                    
                    st.markdown(f"<div style='background:#1f1f1f;border-radius:12px;padding:16px;margin:12px 0;border:1px solid rgba(99,102,241,0.2);'><div style='display:flex;justify-content:space-between;'><span style='font-weight:600;color:#fff;'>{sk.get('skill_name')}</span><span style='background:rgba(99,102,241,0.2);color:{bc};padding:6px 14px;border-radius:20px;font-size:13px;'>{sym} {sc}/10</span></div></div>", unsafe_allow_html=True)
                    
                    if sk.get('what_worked'):
                        st.markdown("**✅ What Worked:**")
                        for w in sk.get('what_worked', []):
                            st.markdown(f"→ {w}")
                    
                    if sk.get('what_needed_improvement'):
                        st.markdown("**❌ Needs Improvement:**")
                        for w in sk.get('what_needed_improvement', []):
                            st.markdown(f"→ {w}")
                    
                    evidence = sk.get('transcript_evidence', [])
                    if evidence:
                        st.markdown("**📍 Evidence:**")
                        for e in evidence:
                            st.markdown(f'<div class="transcript-quote">{e}</div>', unsafe_allow_html=True)
                    
                    improvement = sk.get('improvement', '')
                    if improvement:
                        st.markdown(f'<div class="improvement-box"><p style="color:#10b981;margin:0 0 8px;font-weight:600;">💡 To Improve:</p><p style="color:#e5e5e5;margin:0;">{improvement}</p></div>', unsafe_allow_html=True)
        
        # Objections
        objections = a.get('objections_breakdown', [])
        if objections:
            st.markdown("---")
            st.markdown("## 🛠️ Objection Handling")
            for i, obj in enumerate(objections, 1):
                with st.expander(f"Objection {i}: {obj.get('objection', '')[:60]}... ({obj.get('effectiveness_score', 0)}/10)"):
                    st.markdown(f"Pre-handled: {'✅' if obj.get('pre_handled') else '❌'} | Post-handled: {'✅' if obj.get('post_handled') else '❌'}")
                    if obj.get('what_worked'): st.markdown(f"✅ **What Worked:** {obj.get('what_worked')}")
                    if obj.get('what_needed_improvement'): st.markdown(f"❌ **Needed Improvement:** {obj.get('what_needed_improvement')}")
                    if obj.get('fix_for_next_call'):
                        st.markdown(f'<div class="improvement-box"><p style="color:#10b981;margin:0 0 8px;font-weight:600;">⚡ Fix for Next Call:</p><p style="color:#e5e5e5;margin:0;font-style:italic;">"{obj.get("fix_for_next_call")}"</p></div>', unsafe_allow_html=True)
        
        # Deal Insights
        st.markdown("---")
        st.markdown("## 💼 Deal Insights")
        ins = a.get('deal_insights', {})
        c1, c2, c3 = st.columns(3)
        with c1:
            prob = ins.get('deal_probability', 'Unknown')
            pc = "#10b981" if prob == "High" else "#eab308" if prob == "Medium" else "#ef4444"
            st.markdown(f"<div style='background:#1f1f1f;border-radius:12px;padding:20px;text-align:center;'><p style='color:#9ca3af;margin:0;font-size:12px;'>DEAL PROBABILITY</p><p style='color:{pc};font-size:28px;font-weight:bold;margin:8px 0;'>{prob}</p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("**🟢 Buying Signals**")
            for s in ins.get('buying_signals', []): st.markdown(f"• {s}")
        with c3:
            st.markdown("**🔴 Red Flags**")
            for f in ins.get('red_flags', []): st.markdown(f"• {f}")
        
        st.markdown("#### 📋 Suggested Next Steps")
        for s in ins.get('next_steps_suggested', []): st.markdown(f"- [ ] {s}")
        
        # Final Takeaways
        takeaways = a.get('final_takeaways', {})
        if takeaways:
            st.markdown("---")
            st.markdown("## 🚀 Final Takeaways")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:16px;">
                    <p style="color:#10b981;font-weight:600;margin:0 0 8px;">🔥 Biggest Strength</p>
                    <p style="color:#e5e5e5;margin:0;font-size:14px;">{takeaways.get('biggest_strength', 'N/A')}</p>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:16px;">
                    <p style="color:#ef4444;font-weight:600;margin:0 0 8px;">⚠️ Biggest Weakness</p>
                    <p style="color:#e5e5e5;margin:0;font-size:14px;">{takeaways.get('biggest_weakness', 'N/A')}</p>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);border-radius:12px;padding:16px;">
                    <p style="color:#6366f1;font-weight:600;margin:0 0 8px;">🎯 Game-Changer</p>
                    <p style="color:#e5e5e5;margin:0;font-size:14px;">{takeaways.get('game_changer_for_next_call', 'N/A')}</p>
                </div>""", unsafe_allow_html=True)
        
        # Coaching Summary
        st.markdown("---")
        st.markdown("## 🎓 Coaching Summary")
        st.markdown(f"<div style='background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border-radius:12px;padding:24px;border-left:4px solid #6366f1;'>{a.get('coaching_summary', '')}</div>", unsafe_allow_html=True)
        
        # Follow-up Email Generator
        st.markdown("---")
        st.markdown("## 📧 Follow-up Email Generator")
        
        fe_col1, fe_col2 = st.columns([2, 1])
        with fe_col1:
            email_prompt = st.text_area("What do you want to achieve with this email?", placeholder="e.g., 'Schedule the demo we discussed' or 'Send the proposal with pricing'", height=80, key="gen_email_prompt")
        with fe_col2:
            email_tone = st.selectbox("Tone:", options=list(EMAIL_TONES.keys()), format_func=lambda x: EMAIL_TONES[x]['name'], key="gen_email_tone")
        
        if st.button("✉️ Generate Follow-up Email", use_container_width=True, key="gen_email_btn"):
            with st.spinner("Generating email..."):
                st.session_state.followup_email = generate_followup_email(a, email_tone, email_prompt, mode="general")
        
        if st.session_state.followup_email:
            st.markdown("#### Generated Email:")
            st.code(st.session_state.followup_email, language=None)
            st.download_button("📥 Copy Email", st.session_state.followup_email, "followup_email.txt", use_container_width=True)
        
        # Downloads
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("📥 Markdown", txt, "sales_analysis.md", use_container_width=True)
        with col2:
            pdf_bytes = export_to_pdf(a, f"Sales Call: {st.session_state.get('prospect_name', 'Analysis')}")
            if pdf_bytes:
                st.download_button("📥 PDF", pdf_bytes, "sales_analysis.pdf", "application/pdf", use_container_width=True)
        with col3:
            st.download_button("📥 JSON", json.dumps(a, indent=2), "sales_analysis.json", use_container_width=True)
        
        # Feedback
        st.markdown("---")
        st.markdown("### 💬 Rate This Analysis")
        if st.session_state.feedback_given:
            st.success("Thanks for your feedback! 🙏")
        else:
            fb_col1, fb_col2, _ = st.columns([1, 1, 3])
            with fb_col1:
                if st.button("👍 Helpful", use_container_width=True):
                    if submit_analysis_feedback(a, "thumbs_up"):
                        st.session_state.feedback_given = True
                        st.rerun()
            with fb_col2:
                if st.button("👎 Not Helpful", use_container_width=True):
                    st.session_state.show_feedback_reason = True
            
            if st.session_state.get('show_feedback_reason'):
                reason = st.selectbox("What went wrong?", [r[1] for r in FEEDBACK_REASONS["thumbs_down"]])
                if st.button("Submit Feedback"):
                    submit_analysis_feedback(a, "thumbs_down", reason)
                    st.session_state.feedback_given = True
                    st.session_state.show_feedback_reason = False
                    st.rerun()
        
        st.markdown("---")
        if st.button("🔄 Analyze Another Call", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.feedback_given = False
            st.session_state.followup_email = None
            st.rerun()
    
    except Exception as e:
        st.error(f"Parse error: {e}")
        st.text(st.session_state.analysis_result)

else:
    # General Sales Input Form
    st.markdown("### 📞 Call Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("**Call Information**")
        call_type = st.selectbox("Call Type", list(CALL_FRAMEWORKS.keys()), format_func=lambda x: CALL_FRAMEWORKS[x]['name'])
        
        c1, c2 = st.columns(2)
        with c1:
            prospect_name = st.text_input("Prospect Name", placeholder="John Smith")
        with c2:
            company_name = st.text_input("Company", placeholder="Acme Corp")
        
        c1, c2 = st.columns(2)
        with c1:
            deal_size = st.text_input("Deal Size", placeholder="$50,000")
        with c2:
            stage = st.selectbox("Sales Stage", ["Discovery", "Qualification", "Demo", "Proposal", "Negotiation", "Closed"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("**Context (Optional)**")
        your_website = st.text_input("Your Website", placeholder="https://yourcompany.com - we'll analyze your hero/value prop")
        lead_website = st.text_input("Lead's Website", placeholder="https://leadcompany.com")
        lead_linkedin = st.text_input("Lead's LinkedIn", placeholder="https://linkedin.com/in/lead")
        notes = st.text_area("Notes/Questions", height=68, placeholder="Any specific areas you want analyzed?")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("**Call Recording / Transcript**")
        # Upload as default
        input_method = st.radio("Input Method:", ["📁 Upload File", "📝 Paste Transcript"], horizontal=True)
        
        transcript = ""
        if input_method == "📁 Upload File":
            uploaded_file = st.file_uploader("Upload recording or transcript", type=['txt', 'pdf', 'docx', 'doc', 'vtt', 'srt'], help="Supports: TXT, PDF, DOCX, VTT, SRT")
            if uploaded_file:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    transcript = extract_text_from_file(uploaded_file)
                if transcript and not transcript.startswith("["):
                    st.success(f"✅ Loaded: {uploaded_file.name} ({len(transcript):,} characters)")
                    with st.expander("Preview transcript"):
                        st.text(transcript[:2000] + ("..." if len(transcript) > 2000 else ""))
        else:
            transcript = st.text_area("Paste your transcript here:", height=200, placeholder="Salesperson: Hi John, thanks for taking the time today...\nProspect: Of course, happy to chat...")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Analysis Settings
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("**⚙️ Analysis Settings**")
        
        persona_options = {v["name"]: k for k, v in COACH_PERSONAS.items()}
        selected_persona_name = st.selectbox("Coach Style:", options=list(persona_options.keys()), index=1)
        selected_persona = persona_options[selected_persona_name]
        st.caption(COACH_PERSONAS[selected_persona]["description"])
        
        rigor_options = {v["name"]: k for k, v in RIGOR_LEVELS.items()}
        selected_rigor_name = st.select_slider("Analysis Depth:", options=list(rigor_options.keys()), value="⚖️ Full Analysis")
        selected_rigor = rigor_options[selected_rigor_name]
        
        key_concerns = st.text_area("Specific concerns to analyze:", height=68, placeholder="e.g., 'Did they handle the pricing objection well?' or 'Watch for signs of multi-threading'")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Trial limits
    trial_allowed, trial_usage, trial_limit = check_trial_limit("sales", limit=TRIAL_LIMITS.get("sales", 5))
    user_plan = st.session_state.get('user_plan', 'free')
    if user_plan in ['trial', '7_day_trial', '7-day-trial', 'free_trial']:
        remaining = trial_limit - trial_usage
        if remaining > 0:
            st.info(f"🎯 **Trial:** {remaining} of {trial_limit} analyses remaining")
        else:
            st.warning(f"⚠️ **Trial limit reached:** You've used all {trial_limit} free analyses")
    
    # Analyze Button
    st.markdown("---")
    if st.button("🚀 Analyze Call", type="primary", use_container_width=True, disabled=not trial_allowed):
        if not transcript or len(transcript.strip()) < 100:
            st.warning("Please provide a transcript (minimum 100 characters)")
        else:
            st.session_state.working_on = f"Analyzing as {selected_persona_name}..."
            st.session_state.prospect_name = prospect_name
            
            with st.spinner("🔄 Analyzing your call... This takes 30-60 seconds"):
                result, tokens = analyze_call(
                    transcript=transcript,
                    call_type=call_type,
                    prospect_name=prospect_name,
                    company=company_name,
                    deal_size=deal_size,
                    stage=stage,
                    notes=notes,
                    persona=selected_persona,
                    rigor=selected_rigor,
                    concerns=key_concerns,
                    your_website=your_website,
                    lead_website=lead_website,
                    lead_linkedin=lead_linkedin
                )
            
            st.session_state.working_on = None
            
            if not str(result).startswith("Error"):
                st.session_state.analysis_result = result
                st.rerun()
            else:
                st.error(result)

# Feedback widget
st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)
_, _, _, fb = st.columns([4, 1, 1, 1])
with fb:
    with st.popover("💬 Feedback"):
        st.markdown("**Send Feedback**")
        ft = st.segmented_control("Type", ["🐛 Bug", "✨ Feature", "💬 General"], default="💬 General", label_visibility="collapsed")
        fm = st.text_area("Message", height=100, placeholder="...", label_visibility="collapsed", key="fb_msg")
        if st.button("Send", type="primary", use_container_width=True, key="fb_send"):
            if fm:
                if submit_feedback("sales", ft.split()[1].lower() if ft else "general", fm): st.success("Thanks! 🙏")
                else: st.error("Failed")
