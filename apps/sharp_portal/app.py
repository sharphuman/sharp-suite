"""Sharp Portal - Main Dashboard"""
import streamlit as st
import requests

st.set_page_config(page_title="Sharp Suite", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"

APPS = [
    ("📝", "JD", "Create job descriptions", "https://jd.sharphuman.com"),
    ("🔍", "Screen", "Screen & rank CVs", "https://screen.sharphuman.com"),
    ("🎯", "Interview", "Interview questions", "https://hire.sharphuman.com"),
    ("🎣", "Source", "Boolean & outreach", "https://outreach.sharphuman.com"),
    ("✍️", "Content", "Content engine", "https://content.sharphuman.com"),
    ("💰", "Sales", "Sales call analysis", "https://sales.sharphuman.com"),
    ("🚀", "Reach", "BD outreach", "https://reach.sharphuman.com"),
    ("🤖", "Assistant", "AI chat", "https://assistant.sharphuman.com"),
]

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], 
[data-testid="stSidebar"], [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div { background: #0f0f14 !important; }
* { font-family: 'Nunito', sans-serif !important; }
[data-testid="stSidebar"] { background: #0f0f14 !important; border-right: 1px solid rgba(99,102,241,0.2); }
.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background: #1a1a24 !important; border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important; color: white !important; font-size: 16px !important; padding: 14px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    padding: 14px 24px !important; font-weight: 600 !important; font-size: 15px !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important; }
.stTabs [data-baseweb="tab-list"] { background: #1a1a24; border-radius: 12px; padding: 6px; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #9ca3af !important; border-radius: 8px !important; padding: 12px 24px !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; }
h1, h2, h3 { color: white !important; }
p, span, label { color: #e5e5e5 !important; }
.nav-link { display: flex; align-items: center; gap: 12px; padding: 12px 16px; margin: 4px 0; border-radius: 10px; color: #9ca3af !important; text-decoration: none !important; font-size: 15px; }
.nav-link:hover { background: rgba(99,102,241,0.15); color: white !important; }
.nav-link.active { background: rgba(99,102,241,0.2); color: white !important; border-left: 3px solid #6366f1; }
.app-card { background: #1a1a24; border: 1px solid rgba(99,102,241,0.2); border-radius: 16px; padding: 24px; min-height: 160px; transition: all 0.3s; text-decoration: none !important; display: block; }
.app-card:hover { transform: translateY(-4px); border-color: #6366f1; box-shadow: 0 12px 40px rgba(99,102,241,0.15); }
.app-icon { font-size: 2.2rem; margin-bottom: 10px; }
.app-title { font-size: 1.1rem; font-weight: 700; color: white !important; margin-bottom: 6px; }
.app-desc { font-size: 0.9rem; color: #9ca3af !important; }
.feedback-modal { background: #1a1a24; border: 1px solid rgba(99,102,241,0.3); border-radius: 16px; padding: 24px; margin: 20px 0; }
</style>
"""

def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("user"):
            return {"success": True, "message": "✅ Check your email to confirm!"}
        return {"success": False, "message": data.get("error_description") or "Sign up failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            return {"success": True, "user": data.get("user")}
        return {"success": False, "message": data.get("error_description") or "Invalid credentials"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def supabase_magic_link(email):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email}, timeout=10)
        if r.status_code == 200:
            return {"success": True, "message": "✨ Login link sent! Check your inbox."}
        return {"success": False, "message": "Failed to send. Try again."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def init_session():
    defaults = {'authenticated': False, 'user': None, 'is_god': False, 'show_feedback': False}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_user_email():
    if st.session_state.is_god:
        return "GOD MODE"
    if st.session_state.user:
        return st.session_state.user.get("email", "User")
    return "User"

def render_sidebar(current="Portal"):
    st.markdown(f"""<div style='padding:16px 12px;'>
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:20px;'>
            <img src="https://sharphuman.com/logo1-3.png" style="width:40px;">
            <span style='color:white;font-size:1.2rem;font-weight:700;'>Sharp Suite</span>
        </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280;font-size:12px;padding:0 12px;margin-bottom:8px;'>APPS</p>", unsafe_allow_html=True)
    for icon, name, desc, url in APPS:
        active = "active" if name == current else ""
        st.markdown(f'<a href="{url}" target="_self" class="nav-link {active}"><span>{icon}</span><span>{name}</span></a>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""<div style='padding:12px;background:rgba(99,102,241,0.1);border-radius:10px;margin:12px 0;'>
        <p style='color:#6b7280;font-size:12px;margin:0;'>Logged in as</p>
        <p style='color:white;font-size:14px;margin:4px 0 0;font-weight:600;'>{get_user_email()}</p>
    </div>""", unsafe_allow_html=True)

def render_feedback():
    if st.session_state.get('show_feedback', False):
        st.markdown("<div class='feedback-modal'>", unsafe_allow_html=True)
        st.markdown("### 💬 Send Feedback")
        feedback_type = st.selectbox("Type", ["General Feedback", "Report a Bug", "Feature Request / Enhancement"], key="fb_type")
        feedback_text = st.text_area("Your feedback", height=120, placeholder="Tell us what's on your mind...", key="fb_text")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Submit", use_container_width=True, key="fb_submit"):
                if feedback_text:
                    st.success("✅ Thanks for your feedback!")
                    st.session_state.show_feedback = False
                    st.rerun()
                else:
                    st.warning("Please enter your feedback")
        with col2:
            if st.button("Cancel", use_container_width=True, key="fb_cancel"):
                st.session_state.show_feedback = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def render_auth():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 40px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:90px;margin-bottom:24px;">
            <h1 style="color:white;margin:0 0 8px;font-size:2.4rem;">Sharp Suite</h1>
            <p style="color:#9ca3af;font-size:1.1rem;">AI-Powered Recruiting Tools</p>
        </div>""", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Log In", "✨ Sign Up"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@company.com", key="le")
            password = st.text_input("Password", type="password", placeholder="Your password", key="lp")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 Log In", use_container_width=True):
                if password == GOD_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_god = True
                    st.session_state.user = {"email": "GOD"}
                    st.rerun()
                elif email and password:
                    result = supabase_sign_in(email, password)
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = result["user"]
                        st.rerun()
                    else:
                        st.error(result["message"])
            
            st.markdown("""<div style='display:flex;align-items:center;margin:28px 0;'>
                <div style='flex:1;height:1px;background:rgba(255,255,255,0.1);'></div>
                <span style='padding:0 16px;color:#6b7280;font-size:14px;'>or sign in without password</span>
                <div style='flex:1;height:1px;background:rgba(255,255,255,0.1);'></div>
            </div>""", unsafe_allow_html=True)
            
            st.markdown("""<p style='color:#9ca3af;font-size:14px;text-align:center;margin-bottom:12px;'>
                📧 Enter your email to receive a secure login link
            </p>""", unsafe_allow_html=True)
            
            magic_email = st.text_input("Email", placeholder="you@company.com", key="me", label_visibility="collapsed")
            
            if st.button("✨ Send Login Link", use_container_width=True, key="ml"):
                if magic_email:
                    result = supabase_magic_link(magic_email)
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                else:
                    st.warning("Please enter your email")
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            se = st.text_input("Email", placeholder="you@company.com", key="se")
            sp = st.text_input("Password", type="password", placeholder="Min 6 characters", key="sp")
            sc = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="sc")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🎉 Create Account", use_container_width=True):
                if not se or not sp:
                    st.warning("Please fill all fields")
                elif len(sp) < 6:
                    st.warning("Password must be 6+ characters")
                elif sp != sc:
                    st.error("Passwords don't match")
                else:
                    result = supabase_sign_up(se, sp)
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])

# Initialize
init_session()

if not st.session_state.authenticated:
    render_auth()
    st.stop()

# Main app
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

with st.sidebar:
    render_sidebar("Portal")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.is_god = False
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💬 Feedback", use_container_width=True):
        st.session_state.show_feedback = not st.session_state.get('show_feedback', False)
        st.rerun()

# Header
st.markdown(f"""<div style='display:flex;align-items:center;gap:16px;padding:24px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:32px;'>
    <img src='https://sharphuman.com/logo1-3.png' style='width:55px;'>
    <div>
        <h1 style='margin:0;font-size:2rem;'>Sharp Suite</h1>
        <p style='color:#9ca3af;margin:0;font-size:1rem;'>Welcome back, {get_user_email()}</p>
    </div>
</div>""", unsafe_allow_html=True)

render_feedback()

st.markdown("""<div style='background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15));border:1px solid rgba(99,102,241,0.2);border-radius:16px;padding:40px;margin-bottom:32px;text-align:center;'>
    <h2 style='margin:0 0 12px;color:white;font-size:1.8rem;'>Your AI Recruiting Toolkit 🚀</h2>
    <p style='color:#9ca3af;margin:0;font-size:1.1rem;'>Select an app to get started</p>
</div>""", unsafe_allow_html=True)

st.markdown("### 🛠️ Your Apps")
cols = st.columns(4)
for i, (icon, name, desc, url) in enumerate(APPS):
    with cols[i % 4]:
        st.markdown(f'''<a href="{url}" target="_blank" class="app-card">
            <div class="app-icon">{icon}</div>
            <div class="app-title">{name}</div>
            <div class="app-desc">{desc}</div>
        </a>''', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.is_god:
    st.markdown("---")
    st.markdown("### ⚙️ Admin")
    st.markdown('''<a href="https://admin.sharphuman.com" target="_blank" class="app-card" style="max-width:300px;border-color:rgba(239,68,68,0.3);">
        <div class="app-icon">⚙️</div>
        <div class="app-title">Admin</div>
        <div class="app-desc">User management & analytics</div>
    </a>''', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""<p style='text-align:center;color:#6b7280;font-size:14px;'>© 2024 Sharp Human • <a href='https://sharphuman.com' style='color:#6366f1;'>sharphuman.com</a></p>""", unsafe_allow_html=True)
