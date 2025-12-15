"""Sharp Assistant - AI Recruiting Partner"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json

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
    "assistant": "https://assistant.sharphuman.com", "admin": "https://admin.sharphuman.com"
}

SYSTEM_PROMPT = """You are Sharp Assistant, an expert AI recruiting partner built into the Sharp Suite platform. You have deep expertise in:

## YOUR EXPERTISE
- **Talent Acquisition**: Sourcing, screening, interviewing, hiring best practices
- **Job Descriptions**: Writing compelling, inclusive, legally-compliant JDs
- **Interviewing**: Question design, evaluation frameworks, bias reduction
- **Candidate Experience**: Communication templates, timeline management
- **Compliance**: EEOC, GDPR, ban-the-box laws, salary history bans
- **Compensation**: Market rates, offer negotiation, total rewards
- **Diversity & Inclusion**: Inclusive hiring practices, bias mitigation
- **Employer Branding**: EVP, recruitment marketing, candidate attraction
- **Recruiting Metrics**: Time-to-hire, quality-of-hire, pipeline analytics
- **HR Technology**: ATS optimization, recruiting tools, automation

## SHARP SUITE TOOLS (you can recommend these)
- **Sharp JD**: AI job description writer
- **Sharp Screen**: CV screening and ranking
- **Sharp Interview**: Interview evaluation and question generation
- **Sharp Source**: Boolean search and outreach sequences
- **Sharp Content**: Blog posts, social media, email content
- **Sharp Sales**: Sales call analysis
- **Sharp Reach**: Outreach campaign management

## YOUR PERSONALITY
- Friendly, professional, and direct
- Give actionable advice, not just theory
- Use bullet points and structure for clarity
- Offer to draft content when relevant (emails, JDs, questions)
- Proactively suggest relevant Sharp tools
- Be concise but thorough

## RESPONSE GUIDELINES
- For template requests: Provide complete, ready-to-use templates
- For strategy questions: Give step-by-step actionable plans
- For compliance questions: Be accurate but recommend legal review for specifics
- For tool questions: Explain how Sharp Suite can help
- Always be helpful and practical

