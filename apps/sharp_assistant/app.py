"""Sharp Assistant - AI Chat Partner with Supabase Auth"""
import streamlit as st
import requests
import os

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
GOD_PASSWORD = "G0DHum@n101!!!"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def supabase_sign_in(e, p):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": e, "password": p}, timeout=10)
        d = r.json()
        if r.status_code == 200 and d.get("access_token"): return {"success": True, "user": d.get("user")}
        return {"success": False, "message": d.get("error_description") or "Invalid"}
    except Exception as ex: return {"success": False, "message": str(ex)}

def supabase_sign_up(e, p):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": e, "password": p}, timeout=10)
        d = r.json()
        if r.status_code == 200 and d.get("user"): return {"success": True, "message": "Check email!"}
        return {"success": False, "message": d.get("error_description") or "Failed"}
    except Exception as ex: return {"success": False, "message": str(ex)}

def supabase_magic_link(e):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/magiclink", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": e}, timeout=10)
        return {"success": r.status_code == 200, "message": "Magic link sent!" if r.status_code == 200 else "Failed"}
    except Exception as ex: return {"success": False, "message": str(ex)}

def init_session():
    for k,v in [('authenticated',False),('user',None),('is_god',False),('messages',[])]:
        if k not in st.session_state: st.session_state[k] = v

def get_user_email():
    if st.session_state.user: return st.session_state.user.get("email", "User")
    return "GOD" if st.session_state.is_god else "User"

def call_claude_chat(messages):
    if not ANTHROPIC_API_KEY: return "Error: API key not set"
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, json={"model": "claude-sonnet-4-20250514", "max_tokens": 2000, "system": "You are Sharp Assistant, an expert AI recruiting partner. Help with sourcing, screening, interviewing, job descriptions, offer negotiation, employer branding, and all talent acquisition topics. Be concise, practical, and actionable.", "messages": messages}, timeout=120)
        if r.status_code == 200: return r.json()["content"][0]["text"]
        return f"Error: {r.status_code}"
    except Exception as ex: return f"Error: {str(ex)}"

def render_auth():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}.stTextInput>div>div>input{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}.stTabs [data-baseweb="tab-list"]{background:#12121a;}.stTabs [aria-selected="true"]{background:rgba(99,102,241,0.3)!important;}</style>""", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1.3,1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:40px 0;"><img src="https://sharphuman.com/logo1-3.png" style="width:70px;margin-bottom:16px;"><h1 style="color:white;">Sharp Assistant</h1><p style="color:#9ca3af;">AI Recruiting Partner</p></div>""", unsafe_allow_html=True)
        t1,t2 = st.tabs(["🔐 Log In","✨ Sign Up"])
        with t1:
            e,p = st.text_input("Email",key="le"), st.text_input("Password",type="password",key="lp")
            if st.button("Log In",use_container_width=True):
                if p == GOD_PASSWORD: st.session_state.authenticated=True;st.session_state.is_god=True;st.session_state.user={"email":"GOD"};st.rerun()
                elif e and p:
                    r=supabase_sign_in(e,p)
                    if r["success"]: st.session_state.authenticated=True;st.session_state.user=r["user"];st.rerun()
                    else: st.error(r["message"])
            st.markdown("<p style='text-align:center;color:#6b7280;'>— or —</p>",unsafe_allow_html=True)
            me=st.text_input("",key="me",placeholder="Email for magic link")
            if st.button("✨ Magic Link",use_container_width=True,key="ml"):
                if me:
                    r = supabase_magic_link(me)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])
        with t2:
            se,sp,sc = st.text_input("Email",key="se"),st.text_input("Password",type="password",key="sp"),st.text_input("Confirm",type="password",key="sc")
            if st.button("Create Account",use_container_width=True):
                if sp!=sc: st.error("Passwords don't match")
                elif len(sp)<6: st.warning("6+ chars")
                elif se and sp: r=supabase_sign_up(se,sp)
                    if r["success"]:
                        st.success(r["message"])
                    else:
                        st.error(r["message"])

st.set_page_config(page_title="Sharp Assistant",page_icon="🤖",layout="wide")
init_session()
if not st.session_state.authenticated: render_auth();st.stop()

st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}h1,h2,h3{color:white!important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}p,span,label{color:#e5e5e5!important;}.chat-msg{padding:16px;border-radius:12px;margin:8px 0;}.user-msg{background:rgba(99,102,241,0.2);border:1px solid rgba(99,102,241,0.3);}.assistant-msg{background:#12121a;border:1px solid rgba(99,102,241,0.15);}</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<div style='padding:12px;background:rgba(99,102,241,0.1);border-radius:8px;'><p style='color:#9ca3af;margin:0;font-size:0.75rem;'>Logged in</p><p style='color:white;margin:0;'>{get_user_email()}</p></div>",unsafe_allow_html=True)
    if st.button("🚪 Logout",use_container_width=True): st.session_state.authenticated=False;st.session_state.user=None;st.session_state.is_god=False;st.session_state.messages=[];st.rerun()
    st.markdown("---")
    if st.button("🗑️ Clear Chat",use_container_width=True): st.session_state.messages=[];st.rerun()
    st.markdown("### 💡 Quick Questions")
    for q in ["How do I source passive candidates?","Best interview questions for engineers?","How to reduce time-to-hire?","Write a rejection email"]:
        if st.button(q,key=q,use_container_width=True):
            st.session_state.messages.append({"role":"user","content":q})
            st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;">Sharp Assistant</h1><p style="color:#9ca3af;margin:0;">Your AI Recruiting Partner</p></div></div>""", unsafe_allow_html=True)

# Chat display
for msg in st.session_state.messages:
    cls = "user-msg" if msg["role"]=="user" else "assistant-msg"
    icon = "👤" if msg["role"]=="user" else "🤖"
    st.markdown(f'<div class="chat-msg {cls}">{icon} {msg["content"]}</div>',unsafe_allow_html=True)

# Input
user_input = st.chat_input("Ask me anything about recruiting...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.spinner("🤖 Thinking..."):
        response = call_claude_chat(st.session_state.messages)
        st.session_state.messages.append({"role":"assistant","content":response})
    st.rerun()

if not st.session_state.messages:
    st.markdown("""<div style="text-align:center;padding:60px;color:#6b7280;"><p style="font-size:1.2rem;">👋 Hi! I'm your AI recruiting assistant.</p><p>Ask me anything about sourcing, screening, interviewing, or talent acquisition!</p></div>""",unsafe_allow_html=True)
