"""
Sharp Content - Full Content Engine
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
        st.markdown("""<div style="text-align:center;padding:60px 0 40px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="color:white;">Sharp Content</h1><p style="color:#9ca3af;">Full Stack Content Engine</p></div>""", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", key="pwd")
        if st.button("🚀 Access", type="primary", use_container_width=True):
            if password == GOD_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "god"; st.rerun()
            elif password == DEMO_PASSWORD: st.session_state.authenticated = True; st.session_state.access_level = "demo"; st.rerun()
            else: st.error("Invalid password")

def apply_styles():
    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');*{font-family:'Nunito',sans-serif!important;}.stApp{background:linear-gradient(135deg,#0a0a0f,#0f0f1a);}h1,h2,h3{color:#fff!important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#12121a!important;border:1px solid rgba(99,102,241,0.3)!important;color:white!important;}.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:white!important;border:none!important;}.output-box{background:#12121a;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:24px;margin:16px 0;}p,span,label{color:#e5e5e5!important;}</style>""", unsafe_allow_html=True)

st.set_page_config(page_title="Sharp Content", page_icon="✍️", layout="wide")

if not check_auth(): login_form(); st.stop()

apply_styles()

with st.sidebar:
    st.markdown(f"**{st.session_state.access_level.upper()}**")
    if st.button("🚪 Logout"): st.session_state.authenticated = False; st.rerun()

st.markdown("""<div style="display:flex;align-items:center;gap:12px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:24px;"><img src="https://sharphuman.com/logo1-3.png" style="width:45px;"><div><h1 style="margin:0;color:white;">Sharp Content</h1><p style="color:#9ca3af;margin:0;">Write Once, Publish Everywhere</p></div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📝 Writer", "✨ Refiner", "📱 Social", "📧 Email", "🎬 Video", "🔄 Repurpose"])

with tab1:
    st.markdown("### Generate articles")
    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input("Topic", placeholder="The Future of AI in Recruiting")
        context = st.text_area("Context", height=120)
        audience = st.text_input("Audience", placeholder="HR Leaders")
    with col2:
        words = st.slider("Words", 300, 2500, 1000, 100)
        tone = st.selectbox("Tone", ["Professional", "Conversational", "Bold", "Educational"])
        seo = st.checkbox("SEO description", value=True)
    
    if st.button("📝 Generate", type="primary", use_container_width=True, key="w"):
        if topic:
            prompt = f"Write ~{words} word article. Topic: {topic}. Audience: {audience or 'Professionals'}. Tone: {tone}. Context: {context or 'N/A'}. Include headline, hook, subheadings, takeaways. {'Add SEO meta.' if seo else ''}"
            with st.spinner("📝..."):
                resp, _, _ = call_claude(prompt, 3500)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)
                st.download_button("📥 Download", resp, "article.md")

with tab2:
    st.markdown("### Refine content")
    draft = st.text_area("Paste draft", height=300)
    goal = st.selectbox("Goal", ["Polish", "Make Concise", "Expand", "Change Tone", "Fix Grammar"])
    
    if st.button("✨ Refine", type="primary", use_container_width=True, key="r"):
        if draft:
            prompt = f"Refine this. Goal: {goal}.\n\n{draft}\n\nProvide refined version and changes made."
            with st.spinner("✨..."):
                resp, _, _ = call_claude(prompt, 3000)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("### Social posts")
    source = st.text_area("Source content", height=200)
    platforms = st.multiselect("Platforms", ["LinkedIn", "Twitter/X", "Facebook", "Instagram", "TikTok"], default=["LinkedIn"])
    
    if st.button("📱 Generate", type="primary", use_container_width=True, key="s"):
        if source:
            prompt = f"Generate social posts for {', '.join(platforms)}:\n{source}\n\n2 posts per platform with hooks and hashtags."
            with st.spinner("📱..."):
                resp, _, _ = call_claude(prompt, 2500)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)

with tab4:
    st.markdown("### Email/Newsletter")
    etype = st.selectbox("Type", ["Newsletter", "Announcement", "Welcome Sequence", "Re-engagement"])
    etopic = st.text_input("Topic")
    econtent = st.text_area("Key points", height=150)
    
    if st.button("📧 Generate", type="primary", use_container_width=True, key="em"):
        if etopic:
            prompt = f"Create {etype} email. Topic: {etopic}. Content: {econtent or 'General'}. Include 3 subject lines, preview text, body, CTA."
            with st.spinner("📧..."):
                resp, _, _ = call_claude(prompt, 2000)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)

with tab5:
    st.markdown("### Video/Podcast scripts")
    vtype = st.selectbox("Type", ["YouTube (5-10 min)", "YouTube Short (60 sec)", "Loom (2-3 min)", "Podcast Outline", "LinkedIn Video"])
    vtopic = st.text_input("Topic", key="vt")
    vcontext = st.text_area("Key points", height=150, key="vc")
    
    if st.button("🎬 Generate", type="primary", use_container_width=True, key="v"):
        if vtopic:
            prompt = f"Create {vtype} script. Topic: {vtopic}. Context: {vcontext or 'N/A'}. Include hook, full script, CTA, description."
            with st.spinner("🎬..."):
                resp, _, _ = call_claude(prompt, 2500)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)

with tab6:
    st.markdown("### Repurpose content")
    rsource = st.text_area("Source content", height=250)
    col1, col2 = st.columns(2)
    rli = col1.checkbox("LinkedIn (3)", value=True)
    rtw = col1.checkbox("Twitter thread", value=True)
    rem = col2.checkbox("Email newsletter", value=True)
    rsh = col2.checkbox("Short video script", value=True)
    
    if st.button("🔄 Repurpose", type="primary", use_container_width=True, key="rp"):
        if rsource:
            outputs = []
            if rli: outputs.append("3 LinkedIn posts")
            if rtw: outputs.append("Twitter thread")
            if rem: outputs.append("Email newsletter")
            if rsh: outputs.append("60-sec video script")
            prompt = f"Repurpose into: {', '.join(outputs)}.\n\n{rsource}"
            with st.spinner("🔄..."):
                resp, _, _ = call_claude(prompt, 4000)
                st.markdown(f'<div class="output-box">{resp}</div>', unsafe_allow_html=True)

st.markdown('<a href="mailto:sharpsuite@sharphuman.com?subject=Feedback" style="position:fixed;bottom:20px;right:20px;background:#6366f1;color:white;padding:12px 20px;border-radius:30px;text-decoration:none;">💬 Feedback</a>', unsafe_allow_html=True)
