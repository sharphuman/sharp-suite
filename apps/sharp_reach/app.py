"""Sharp Reach - BD Outreach with Supabase Auth"""
import streamlit as st
import requests
import os
import concurrent.futures

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def supabase_sign_in(e, p):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", 
                         headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, 
                         json={"email": e, "password": p}, timeout=10)
        d = r.json()
        if r.status_code == 200 and d.get("access_token"):
            return {"success": True, "user": d.get("user")}
        return {"success": False, "message": d.get("error_description") or "Invalid credentials"}
    except Exception as ex:
        return {"success": False, "message": str(ex)}

def supabase_sign_up(e, p):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup", 
                         headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, 
                         json={"email": e, "password": p}, timeout=10)
        d = r.json()
        if r.status_code == 200 and d.get("user"):
            return {"success": True, "message": "Check email!"}
        return {"success": False, "message": d.get("error_description") or "Failed"}
    except Exception as ex:
        return {"success": False, "message": str(ex)}

def supabase_magic_link(e):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink", 
                         headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, 
                         json={"email": e}, timeout=10)
        if r.status_code == 200:
            return {"success": True, "message": "✨ Login link sent! Check your inbox."}
        return {"success": False, "message": "Failed to send"}
    except Exception as ex:
        return {"success": False, "message": str(ex)}

def init_session():
    for k, v in [('authenticated', False), ('user', None), ('is_god', False)]:
        if k not in st.session_state:
            st.session_state[k] = v

def get_user_email():
    if st.session_state.user:
        return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"

def call_claude(prompt, max_tokens=2000):
    if not ANTHROPIC_API_KEY:
        return "Error: API key not set"
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
                         timeout=60)
        if r.status_code == 200:
            return r.json()["content"][0]["text"]
        return f"Error: {r.status_code}"
    except Exception as ex:
        return f"Error: {str(ex)}"

def render_auth():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f, #0f0f1a); }
    * { font-family: 'Nunito', sans-serif !important; }
    .stTextInput > div > div > input { 
        background: #12121a !important; 
        border: 1px solid rgba(99,102,241,0.3) !important; 
        color: white !important; 
    }
    .stButton > button { 
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; 
        color: white !important; 
        border: none !important; 
    }
    .stTabs [data-baseweb="tab-list"] { background: #12121a; }
    .stTabs [aria-selected="true"] { background: rgba(99,102,241,0.3) !important; }
    </style>""", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:40px 0;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:70px;margin-bottom:16px;">
            <h1 style="color:white;">Sharp Reach</h1>
            <p style="color:#9ca3af;">BD & Lead Outreach</p>
        </div>""", unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        
        with t1:
            e = st.text_input("Email", key="le")
            p = st.text_input("Password", type="password", key="lp")
            
            if st.button("Log In", use_container_width=True):
                if p == GOD_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_god = True
                    st.session_state.user = {"email": "GOD"}
                    st.rerun()
                elif e and p:
                    r = supabase_sign_in(e, p)
                    if r["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = r["user"]
                        st.rerun()
                    else:
                        st.error(r["message"])
            
            st.markdown("<p style='text-align:center;color:#6b7280;'>— or sign in without password —</p>", unsafe_allow_html=True)
            st.markdown("<p style='color:#9ca3af;font-size:13px;text-align:center;'>Enter email to receive a secure login link</p>", unsafe_allow_html=True)
            
            me = st.text_input("Email for login link", key="me", placeholder="you@company.com", label_visibility="collapsed")
            if st.button("✨ Send Login Link", use_container_width=True, key="ml"):
                if me:
                    r = supabase_magic_link(me)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
                else:
                    st.warning("Please enter your email")
        
        with t2:
            se = st.text_input("Email", key="se")
            sp = st.text_input("Password", type="password", key="sp")
            sc = st.text_input("Confirm", type="password", key="sc")
            
            if st.button("Create Account", use_container_width=True):
                if sp != sc:
                    st.error("Passwords don't match")
                elif len(sp) < 6:
                    st.warning("6+ chars required")
                elif se and sp:
                    r = supabase_sign_up(se, sp)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])

st.set_page_config(page_title="Sharp Reach", page_icon="🚀", layout="wide")
init_session()

