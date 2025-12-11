"""Sharp Admin - GOD ONLY with Supabase Auth"""
import streamlit as st
import requests
import os

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
GOD_PASSWORD = "G0DHum@n101!!!"

def supabase_sign_in(e, p):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": e, "password": p}, timeout=10)
        d = r.json()
        if r.status_code == 200 and d.get("access_token"): return {"success": True, "user": d.get("user")}
        return {"success": False, "message": d.get("error_description") or "Invalid"}
    except Exception as ex: return {"success": False, "message": str(ex)}

def init_session():
    for k,v in [('authenticated',False),('user',None),('is_god',False)]:
        if k not in st.session_state: st.session_state[k] = v

def get_user_email():
    if st.session_state.user: return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"

def get_all_users():
    """Fetch users from Supabase Auth"""
    if not SUPABASE_SERVICE_KEY:
        return []
    try:
        r = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users", 
            headers={"apikey": SUPABASE_SERVICE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        if r.status_code == 200:
            return r.json().get("users", [])
        return []
    except:
        return []

def render_auth():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}.stTextInput>div>div>input{background:#12121a!important;border:1px solid rgba(239,68,68,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#ef4444,#dc2626)!important;color:white!important;border:none!important;}</style>""", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1.3,1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:40px 0;"><img src="https://sharphuman.com/logo1-3.png" style="width:70px;margin-bottom:16px;"><h1 style="color:white;">Sharp Admin</h1><p style="color:#ef4444;">⚠️ GOD ACCESS ONLY</p></div>""", unsafe_allow_html=True)
        e = st.text_input("Email",key="le")
        p = st.text_input("Password",type="password",key="lp")
        if st.button("🔐 Access Admin",use_container_width=True):
            if p == GOD_PASSWORD:
                st.session_state.authenticated=True
                st.session_state.is_god=True
                st.session_state.user={"email":"GOD"}
                st.rerun()
            elif e and p:
                r=supabase_sign_in(e,p)
                if r["success"]:
                    # Check if user is GOD (you could check against a list of admin emails)
                    st.session_state.authenticated=True
                    st.session_state.user=r["user"]
                    st.session_state.is_god=False  # Regular user, will be blocked
                    st.rerun()
                else:
                    st.error(r["message"])
            else:
                st.error("Invalid credentials")

st.set_page_config(page_title="Sharp Admin",page_icon="⚙️",layout="wide")
init_session()

if not st.session_state.authenticated:
    render_auth()
    st.stop()

# GOD CHECK - Block non-GOD users
if not st.session_state.is_god:
    st.markdown("""<style>.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}</style>""", unsafe_allow_html=True)
    st.error("⛔ ACCESS DENIED - GOD MODE REQUIRED")
    st.markdown("This admin panel is restricted to GOD access only.")
    if st.button("🚪 Logout"):
        st.session_state.authenticated=False
        st.session_state.user=None
        st.session_state.is_god=False
        st.rerun()
    st.stop()

# ============== ADMIN PANEL ==============
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}h1,h2,h3{color:white!important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#12121a!important;border:1px solid rgba(239,68,68,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#ef4444,#dc2626)!important;color:white!important;border:none!important;}p,span,label{color:#e5e5e5!important;}.stat-card{background:#12121a;border:1px solid rgba(239,68,68,0.2);border-radius:12px;padding:20px;text-align:center;}</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<div style='padding:12px;background:rgba(239,68,68,0.1);border-radius:8px;border:1px solid rgba(239,68,68,0.3);'><p style='color:#fca5a5;margin:0;font-size:0.75rem;'>👑 GOD MODE</p><p style='color:white;margin:0;'>{get_user_email()}</p></div>",unsafe_allow_html=True)
    if st.button("🚪 Logout",use_container_width=True): st.session_state.authenticated=False;st.session_state.user=None;st.session_state.is_god=False;st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(239,68,68,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;">Sharp Admin</h1><p style="color:#ef4444;margin:0;">👑 GOD MODE ACTIVE</p></div></div>""", unsafe_allow_html=True)

tab1,tab2,tab3 = st.tabs(["👥 Users","📢 Broadcast","📊 Analytics"])

with tab1:
    st.markdown("### 👥 User Management")
    users = get_all_users()
    if users:
        st.success(f"Found {len(users)} users")
        for u in users[:20]:
            c1,c2,c3 = st.columns([3,2,1])
            c1.write(u.get("email","N/A"))
            c2.write(u.get("created_at","N/A")[:10] if u.get("created_at") else "N/A")
            c3.write("✅" if u.get("email_confirmed_at") else "⏳")
    else:
        st.warning("No users found or SUPABASE_SERVICE_KEY not set")
        st.info("Add SUPABASE_SERVICE_KEY to Railway env vars to enable user management")
    
    st.markdown("---")
    st.markdown("### ➕ Add User Manually")
    new_email = st.text_input("Email")
    new_pass = st.text_input("Password",type="password")
    if st.button("Create User"):
        if new_email and new_pass:
            from requests import post
            r = post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": new_email, "password": new_pass})
            if r.status_code == 200: st.success("User created!")
            else: st.error(f"Failed: {r.json()}")

with tab2:
    st.markdown("### 📢 Broadcast Message")
    st.info("Email broadcast requires email service integration (SendGrid, etc)")
    subject = st.text_input("Subject")
    message = st.text_area("Message",height=150)
    if st.button("📤 Send Broadcast"):
        st.warning("Email service not configured. Add SENDGRID_API_KEY to enable.")

with tab3:
    st.markdown("### 📊 Analytics")
    users = get_all_users()
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f'<div class="stat-card"><h2>{len(users)}</h2><p>Total Users</p></div>',unsafe_allow_html=True)
    confirmed = len([u for u in users if u.get("email_confirmed_at")])
    c2.markdown(f'<div class="stat-card"><h2>{confirmed}</h2><p>Confirmed</p></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><h2>{len(users)-confirmed}</h2><p>Pending</p></div>',unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><h2>9</h2><p>Apps</p></div>',unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("- [Supabase Dashboard](https://supabase.com/dashboard)")
    st.markdown("- [Railway Dashboard](https://railway.app/dashboard)")
    st.markdown("- [Cloudflare DNS](https://dash.cloudflare.com)")
