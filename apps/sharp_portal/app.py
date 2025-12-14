"""Sharp Portal - Dashboard with Full Auth"""
import streamlit as st
import requests

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"

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
            return {"success": True, "message": "✨ Magic link sent! Check your inbox."}
        return {"success": False, "message": "Failed to send magic link"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def init_session():
    for k, v in [('authenticated', False), ('user', None), ('is_god', False)]:
        if k not in st.session_state:
            st.session_state[k] = v

def get_user_email():
    if st.session_state.is_god:
        return "GOD MODE"
    if st.session_state.user:
        return st.session_state.user.get("email", "User")
    return "User"

def render_auth():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%); }
    * { font-family: 'Nunito', sans-serif !important; }
    html, body { font-size: 16px !important; }
    .stTextInput > div > div > input { 
        background: rgba(255,255,255,0.05) !important; 
        border: 1px solid rgba(99,102,241,0.3) !important; 
        border-radius: 10px !important; 
        color: white !important; 
        padding: 14px 18px !important;
        font-size: 16px !important;
    }
    .stButton > button { 
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; 
        color: white !important; 
        border: none !important; 
        border-radius: 10px !important; 
        padding: 14px 28px !important; 
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    .stButton > button:hover { 
        transform: translateY(-2px) !important; 
        box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important; 
    }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 6px; }
    .stTabs [data-baseweb="tab"] { 
        background: transparent !important; 
        color: #9ca3af !important; 
        border-radius: 8px !important; 
        padding: 12px 28px !important; 
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; 
        color: white !important; 
    }
    p, span, label, div { font-size: 15px !important; }
    h1 { font-size: 2.2rem !important; }
    h2 { font-size: 1.8rem !important; }
    h3 { font-size: 1.4rem !important; }
    </style>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:50px 0 40px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:90px;margin-bottom:20px;">
            <h1 style="color:white;margin:0 0 8px;font-size:2.2rem;">Sharp Suite</h1>
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
                    r = supabase_sign_in(email, password)
                    if r["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = r["user"]
                        st.rerun()
                    else:
                        st.error(r["message"])
            
            st.markdown("""<div style='display:flex;align-items:center;margin:28px 0;'>
                <div style='flex:1;height:1px;background:rgba(255,255,255,0.1);'></div>
                <span style='padding:0 16px;color:#6b7280;font-size:14px;'>or sign in without password</span>
                <div style='flex:1;height:1px;background:rgba(255,255,255,0.1);'></div>
            </div>""", unsafe_allow_html=True)
            
            st.markdown("""<p style='color:#9ca3af;font-size:14px;margin-bottom:12px;text-align:center;'>
                📧 <strong>Passwordless Login:</strong> Enter your email below and we'll send you a secure link to sign in instantly.
            </p>""", unsafe_allow_html=True)
            
            magic_email = st.text_input("Email for passwordless login", placeholder="you@company.com", key="me", label_visibility="collapsed")
            if st.button("✨ Send Login Link", use_container_width=True, key="ml"):
                if magic_email:
                    result = supabase_magic_link(magic_email)
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                else:
                    st.warning("Please enter your email address")
        
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
                    r = supabase_sign_up(se, sp)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
        
        st.markdown("""<p style='text-align:center;color:#6b7280;margin-top:28px;font-size:14px;'>
            Need help? <a href='mailto:support@sharphuman.com' style='color:#6366f1;'>support@sharphuman.com</a>
        </p>""", unsafe_allow_html=True)

st.set_page_config(page_title="Sharp Suite", page_icon="⚡", layout="wide")
init_session()

if not st.session_state.authenticated:
    render_auth()
    st.stop()

# Dashboard
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
html, body { font-size: 16px !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%); }
h1,h2,h3 { color: white !important; }
h1 { font-size: 2rem !important; }
h2 { font-size: 1.6rem !important; }
h3 { font-size: 1.3rem !important; }
p, span, label { font-size: 15px !important; }
.app-card { 
    background: rgba(255,255,255,0.03); 
    border: 1px solid rgba(99,102,241,0.2); 
    border-radius: 16px; 
    padding: 28px; 
    height: 180px; 
    transition: all 0.3s; 
    text-decoration: none !important; 
    display: block; 
}
.app-card:hover { 
    transform: translateY(-4px); 
    border-color: #6366f1; 
    box-shadow: 0 12px 40px rgba(99,102,241,0.15); 
}
.app-icon { font-size: 2.5rem; margin-bottom: 12px; }
.app-title { font-size: 1.15rem; font-weight: 700; color: white !important; margin-bottom: 8px; }
.app-desc { font-size: 0.95rem; color: #9ca3af !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"""<div style='padding:18px;background:rgba(99,102,241,0.1);border-radius:12px;border:1px solid rgba(99,102,241,0.2);'>
        <p style='color:#9ca3af;margin:0 0 6px;font-size:0.85rem;'>Logged in as</p>
        <p style='color:white;margin:0;font-weight:600;font-size:1rem;'>{get_user_email()}</p>
        {'<p style="color:#f59e0b;margin:6px 0 0;font-size:0.85rem;">👑 GOD MODE</p>' if st.session_state.is_god else ''}
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.is_god = False
        st.rerun()

st.markdown(f"""<div style='display:flex;align-items:center;gap:16px;padding:24px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:32px;'>
    <img src='https://sharphuman.com/logo1-3.png' style='width:55px;'>
    <div>
        <h1 style='margin:0;font-size:2rem;'>Sharp Suite</h1>
        <p style='color:#9ca3af;margin:0;font-size:1rem;'>Welcome back, {get_user_email()}</p>
    </div>
</div>""", unsafe_allow_html=True)

st.markdown("""<div style='background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));border:1px solid rgba(99,102,241,0.2);border-radius:16px;padding:36px;margin-bottom:32px;text-align:center;'>
    <h2 style='margin:0 0 10px;color:white;font-size:1.6rem;'>Your AI Recruiting Toolkit 🚀</h2>
    <p style='color:#9ca3af;margin:0;font-size:1.05rem;'>Select an app to get started</p>
</div>""", unsafe_allow_html=True)

APPS = [
    ("📝", "Sharp JD", "AI job descriptions", "https://jd.sharphuman.com"),
    ("🔍", "Sharp Screen", "CV screening & ranking", "https://screen.sharphuman.com"),
    ("🎯", "Sharp Interview", "Questions & analysis", "https://hire.sharphuman.com"),
    ("🎣", "Sharp Source", "Boolean & outreach", "https://outreach.sharphuman.com"),
    ("✍️", "Sharp Content", "Content engine", "https://content.sharphuman.com"),
    ("💰", "Sharp Sales", "Sales call analysis", "https://sales.sharphuman.com"),
    ("🚀", "Sharp Reach", "BD & leads", "https://reach.sharphuman.com"),
    ("🤖", "Sharp Assistant", "AI chat partner", "https://assistant.sharphuman.com"),
]

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
        <div class="app-title">Sharp Admin</div>
        <div class="app-desc">Users & analytics</div>
    </a>''', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""<p style='text-align:center;color:#6b7280;font-size:14px;'>
    © 2024 Sharp Human • <a href='https://sharphuman.com' style='color:#6366f1;'>sharphuman.com</a>
</p>""", unsafe_allow_html=True)
