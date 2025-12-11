"""Sharp JD - AI Job Description Generator with Full Auth"""
import streamlit as st
import requests
import os

# ============== CONFIG ==============
SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ============== SUPABASE AUTH ==============
def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("user"):
            return {"success": True, "message": "✅ Check your email to confirm your account!"}
        return {"success": False, "message": data.get("error_description") or data.get("msg") or "Sign up failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            return {"success": True, "user": data.get("user"), "access_token": data.get("access_token")}
        return {"success": False, "message": data.get("error_description") or "Invalid email or password"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def supabase_magic_link(email):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"email": email}, timeout=10)
        if r.status_code == 200:
            return {"success": True, "message": "✨ Magic link sent! Check your email."}
        return {"success": False, "message": "Failed to send magic link"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ============== SESSION ==============
def init_session():
    defaults = {'authenticated': False, 'user': None, 'is_god': False, 'access_token': None}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_user_email():
    if st.session_state.is_god:
        return "GOD MODE"
    if st.session_state.user:
        return st.session_state.user.get("email", "User")
    return "User"

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.is_god = False
    st.session_state.access_token = None

# ============== AUTH UI ==============
def render_auth_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%); }
    * { font-family: 'Nunito', sans-serif !important; }
    
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 12px 16px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 6px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #9ca3af !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
    }
    
    .magic-link-btn button {
        background: transparent !important;
        border: 1px solid rgba(99,102,241,0.4) !important;
        color: #a5b4fc !important;
    }
    .magic-link-btn button:hover {
        background: rgba(99,102,241,0.1) !important;
        border-color: #6366f1 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 50px 0 40px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width: 80px; height: 80px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0 0 8px; font-size: 2rem; font-weight: 800;">Sharp JD</h1>
            <p style="color: #9ca3af; margin: 0; font-size: 1rem;">AI-Powered Job Description Generator</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Auth container
        st.markdown('<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(99,102,241,0.15); border-radius: 16px; padding: 32px;">', unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        
        with tab1:
            st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
            
            login_email = st.text_input("Email", placeholder="you@company.com", key="login_email")
            login_password = st.text_input("Password", type="password", placeholder="Your password", key="login_password")
            
            st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
            
            if st.button("🚀 Log In", use_container_width=True, key="btn_login"):
                if login_password == GOD_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_god = True
                    st.session_state.user = {"email": "GOD"}
                    st.rerun()
                elif login_email and login_password:
                    result = supabase_sign_in(login_email, login_password)
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = result["user"]
                        st.session_state.access_token = result.get("access_token")
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning("Please enter email and password")
            
            # Divider
            st.markdown("""
            <div style="display: flex; align-items: center; margin: 24px 0;">
                <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.1);"></div>
                <span style="padding: 0 16px; color: #6b7280; font-size: 0.85rem;">or continue with</span>
                <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.1);"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Magic link
            magic_email = st.text_input("", placeholder="Enter email for magic link", key="magic_email", label_visibility="collapsed")
            
            st.markdown('<div class="magic-link-btn">', unsafe_allow_html=True)
            if st.button("✨ Send Magic Link", use_container_width=True, key="btn_magic"):
                if magic_email:
                    result = supabase_magic_link(magic_email)
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                else:
                    st.warning("Enter your email above")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
            
            signup_email = st.text_input("Email", placeholder="you@company.com", key="signup_email")
            signup_password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="signup_confirm")
            
            st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
            
            if st.button("🎉 Create Account", use_container_width=True, key="btn_signup"):
                if not signup_email or not signup_password:
                    st.warning("Please fill in all fields")
                elif len(signup_password) < 6:
                    st.warning("Password must be at least 6 characters")
                elif signup_password != signup_confirm:
                    st.error("Passwords don't match")
                else:
                    result = supabase_sign_up(signup_email, signup_password)
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <p style="text-align: center; color: #6b7280; margin-top: 24px; font-size: 0.85rem;">
            Need help? <a href="mailto:support@sharphuman.com" style="color: #6366f1; text-decoration: none;">support@sharphuman.com</a>
        </p>
        """, unsafe_allow_html=True)

# ============== CLAUDE API ==============
def call_claude(prompt, max_tokens=2000):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not configured"
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=120)
        if r.status_code == 200:
            return r.json()["content"][0]["text"]
        return f"Error: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# ============== MAIN APP ==============
st.set_page_config(page_title="Sharp JD", page_icon="📝", layout="wide")
init_session()

# Auth check
if not st.session_state.authenticated:
    render_auth_ui()
    st.stop()

# ============== AUTHENTICATED APP ==============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%); }
h1, h2, h3 { color: white !important; }
p, span, label { color: #e5e5e5 !important; }

.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    color: white !important;
    border-radius: 8px !important;
}
.stSelectbox > div > div { background: rgba(255,255,255,0.05) !important; }

.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

.output-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 24px;
    margin: 16px 0;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 16px; background: rgba(99,102,241,0.1); border-radius: 12px; border: 1px solid rgba(99,102,241,0.2);">
        <p style="color: #9ca3af; margin: 0 0 4px; font-size: 0.75rem;">Logged in as</p>
        <p style="color: white; margin: 0; font-weight: 600;">{get_user_email()}</p>
        {"<p style='color: #f59e0b; margin: 4px 0 0; font-size: 0.75rem;'>👑 GOD MODE</p>" if st.session_state.is_god else ""}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

# Header
st.markdown("""
<div style="display: flex; align-items: center; gap: 16px; padding: 24px 0; border-bottom: 1px solid rgba(99,102,241,0.2); margin-bottom: 32px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width: 50px; height: 50px;">
    <div>
        <h1 style="margin: 0; font-size: 1.8rem;">Sharp JD</h1>
        <p style="color: #9ca3af; margin: 0;">AI-Powered Job Description Generator</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Form
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📋 Job Details")
    
    c1, c2 = st.columns(2)
    job_title = c1.text_input("Job Title *", placeholder="Senior Software Engineer")
    company = c1.text_input("Company *", placeholder="Acme Corp")
    location = c1.text_input("Location *", placeholder="San Francisco, CA")
    
    department = c2.text_input("Department", placeholder="Engineering")
    reports_to = c2.text_input("Reports To", placeholder="VP of Engineering")
    emp_type = c2.selectbox("Employment Type", ["Full-time", "Part-time", "Contract", "Intern"])
    
    c3, c4 = st.columns(2)
    salary = c3.text_input("Salary Range", placeholder="$120,000 - $150,000")
    remote = c4.selectbox("Remote Policy", ["Remote", "Hybrid", "On-site"])
    
    requirements = st.text_area("Requirements *", placeholder="- 5+ years Python experience\n- AWS/cloud experience\n- Strong communication skills", height=120)
    responsibilities = st.text_area("Key Responsibilities *", placeholder="- Lead development of microservices\n- Mentor junior engineers\n- Code reviews", height=120)
    
    additional = st.text_area("Additional Details (Optional)", placeholder="Benefits, culture, perks...", height=80)

with col2:
    st.markdown("### ⚙️ Options")
    
    jd_format = st.radio("JD Format", ["Short (300-500 words)", "Long (800-1200 words)"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    check_bias = st.checkbox("🔍 Check for biased language", value=True)
    estimate_salary = st.checkbox("💰 Estimate market salary", value=False)
    seo_optimize = st.checkbox("🔎 SEO optimize for Google Jobs", value=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("💡 **Pro Tip:** Adding salary info increases applications by 30%!")

st.markdown("---")

if st.button("⚡ Generate Job Description", type="primary", use_container_width=True):
    if not job_title or not company or not requirements:
        st.error("Please fill in required fields (Job Title, Company, Requirements)")
    else:
        word_count = "300-500" if "Short" in jd_format else "800-1200"
        
        prompt = f"""Create a {word_count} word job description with the following details:

Job Title: {job_title}
Company: {company}
Location: {location}
Department: {department}
Reports To: {reports_to}
Employment Type: {emp_type}
Salary Range: {salary or "Competitive"}
Remote Policy: {remote}

Requirements:
{requirements}

Key Responsibilities:
{responsibilities}

Additional Details:
{additional or "N/A"}

Instructions:
- Write in a professional, engaging tone
- Use inclusive language (avoid gendered terms, ableist language)
- {"Optimize for Google Jobs SEO with relevant keywords" if seo_optimize else ""}
- Include sections: About Company, Role Overview, Responsibilities, Requirements, Nice-to-haves, Benefits
- Format in clean markdown"""

        with st.spinner("✨ Generating your job description..."):
            result = call_claude(prompt)
            
            # Bias check
            if check_bias:
                bias_terms = {"ninja": "specialist", "rockstar": "high-performer", "guru": "expert", "he/him": "they/them", "manpower": "workforce"}
                for term, replacement in bias_terms.items():
                    if term.lower() in result.lower():
                        st.warning(f"⚠️ Consider replacing '{term}' with '{replacement}' for more inclusive language")
            
            st.markdown("### 📄 Your Job Description")
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            col1.download_button("📥 Download as TXT", result, file_name=f"JD_{job_title.replace(' ', '_')}.txt", use_container_width=True)
            col2.download_button("📋 Copy to Clipboard", result, file_name=f"JD_{job_title.replace(' ', '_')}.md", use_container_width=True)