When users ask for templates or content, provide complete, professional examples they can use immediately."""

QUICK_TEMPLATES = {
    "rejection_email": {
        "name": "Rejection Email",
        "icon": "📧",
        "prompt": "Write a professional, empathetic rejection email for a candidate who interviewed but wasn't selected. Keep the door open for future opportunities."
    },
    "offer_letter": {
        "name": "Offer Letter Template", 
        "icon": "📝",
        "prompt": "Create a professional job offer letter template with placeholders for: candidate name, job title, salary, start date, benefits summary, and reporting manager."
    },
    "interview_scorecard": {
        "name": "Interview Scorecard",
        "icon": "📋",
        "prompt": "Create a structured interview scorecard template with rating scales for: technical skills, communication, problem-solving, cultural fit, and motivation. Include space for notes and an overall recommendation."
    },
    "reference_check": {
        "name": "Reference Check Questions",
        "icon": "📞",
        "prompt": "Provide a comprehensive list of reference check questions covering: job performance, strengths/weaknesses, work style, reason for leaving, and rehire eligibility."
    },
    "counter_offer": {
        "name": "Counter-Offer Response",
        "icon": "💰",
        "prompt": "Write a professional response to a candidate who received a counter-offer from their current employer. Address their concerns while reinforcing your opportunity's value."
    },
    "sourcing_message": {
        "name": "LinkedIn Sourcing Message",
        "icon": "💼",
        "prompt": "Write 3 different LinkedIn InMail templates for reaching out to passive candidates: 1) Direct approach, 2) Curiosity-driven, 3) Mutual connection reference. Keep each under 300 characters."
    },
    "phone_screen": {
        "name": "Phone Screen Script",
        "icon": "📱",
        "prompt": "Create a 20-minute phone screen script template with: intro, role overview, candidate background questions, motivation questions, logistics (salary, availability, location), and next steps."
    },
    "hiring_manager_intake": {
        "name": "Hiring Manager Intake",
        "icon": "🎯",
        "prompt": "Create a hiring manager intake questionnaire covering: role requirements, team structure, ideal candidate profile, interview process preferences, timeline, and success metrics."
    }
}

QUICK_QUESTIONS = [
    "How do I source passive candidates for hard-to-fill roles?",
    "What are the best behavioral interview questions?",
    "How do I reduce time-to-hire without sacrificing quality?",
    "What should I include in a job description for a Senior Engineer?",
    "How do I handle salary negotiation conversations?",
    "What are illegal interview questions I should avoid?",
    "How do I improve candidate experience?",
    "What metrics should I track for recruiting success?"
]

# ============================================
# AUTH FUNCTIONS
# ============================================

def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "assistant",
                  "is_active": True, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()}, timeout=10)
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
            return {"success": True, "message": "Check your email to confirm!"}
        return {"success": False, "message": data.get("error_description") or "Sign up failed"}
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
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "session_id": session_id, "app": app, "action": action, "tokens_used": tokens_used}, timeout=5)
    except:
        pass

def submit_feedback(app, feedback_type, message):
    try:
        email = get_user_email()
        user_id = st.session_state.user.get("id") if st.session_state.user else None
        r = requests.post(f"{SUPABASE_URL}/rest/v1/user_feedback",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"user_id": user_id, "app": app, "feedback_type": feedback_type, "rating": 4, "message": message, "email": email}, timeout=10)
        return r.status_code in [200, 201]
    except:
        return False

def init_session():
    defaults = [
        ('authenticated', False), ('user', None), ('is_god', False), ('session_token', None),
        ('user_plan', 'free'), ('messages', []), ('working_on', None)
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
# CHAT FUNCTIONS
# ============================================

def chat_with_assistant(messages):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set"
    
    try:
        # Build message history for Claude
        claude_messages = []
        for msg in messages:
            claude_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "system": SYSTEM_PROMPT,
                "messages": claude_messages
            }, timeout=120)
        
        if r.status_code == 200:
            response_text = r.json()["content"][0]["text"]
            # Log usage
            if st.session_state.user:
                tokens = sum(len(m["content"]) for m in messages) + len(response_text)
                log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "assistant", "chat", tokens // 4)
            return response_text
        return f"Error: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# ============================================
# MAIN APP
# ============================================

st.set_page_config(page_title="Sharp Assistant", page_icon="🤖", layout="wide")
init_session()
check_url_auth()

# Styles
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
.stTextInput > div > div > input, .stTextArea > div > div > textarea { 
    background: #12121a !important; 
    border: 1px solid rgba(99,102,241,0.3) !important; 
    color: #fff !important; 
    border-radius: 8px !important; 
}
.stButton > button { 
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; 
    color: white !important; 
    border: none !important; 
    border-radius: 8px !important; 
    font-weight: 600 !important; 
}
.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.chat-container { 
    background: #12121a; 
    border: 1px solid rgba(99,102,241,0.2); 
    border-radius: 16px; 
    padding: 20px; 
    margin: 16px 0;
    max-height: 500px;
    overflow-y: auto;
}
.user-message {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    padding: 12px 16px;
    border-radius: 16px 16px 4px 16px;
    margin: 8px 0;
    margin-left: 20%;
    text-align: right;
}
.assistant-message {
    background: #1a1a2e;
    color: #e5e5e5;
    padding: 12px 16px;
    border-radius: 16px 16px 16px 4px;
    margin: 8px 0;
    margin-right: 10%;
    border: 1px solid rgba(99,102,241,0.2);
}
.template-btn {
    background: #1a1a2e !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    color: #a5b4fc !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    margin: 4px !important;
    font-size: 13px !important;
}
.quick-question {
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    cursor: pointer;
    font-size: 14px;
    color: #a5b4fc;
}
.quick-question:hover {
    background: rgba(99,102,241,0.2);
}
.status-badge { 
    position: fixed; 
    top: 70px; 
    right: 20px; 
    background: linear-gradient(135deg, #6366f1, #8b5cf6); 
    color: white; 
    padding: 10px 20px; 
    border-radius: 25px; 
    font-weight: 600; 
    z-index: 999; 
    animation: pulse 2s infinite; 
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
div[data-testid="stPopover"] button { 
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; 
    color: white !important; 
    border: none !important; 
    border-radius: 25px !important; 
}
.tool-card {
    background: #12121a;
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    transition: all 0.2s;
}
.tool-card:hover {
    border-color: #6366f1;
    transform: translateY(-2px);
}
</style>""", unsafe_allow_html=True)

# Auth Screen
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;">
            <h1 style="margin:0;">Sharp Assistant</h1>
            <p style="color:#9ca3af;">Your AI Recruiting Partner</p>
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
            s_conf = st.text_input("Confirm Password", type="password", key="s_conf")
            if st.button("Create Account", use_container_width=True):
                if s_pwd != s_conf:
                    st.error("Passwords don't match")
                elif len(s_pwd) < 6:
                    st.warning("Password must be 6+ characters")
                elif s_email and s_pwd:
                    r = supabase_sign_up(s_email, s_pwd)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
    st.stop()

