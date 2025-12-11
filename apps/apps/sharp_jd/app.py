"""
Sharp JD - AI Job Description Generator
With Supabase Auth
"""
import streamlit as st
import requests
import os

# ============== CONFIG ==============
SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ============== AUTH ==============
def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            return {"success": True, "user": data.get("user")}
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

def supabase_magic_link(email):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email}, timeout=10)
        return {"success": r.status_code == 200, "message": "Magic link sent!" if r.status_code == 200 else "Failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def init_session():
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False
    if 'user' not in st.session_state: st.session_state.user = None
    if 'is_god' not in st.session_state: st.session_state.is_god = False

def get_user_email():
    if st.session_state.user: return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"

def render_auth():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f, #0f0f1a); }
    * { font-family: 'Nunito', sans-serif !important; }
    .stTextInput > div > div > input { background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; }
    .stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; }
    .stTabs [data-baseweb="tab-list"] { background: #12121a; border-radius: 8px; }
    .stTabs [aria-selected="true"] { background: rgba(99,102,241,0.3) !important; color: white !important; }
    </style>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""<div style="text-align:center; padding:40px 0 30px;"><img src="https://sharphuman.com/logo1-3.png" style="width:70px; margin-bottom:16px;"><h1 style="color:white;">Sharp JD</h1><p style="color:#9ca3af;">AI Job Description Generator</p></div>""", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        with tab1:
            email = st.text_input("Email", key="le")
            password = st.text_input("Password", type="password", key="lp")
            if st.button("Log In", use_container_width=True):
                if password == GOD_PASSWORD:
                    st.session_state.authenticated = True; st.session_state.is_god = True; st.session_state.user = {"email": "GOD"}; st.rerun()
                elif email and password:
                    r = supabase_sign_in(email, password)
                    if r["success"]: st.session_state.authenticated = True; st.session_state.user = r["user"]; st.rerun()
                    else: st.error(r["message"])
            st.markdown("<p style='text-align:center;color:#6b7280;'>— or —</p>", unsafe_allow_html=True)
            me = st.text_input("Magic link email", key="me", label_visibility="collapsed", placeholder="Email for magic link")
            if st.button("✨ Send Magic Link", use_container_width=True, key="ml"):
                if me: r = supabase_magic_link(me); st.success(r["message"]) if r["success"] else st.error(r["message"])
        with tab2:
            se = st.text_input("Email", key="se")
            sp = st.text_input("Password", type="password", key="sp")
            sc = st.text_input("Confirm", type="password", key="sc")
            if st.button("Create Account", use_container_width=True):
                if sp != sc: st.error("Passwords don't match")
                elif len(sp) < 6: st.warning("6+ characters")
                elif se and sp: r = supabase_sign_up(se, sp); st.success(r["message"]) if r["success"] else st.error(r["message"])

# ============== CLAUDE API ==============
def call_claude(prompt, max_tokens=2000):
    if not ANTHROPIC_API_KEY: return "Error: ANTHROPIC_API_KEY not set"
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200: return r.json()["content"][0]["text"]
        return f"Error: {r.status_code}"
    except Exception as e: return f"Error: {str(e)}"

# ============== MAIN ==============
st.set_page_config(page_title="Sharp JD", page_icon="📝", layout="wide")
init_session()

if not st.session_state.authenticated:
    render_auth()
    st.stop()

# ============== APP STYLES ==============
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f, #0f0f1a); }
h1,h2,h3 { color: white !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; }
.output-box { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 24px; margin: 16px 0; }
p,span,label { color: #e5e5e5 !important; }
</style>""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"<div style='padding:12px;background:rgba(99,102,241,0.1);border-radius:8px;'><p style='color:#9ca3af;margin:0;font-size:0.75rem;'>Logged in as</p><p style='color:white;margin:0;font-weight:600;'>{get_user_email()}</p></div>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True): st.session_state.authenticated = False; st.session_state.user = None; st.session_state.is_god = False; st.rerun()

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;font-size:1.8rem;">Sharp JD</h1><p style="color:#9ca3af;margin:0;">AI-Powered Job Description Generator</p></div></div>""", unsafe_allow_html=True)

# Form
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### 📋 Job Details")
    c1, c2 = st.columns(2)
    job_title = c1.text_input("Job Title *", placeholder="Senior Software Engineer")
    company = c1.text_input("Company *", placeholder="TechCorp")
    location = c1.text_input("Location *", placeholder="San Francisco, CA")
    department = c2.text_input("Department", placeholder="Engineering")
    reports_to = c2.text_input("Reports To", placeholder="VP Engineering")
    emp_type = c2.selectbox("Type", ["Full-time", "Part-time", "Contract"])
    
    c3, c4 = st.columns(2)
    salary = c3.text_input("Salary Range", placeholder="$120K - $150K")
    remote = c4.selectbox("Remote", ["Remote", "Hybrid", "On-site"])
    
    requirements = st.text_area("Requirements *", placeholder="- 5+ years Python\n- AWS experience", height=100)
    responsibilities = st.text_area("Responsibilities *", placeholder="- Lead development\n- Code reviews", height=100)

with col2:
    st.markdown("### ⚙️ Options")
    jd_format = st.radio("Format", ["Short (300-500)", "Long (800-1200)"])
    check_bias = st.checkbox("🔍 Check bias", value=True)
    seo = st.checkbox("🔎 SEO optimize", value=True)
    st.info("💡 Salary info increases applications 30%!")

st.markdown("---")
if st.button("⚡ Generate Job Description", type="primary", use_container_width=True):
    if not job_title or not company or not requirements:
        st.error("Fill required fields")
    else:
        fmt = "CONCISE 300-500 words" if "Short" in jd_format else "DETAILED 800-1200 words"
        prompt = f"""Create a {fmt} job description:
Title: {job_title} | Company: {company} | Location: {location}
Dept: {department} | Reports: {reports_to} | Type: {emp_type}
Salary: {salary or "Competitive"} | Remote: {remote}
Requirements: {requirements}
Responsibilities: {responsibilities}
{"SEO optimize for Google Jobs." if seo else ""} Use inclusive language. Markdown format."""
        
        with st.spinner("✨ Generating..."):
            response = call_claude(prompt)
            if check_bias:
                for term, alt in {"ninja":"specialist","rockstar":"high-performer","guru":"expert"}.items():
                    if term in response.lower(): st.warning(f"Consider replacing '{term}' with '{alt}'")
            st.markdown("### 📄 Your JD")
            st.markdown(f'<div class="output-box">{response}</div>', unsafe_allow_html=True)
            st.download_button("📥 Download", response, f"JD_{job_title}.txt")