if not st.session_state.authenticated:
    render_auth()
    st.stop()

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f, #0f0f1a); }
h1, h2, h3 { color: white !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { 
    background: #12121a !important; 
    border: 1px solid rgba(99,102,241,0.3) !important; 
    color: white !important; 
}
.stButton > button { 
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; 
    color: white !important; 
    border: none !important; 
}
.output-box { 
    background: #12121a; 
    border: 1px solid rgba(99,102,241,0.2); 
    border-radius: 12px; 
    padding: 24px; 
    margin: 16px 0; 
}
p, span, label { color: #e5e5e5 !important; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"""<div style='padding:12px;background:rgba(99,102,241,0.1);border-radius:8px;'>
        <p style='color:#9ca3af;margin:0;font-size:0.75rem;'>Logged in</p>
        <p style='color:white;margin:0;'>{get_user_email()}</p>
    </div>""", unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.is_god = False
        st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:45px;">
    <div>
        <h1 style="margin:0;">Sharp Reach</h1>
        <p style="color:#9ca3af;margin:0;">Multi-Channel BD Outreach</p>
    </div>
</div>""", unsafe_allow_html=True)

st.markdown("### 🎯 Lead Information")
c1, c2, c3 = st.columns(3)
name = c1.text_input("Lead Name")
company = c1.text_input("Company")
title = c2.text_input("Title")
industry = c2.text_input("Industry")
pain = c3.text_area("Pain points/context", height=68)
your_offer = c3.text_input("Your offering")

st.markdown("---")
st.markdown("### 📤 Generate Outreach")

# Individual channel buttons instead of one massive generation
col1, col2, col3, col4 = st.columns(4)

with col1:
    email_btn = st.button("📧 Email Sequence", use_container_width=True)
with col2:
    phone_btn = st.button("📞 Phone Script", use_container_width=True)
with col3:
    linkedin_btn = st.button("💼 LinkedIn", use_container_width=True)
with col4:
    video_btn = st.button("🎬 Video Script", use_container_width=True)

insights_btn = st.button("🧠 AI Insights", use_container_width=True)
all_btn = st.button("🚀 Generate All Channels", type="primary", use_container_width=True)

context = f"Lead: {name}, {title} at {company} ({industry}). Pain: {pain}. Offering: {your_offer}"

if name and company:
    # Individual channel generation
    if email_btn:
        with st.spinner("📧 Generating email sequence..."):
            st.markdown("#### 📧 Email Sequence")
            result = call_claude(f"Generate a 3-email BD sequence for {context}. Include subject lines, email bodies, and recommended timing between emails.")
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
    
    if phone_btn:
        with st.spinner("📞 Generating phone script..."):
            st.markdown("#### 📞 Phone Script")
            result = call_claude(f"Generate a cold call script for {context}. Include opening, pitch, objection handling, and close.")
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
    
    if linkedin_btn:
        with st.spinner("💼 Generating LinkedIn messages..."):
            st.markdown("#### 💼 LinkedIn")
            result = call_claude(f"Generate a LinkedIn connection request (max 300 characters) and a follow-up InMail for {context}.")
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
    
    if video_btn:
        with st.spinner("🎬 Generating video script..."):
            st.markdown("#### 🎬 Video Script")
            result = call_claude(f"Generate a 60-second personalized video script for {context}.")
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
    
    if insights_btn:
        with st.spinner("🧠 Generating insights..."):
            st.markdown("#### 🧠 AI Insights")
            result = call_claude(f"For {context}: Provide best time to reach out, predicted response rate, recommended channel priority, and personalization tips.")
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
    
    # Generate all - but one at a time with progress
    if all_btn:
        progress = st.progress(0, text="Starting multi-channel generation...")
        
        st.markdown("#### 📧 Email Sequence")
        progress.progress(10, text="📧 Generating email sequence...")
        email_result = call_claude(f"Generate a 3-email BD sequence for {context}. Include subject lines, email bodies, and recommended timing.")
        st.markdown(f'<div class="output-box">{email_result}</div>', unsafe_allow_html=True)
        
        st.markdown("#### 📞 Phone Script")
        progress.progress(30, text="📞 Generating phone script...")
        phone_result = call_claude(f"Generate a cold call script for {context}. Include opening, pitch, objection handling, and close.")
        st.markdown(f'<div class="output-box">{phone_result}</div>', unsafe_allow_html=True)
        
        st.markdown("#### 💼 LinkedIn")
        progress.progress(50, text="💼 Generating LinkedIn messages...")
        linkedin_result = call_claude(f"Generate a LinkedIn connection request (max 300 characters) and a follow-up InMail for {context}.")
        st.markdown(f'<div class="output-box">{linkedin_result}</div>', unsafe_allow_html=True)
        
        st.markdown("#### 🎬 Video Script")
        progress.progress(70, text="🎬 Generating video script...")
        video_result = call_claude(f"Generate a 60-second personalized video script for {context}.")
        st.markdown(f'<div class="output-box">{video_result}</div>', unsafe_allow_html=True)
        
        st.markdown("#### 🧠 AI Insights")
        progress.progress(90, text="🧠 Generating insights...")
        insights_result = call_claude(f"For {context}: Best time to reach, predicted response rate, recommended channel priority, personalization tips.")
        st.markdown(f'<div class="output-box">{insights_result}</div>', unsafe_allow_html=True)
        
        progress.progress(100, text="✅ All channels generated!")
        st.success("🎉 Multi-channel outreach generated successfully!")

elif email_btn or phone_btn or linkedin_btn or video_btn or insights_btn or all_btn:
    st.warning("Please enter lead name and company")
