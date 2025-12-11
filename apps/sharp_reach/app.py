"""
Sharp Reach - BD & Lead Outreach
STANDALONE VERSION
"""
import streamlit as st
import requests
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOD_PASSWORD = "G0DHum@n101!!!"
DEMO_PASSWORD = "D3M0Human101!!!"

def call_claude(prompt, max_tokens=4096):
    if not ANTHROPIC_API_KEY: return "Error: ANTHROPIC_API_KEY not set", 0, 0
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200: return r.json()["content"][0]["text"], 0, 0
        return f"API Error: {r.status_code}", 0, 0
    except Exception as e: return f"Error: {str(e)}", 0, 0

def check_auth():
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False; st.session_state.access_level = None
    return st.session_state.authenticated

def login_form():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:60px 0 40px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="color:white;">Sharp Reach</h1><p style="color:#9ca3af;">BD & Lead Outreach</p></div>""", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", key="pwd")
        if st.button("🚀 Access", type="primary", use_container_width=True):
            if password == GOD_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "god"; st.rerun()
            elif password == DEMO_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "demo"; st.rerun()
            else: st.error("Invalid password")

def apply_styles():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}h1,h2,h3{color:#fff!important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}.output-box{background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:24px;margin:16px 0;}p,span,label{color:#e5e5e5!important;}</style>""", unsafe_allow_html=True)

st.set_page_config(page_title="Sharp Reach", page_icon="🚀", layout="wide")

if not check_auth(): login_form(); st.stop()

apply_styles()

with st.sidebar:
    st.markdown(f"**{st.session_state.access_level.upper()}**")
    if st.button("🚪 Logout"): st.session_state.authenticated = False; st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;color:white;">Sharp Reach</h1><p style="color:#9ca3af;margin:0;">Multi-Channel Lead Outreach</p></div></div>""", unsafe_allow_html=True)

st.markdown("### 🎯 Create Personalized Outreach")

st.markdown("#### 📋 Lead Info")
col1, col2, col3 = st.columns(3)
with col1:
    name = st.text_input("Contact Name", placeholder="Sarah Johnson")
    company = st.text_input("Company", placeholder="TechCorp")
    title = st.text_input("Title", placeholder="VP Talent")
with col2:
    ltype = st.selectbox("Lead Type", ["🔥 Hot", "🌡️ Warm", "❄️ Cold", "👴 Dormant"])
    history = st.text_input("History", placeholder="Met at conference...")
    last = st.text_input("Last Contact", placeholder="3 months ago")
with col3:
    linkedin = st.text_input("LinkedIn")
    email = st.text_input("Email")

st.markdown("---")
st.markdown("#### 📎 Context")
context = st.text_area("All context (call notes, previous emails, company info)", height=150)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    goal = st.selectbox("Goal", ["Re-engage", "Follow up on proposal", "Share new service", "Request meeting", "Share content", "Request referral"])
    offering = st.text_area("What you're offering", height=80)
with col2:
    yname = st.text_input("Your Name", placeholder="Judd Kozi")
    ycompany = st.text_input("Your Company", placeholder="Sharp Human")
    calendar = st.text_input("Calendar Link")

st.markdown("---")
st.markdown("#### 📤 Generate")
col1, col2 = st.columns(2)
gen_email = col1.checkbox("📧 Email Sequence", value=True)
gen_li = col1.checkbox("💼 LinkedIn", value=True)
gen_phone = col2.checkbox("📞 Phone Script", value=False)
gen_video = col2.checkbox("🎥 Video Script", value=False)
email_count = st.slider("Emails", 1, 5, 3) if gen_email else 1
tone = st.selectbox("Tone", ["Professional", "Casual", "Bold"])

if st.button("🚀 Generate Outreach", type="primary", use_container_width=True):
    if not name or not company: st.error("Please enter name and company")
    else:
        outputs = []
        if gen_email: outputs.append(f"{email_count} emails with subjects, bodies, timing")
        if gen_li: outputs.append("LinkedIn connection request + InMail")
        if gen_phone: outputs.append("Phone script + voicemail")
        if gen_video: outputs.append("60-sec video script")
        
        prompt = f"""Create personalized outreach:
LEAD: {name} | {title} at {company} | Type: {ltype} | Last: {last or 'Unknown'}
History: {history or 'New contact'} | LinkedIn: {linkedin or 'N/A'}

CONTEXT: {context or 'No additional context'}

GOAL: {goal}
OFFERING: {offering or 'General outreach'}

FROM: {yname or 'N/A'} at {ycompany or 'N/A'} | Calendar: {calendar or 'N/A'}

TONE: {tone}

GENERATE: {', '.join(outputs)}

Be SPECIFIC, reference context. Emails <150 words. Include AI insights: best time, predicted response, best channel."""

        with st.spinner("🚀 Generating..."):
            resp, _, _ = call_claude(prompt, 4000)
            st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)
            st.download_button("📥 Download", resp, f"outreach_{name.replace(' ','_')}.txt")

st.markdown('<a href="mailto:sharpsuite@sharphuman.com?subject=Feedback" style="position:fixed;bottom:20px;right:20px;background:#6366f1;color:white;padding:12px 20px;border-radius:30px;text-decoration:none;">💬 Feedback</a>', unsafe_allow_html=True)