# Working indicator
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
    apps = [
        ("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"),
        ("interview", "🎯 Interview"), ("source", "🎣 Sourcing"), ("content", "✍️ Content"),
        ("sales", "💰 Sales"), ("reach", "🚀 Reach"), ("assistant", "🤖 Assistant")
    ]
    for key, label in apps:
        if key == "assistant":
            st.markdown(f"<div style='background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:10px 16px;border-radius:8px;text-align:center;margin:4px 0;color:white;font-weight:600;'>{label} ◀</div>", unsafe_allow_html=True)
        else:
            st.link_button(label, build_app_url(key), use_container_width=True)
    
    if st.session_state.get("is_god"):
        st.markdown("---")
        st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:50px;">
    <div>
        <h1 style="margin:0;font-size:28px;">Sharp Assistant</h1>
        <p style="color:#9ca3af;margin:0;">Your AI Recruiting Partner</p>
    </div>
</div>""", unsafe_allow_html=True)

# Main Layout
col_chat, col_tools = st.columns([2, 1])

with col_chat:
    # Chat Messages
    st.markdown("### 💬 Chat")
    
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            # Welcome message
            st.markdown("""
            <div class="assistant-message">
                <p style="margin:0 0 12px;"><strong>👋 Welcome! I'm your AI recruiting partner.</strong></p>
                <p style="margin:0 0 8px;">I can help you with:</p>
                <ul style="margin:0;padding-left:20px;">
                    <li>Writing job descriptions and interview questions</li>
                    <li>Sourcing and screening strategies</li>
                    <li>Salary negotiation and offer management</li>
                    <li>Compliance and legal considerations</li>
                    <li>Email templates and candidate communication</li>
                    <li>Recruiting metrics and process optimization</li>
                </ul>
                <p style="margin:12px 0 0;color:#a5b4fc;">Try a quick question below or ask me anything!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display chat history
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="assistant-message">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    
    user_input = st.text_area("Ask me anything about recruiting...", height=80, key="user_input", 
        placeholder="e.g., How do I write a compelling job description for a remote Senior Engineer role?")
    
    col_send, col_clear = st.columns([3, 1])
    with col_send:
        if st.button("🚀 Send", type="primary", use_container_width=True):
            if user_input and user_input.strip():
                # Add user message
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Get response
                st.session_state.working_on = "Thinking..."
                response = chat_with_assistant(st.session_state.messages)
                st.session_state.working_on = None
                
                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                st.rerun()
    
    # Quick Questions
    if not st.session_state.messages:
        st.markdown("#### 💡 Quick Questions")
        cols = st.columns(2)
        for i, q in enumerate(QUICK_QUESTIONS):
            with cols[i % 2]:
                if st.button(q, key=f"qq_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": q})
                    st.session_state.working_on = "Thinking..."
                    response = chat_with_assistant(st.session_state.messages)
                    st.session_state.working_on = None
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

with col_tools:
    # Templates
    st.markdown("### 📚 Templates")
    st.caption("Click to generate instantly")
    
    for key, template in QUICK_TEMPLATES.items():
        if st.button(f"{template['icon']} {template['name']}", key=f"tpl_{key}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": template["prompt"]})
            st.session_state.working_on = "Generating template..."
            response = chat_with_assistant(st.session_state.messages)
            st.session_state.working_on = None
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    st.markdown("---")
    
    # Quick Links to Tools
    st.markdown("### 🛠️ Sharp Tools")
    st.caption("Jump to other apps")
    
    tool_links = [
        ("jd", "📝 Write JD", "Create job descriptions"),
        ("screen", "🔍 Screen CVs", "Rank candidates"),
        ("interview", "🎯 Interview", "Evaluate candidates"),
        ("source", "🎣 Source", "Find candidates"),
        ("content", "✍️ Content", "Create content"),
    ]
    
    for app_key, label, desc in tool_links:
        st.link_button(f"{label}", build_app_url(app_key), use_container_width=True)

# Feedback
st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)
_, _, _, fb = st.columns([4, 1, 1, 1])
with fb:
    with st.popover("💬 Feedback"):
        st.markdown("**Send Feedback**")
        ft = st.segmented_control("Type", ["🐛 Bug", "✨ Feature", "💬 General"], default="💬 General", label_visibility="collapsed")
        fm = st.text_area("Message", height=100, placeholder="Your feedback...", label_visibility="collapsed", key="fb_msg")
        if st.button("Send", type="primary", use_container_width=True, key="fb_send"):
            if fm:
                fb_type = ft.split()[1].lower() if ft else "general"
                if submit_feedback("assistant", fb_type, fm):
                    st.success("Thanks! 🙏")
                else:
                    st.error("Failed to send")
