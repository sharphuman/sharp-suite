"""
Sharp Assistant - AI Recruiting Partner
STANDALONE VERSION
"""
import streamlit as st
import requests
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOD_PASSWORD = "G0DHum@n101!!!"
DEMO_PASSWORD = "D3M0Human101!!!"

SYSTEM = "You are Sharp Assistant, an expert AI recruiting partner. Expertise: talent acquisition, sourcing, interviewing, compensation, employment law, ATS, candidate experience, employer branding, diversity hiring, agency recruiting, BD. Be helpful, practical, concise."

def call_claude(prompt, system=SYSTEM, max_tokens=2000):
    if not ANTHROPIC_API_KEY: return "Error: ANTHROPIC_API_KEY not set"
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "system": system, "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        if r.status_code == 200: return r.json()["content"][0]["text"]
        return f"API Error: {r.status_code}"
    except Exception as e: return f"Error: {str(e)}"

def check_auth():
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False; st.session_state.access_level = None
    return st.session_state.authenticated

def login_form():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}*{font-family:'Nunito',sans-serif!important;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:60px 0 40px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="color:white;">Sharp Assistant</h1><p style="color:#9ca3af;">AI Recruiting Partner</p></div>""", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", key="pwd")
        if st.button("🚀 Access", type="primary", use_container_width=True):
            if password == GOD_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "god"; st.rerun()
            elif password == DEMO_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "demo"; st.rerun()
            else: st.error("Invalid password")

def apply_styles():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}h1,h2,h3{color:#fff!important;}p,span,label{color:#e5e5e5!important;}[data-testid="stSidebar"]{background:#0a0a0f;}.user-msg{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;padding:16px 20px;border-radius:12px;margin:8px 0 8px 20%;}.asst-msg{background:#1a1a2e;border:1px solid rgba(99,102,241,0.2);color:#e5e5e5;padding:16px 20px;border-radius:12px;margin:8px 20% 8px 0;}</style>""", unsafe_allow_html=True)

st.set_page_config(page_title="Sharp Assistant", page_icon="🤖", layout="wide")

if not check_auth(): login_form(); st.stop()

apply_styles()

if 'messages' not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.markdown(f"**{st.session_state.access_level.upper()}**")
    if st.button("🚪 Logout"): st.session_state.authenticated = False; st.rerun()
    st.markdown("---")
    st.markdown("### 💡 Quick Questions")
    for q in ["How to negotiate counteroffer?", "Market rate for Senior PM?", "Write rejection email", "Handle no-show candidate", "Boolean for Python devs"]:
        if st.button(q, key=q[:10], use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;color:white;">Sharp Assistant</h1><p style="color:#9ca3af;margin:0;">Ask Me Anything About Recruiting</p></div></div>""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""<div style="text-align:center;padding:60px;color:#6b7280;"><p style="font-size:3rem;">🤖</p><h3 style="color:#9ca3af;">Hi! I'm your AI recruiting partner.</h3><p>Ask me anything about recruiting, hiring, sourcing, or talent strategy.</p></div>""", unsafe_allow_html=True)
else:
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f'<div class="user-msg">{m["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="asst-msg">{m["content"]}</div>', unsafe_allow_html=True)

user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    context = "\n".join([f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}" for m in st.session_state.messages[-10:]])
    with st.spinner("Thinking..."):
        response = call_claude(f"Conversation:\n{context}\n\nRespond helpfully and concisely.")
        st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

st.markdown('<a href="mailto:sharpsuite@sharphuman.com?subject=Feedback" style="position:fixed;bottom:20px;right:20px;background:#6366f1;color:white;padding:12px 20px;border-radius:30px;text-decoration:none;">💬 Feedback</a>', unsafe_allow_html=True)
