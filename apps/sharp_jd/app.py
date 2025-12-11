"""
Sharp JD - AI-Powered Job Description Generator
STANDALONE VERSION - No external imports
"""
import streamlit as st
import requests
import os

# ============== CONFIG ==============
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOD_PASSWORD = "G0DHum@n101!!!"
DEMO_PASSWORD = "D3M0Human101!!!"

# ============== API ==============
def call_claude(prompt, max_tokens=4096):
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set", 0, 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]},
            timeout=120)
        if r.status_code == 200:
            return r.json()["content"][0]["text"], r.json().get("usage",{}).get("input_tokens",0), r.json().get("usage",{}).get("output_tokens",0)
        return f"API Error: {r.status_code}", 0, 0
    except Exception as e:
        return f"Error: {str(e)}", 0, 0

# ============== AUTH ==============
def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.access_level = None
    return st.session_state.authenticated

def login_form():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%); }
    * { font-family: 'Nunito', sans-serif !important; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding:60px 0 40px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px; height:80px; margin-bottom:20px;">
            <h1 style="color:white; margin-bottom:8px;">Sharp JD</h1>
            <p style="color:#9ca3af;">AI-Powered Job Description Generator</p>
        </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Enter Access Password", type="password", key="pwd")
        if st.button("🚀 Access Sharp Suite", type="primary", use_container_width=True):
            if password == GOD_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.access_level = "god"
                st.rerun()
            elif password == DEMO_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.access_level = "demo"
                st.rerun()
            else:
                st.error("Invalid password")
        
        st.markdown('<p style="text-align:center; color:#6b7280; margin-top:24px;">Need access? <a href="mailto:sharpsuite@sharphuman.com" style="color:#6366f1;">sharpsuite@sharphuman.com</a></p>', unsafe_allow_html=True)

# ============== STYLES ==============
def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    * { font-family: 'Nunito', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 100%); }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #ffffff !important; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { background: #12121a !important; border: 1px solid rgba(99,102,241,0.3) !important; color: white !important; border-radius: 8px !important; }
    .stSelectbox > div > div { background: #12121a !important; color: white !important; }
    .stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
    .stCheckbox label, .stRadio label, p, span, label { color: #e5e5e5 !important; }
    .output-box { background: #12121a; border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 24px; margin: 16px 0; }
    [data-testid="stSidebar"] { background: #0a0a0f; border-right: 1px solid rgba(99,102,241,0.1); }
    .stExpander { background: #12121a; border: 1px solid rgba(99,102,241,0.1); border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# ============== MAIN APP ==============
st.set_page_config(page_title="Sharp JD | Generator", page_icon="📝", layout="wide")

if not check_auth():
    login_form()
    st.stop()

apply_styles()

# Sidebar logout
with st.sidebar:
    st.markdown(f"**{st.session_state.access_level.upper()}** access")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Header
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; padding:20px 0; border-bottom:1px solid rgba(99,102,241,0.2); margin-bottom:24px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:45px;">
    <div>
        <h1 style="margin:0; font-size:1.8rem; color:white;">Sharp JD</h1>
        <p style="color:#9ca3af; margin:0;">AI-Powered Job Description Generator</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Bias terms
BIASED_TERMS = {"ninja": "specialist", "rockstar": "high-performer", "guru": "expert", "wizard": "specialist", "hacker": "developer", "aggressive": "ambitious", "manpower": "workforce"}

# Tips
with st.expander("💡 Tips for Best Results"):
    st.markdown("• **Include salary** - 30% more applications\n• **Remote policy** - #1 candidate filter\n• **Short format** for job boards, **Long** for formal")

# Form
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📋 Job Details")
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        job_title = st.text_input("Job Title *", placeholder="Senior Software Engineer")
        company = st.text_input("Company *", placeholder="TechCorp Inc.")
        location = st.text_input("Location *", placeholder="San Francisco, CA")
    with r1c2:
        department = st.text_input("Department", placeholder="Engineering")
        reports_to = st.text_input("Reports To", placeholder="VP of Engineering")
        employment_type = st.selectbox("Type", ["Full-time", "Part-time", "Contract", "Internship"])
    
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        salary_range = st.text_input("Salary Range", placeholder="$120,000 - $150,000")
    with r2c2:
        remote_policy = st.selectbox("Remote Policy", ["Remote", "Hybrid", "On-site", "Flexible"])
    
    requirements = st.text_area("Requirements *", placeholder="- 5+ years Python\n- AWS experience\n- Communication skills", height=120)
    responsibilities = st.text_area("Responsibilities *", placeholder="- Lead development\n- Mentor engineers\n- Code reviews", height=120)
    
    with st.expander("➕ Additional Details"):
        company_desc = st.text_area("Company Description", height=80)
        benefits = st.text_area("Benefits", height=80)

with col2:
    st.markdown("### ⚙️ Options")
    jd_format = st.radio("Format", ["Short (300-500 words)", "Long (800-1200 words)"])
    st.markdown("---")
    check_bias = st.checkbox("🔍 Check for bias", value=True)
    estimate_salary = st.checkbox("💰 Estimate salary", value=False)
    seo_optimize = st.checkbox("🔎 SEO optimize", value=True)
    st.markdown("---")
    st.info("💡 Salary info increases applications 30%!")

# Generate
st.markdown("---")
if st.button("⚡ Generate Job Description", type="primary", use_container_width=True):
    if not job_title or not company or not requirements:
        st.error("Please fill Job Title, Company, and Requirements")
    else:
        format_inst = "CONCISE (300-500 words)" if "Short" in jd_format else "COMPREHENSIVE (800-1200 words)"
        prompt = f"""Create a {format_inst} job description:
Job Title: {job_title} | Company: {company} | Location: {location}
Department: {department} | Reports To: {reports_to} | Type: {employment_type}
Salary: {salary_range or "Competitive"} | Remote: {remote_policy}

REQUIREMENTS: {requirements}
RESPONSIBILITIES: {responsibilities}
COMPANY: {company_desc or "N/A"} | BENEFITS: {benefits or "Competitive package"}

{"SEO optimize for Google Jobs." if seo_optimize else ""} Use inclusive language. Format in markdown."""

        with st.spinner("✨ Generating..."):
            response, _, _ = call_claude(prompt, max_tokens=2000)
            
            if response.startswith("Error"):
                st.error(response)
            else:
                if check_bias:
                    for term, alt in BIASED_TERMS.items():
                        if term.lower() in response.lower():
                            st.warning(f"⚠️ Consider replacing **'{term}'** with **'{alt}'**")
                
                st.markdown("### 📄 Your Job Description")
                st.markdown(f'<div class="output-box">{response}</div>', unsafe_allow_html=True)
                st.download_button("📥 Download", response, f"JD_{job_title.replace(' ','_')}.txt")
        
        if estimate_salary:
            with st.spinner("💰 Estimating salary..."):
                sal_resp, _, _ = call_claude(f"Estimate salary for {job_title} in {location}: {requirements[:300]}. Give 25th/50th/75th percentile.", max_tokens=500)
                st.markdown("### 💰 Salary Estimate")
                st.info(sal_resp)

# Feedback
st.markdown('<a href="mailto:sharpsuite@sharphuman.com?subject=Sharp%20JD%20Feedback" style="position:fixed; bottom:20px; right:20px; background:#6366f1; color:white; padding:12px 20px; border-radius:30px; text-decoration:none; font-weight:600;">💬 Feedback</a>', unsafe_allow_html=True)
